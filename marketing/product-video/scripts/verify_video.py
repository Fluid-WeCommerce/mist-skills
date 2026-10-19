#!/usr/bin/env python3
"""Verify an encoded movie's explicit format expectations and optional full decode."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--width', type=int)
    parser.add_argument('--height', type=int)
    parser.add_argument('--fps', help='For example 30 or 30000/1001')
    parser.add_argument('--duration', type=float, help='Expected seconds; tolerance is at least one frame')
    parser.add_argument('--frames', type=int)
    parser.add_argument('--require-audio', action='store_true')
    parser.add_argument('--decode', action='store_true', help='Fully decode video/audio with FFmpeg')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = {'ok': False, 'issues': [], 'fullDecodePassed': None}
    try:
        path = args.video.resolve(strict=True)
        ffprobe = shutil.which('ffprobe')
        if not ffprobe:
            raise ValueError('ffprobe is required; no software was installed')
        probe = subprocess.run([ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                               capture_output=True, text=True, timeout=60)
        if probe.returncode:
            raise ValueError('ffprobe failed: ' + probe.stderr.strip()[:2000])
        metadata = json.loads(probe.stdout)
        videos = [s for s in metadata['streams'] if s['codec_type'] == 'video']
        audio = [s for s in metadata['streams'] if s['codec_type'] == 'audio']
        if not videos:
            raise ValueError('No video stream')
        video = videos[0]
        rate = Fraction(video.get('avg_frame_rate', video.get('r_frame_rate', '0')))
        if rate <= 0:
            raise ValueError('Video has no usable frame rate')
        seconds = float(metadata['format']['duration'])
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError('Video has no usable duration')
        frames = int(video['nb_frames']) if video.get('nb_frames', '').isdigit() else None
        result.update({'video': str(path), 'sha256': digest(path), 'bytes': path.stat().st_size,
                       'durationSeconds': seconds, 'width': video['width'], 'height': video['height'],
                       'fps': str(rate), 'frames': frames, 'videoCodec': video.get('codec_name'),
                       'audio': [{'codec': s.get('codec_name'), 'channels': s.get('channels'),
                                  'sampleRate': s.get('sample_rate'), 'duration': s.get('duration')} for s in audio]})
        for field in ['width', 'height', 'frames']:
            expected = getattr(args, field)
            if expected is not None and result[field] != expected:
                result['issues'].append(f'{field}: expected {expected}, observed {result[field]}')
        if args.fps and not math.isclose(float(rate), float(Fraction(args.fps)), rel_tol=0.00001):
            result['issues'].append(f'fps: expected {args.fps}, observed {rate}')
        tolerance = max(.05, 1 / float(rate) + .01)
        if args.duration is not None and abs(seconds - args.duration) > tolerance:
            result['issues'].append(f'duration: expected {args.duration}, observed {seconds}')
        if args.require_audio and not audio:
            result['issues'].append('Required audio stream is missing')
        if args.require_audio:
            for stream in audio:
                if not stream.get('channels', 0):
                    result['issues'].append('Audio stream has no usable channels')
                if stream.get('duration') and abs(float(stream['duration']) - seconds) > tolerance:
                    result['issues'].append('Audio/video durations differ beyond one-frame tolerance')
        if args.decode:
            ffmpeg = shutil.which('ffmpeg')
            if not ffmpeg:
                raise ValueError('ffmpeg is required for --decode; no software was installed')
            decoded = subprocess.run([ffmpeg, '-nostdin', '-hide_banner', '-v', 'error', '-xerror',
                                      '-i', str(path), '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-'],
                                     capture_output=True, text=True, timeout=max(120, seconds * 4 + 30))
            result['fullDecodePassed'] = decoded.returncode == 0
            if decoded.returncode:
                result['issues'].append('Full decode failed: ' + decoded.stderr.strip()[:2000])
        result['ok'] = not result['issues']
    except (OSError, ValueError, KeyError, ZeroDivisionError, subprocess.TimeoutExpired) as error:
        result['issues'].append(str(error))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
