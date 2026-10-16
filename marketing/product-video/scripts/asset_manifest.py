#!/usr/bin/env python3
"""Hash explicitly selected render inputs; verify them after transfer. No copying."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def relative_name(value):
    # Use the same manifest safely on POSIX and Windows.
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Input paths must be relative POSIX paths')
    parts = value.split('/')
    if value.startswith('/') or '..' in parts or '' in parts:
        raise ValueError('Input path escapes its root: ' + value)
    return Path(value).as_posix()


def contained(root, name):
    path = root / relative_name(name)
    try:
        path.resolve().relative_to(root)
    except ValueError:
        raise ValueError('Input symlink escapes its root: ' + name)
    return path


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def create(args, root):
    output = args.output.resolve()
    excluded = [relative_name(x).rstrip('/') for group in args.exclude for x in group]
    selected = {}
    case_names = {}
    for group in args.include:
        for name in group:
            entry = contained(root, name)
            if not entry.exists():
                raise ValueError('Declared input does not exist: ' + name)
            candidates = entry.rglob('*') if entry.is_dir() else [entry]
            for path in candidates:
                if not path.is_file() or path.resolve() == output:
                    continue
                rel = path.relative_to(root).as_posix()
                if any(rel == x or rel.startswith(x + '/') for x in excluded):
                    continue
                contained(root, rel)
                previous = case_names.setdefault(rel.casefold(), rel)
                if previous != rel:
                    raise ValueError('Case-insensitive path collision: ' + previous + ' / ' + rel)
                selected[rel] = path
    if not selected:
        raise ValueError('No files selected')
    files = [{'path': rel, 'bytes': path.stat().st_size, 'sha256': digest(path)}
             for rel, path in sorted(selected.items())]
    write_json(output, {'version': 1, 'files': files})
    return {'ok': True, 'files': len(files), 'bytes': sum(f['bytes'] for f in files),
            'manifest': str(output), 'manifestSha256': digest(output)}


def verify(args, root):
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or manifest.get('version') != 1 or not isinstance(manifest.get('files'), list) or not manifest['files']:
        raise ValueError('Expected a nonempty version 1 input manifest')
    issues = []
    seen = set()
    for record in manifest['files']:
        name = relative_name(record['path'])
        if name.casefold() in seen:
            raise ValueError('Duplicate manifest path: ' + name)
        seen.add(name.casefold())
        path = contained(root, name)
        if not path.is_file():
            issues.append({'path': name, 'issue': 'missing'})
        elif path.stat().st_size != record['bytes']:
            issues.append({'path': name, 'issue': 'size mismatch'})
        elif digest(path) != record['sha256']:
            issues.append({'path': name, 'issue': 'hash mismatch'})
    return {'ok': not issues, 'files': len(seen), 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest='mode', required=True)
    make = modes.add_parser('create')
    make.add_argument('--root', type=Path, required=True)
    make.add_argument('--include', action='append', nargs='+', required=True)
    make.add_argument('--exclude', action='append', nargs='+', default=[])
    make.add_argument('--output', type=Path, required=True)
    check = modes.add_parser('verify')
    check.add_argument('--root', type=Path, required=True)
    check.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('Root must be a directory')
        result = create(args, root) if args.mode == 'create' else verify(args, root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
