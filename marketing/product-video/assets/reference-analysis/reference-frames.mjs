import fs from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';

// Local reference inspection only. Extracts a bounded set of stills, not a new video or editable scene recovery.
const args=process.argv.slice(2);
const arg=(key,fallback)=>{const i=args.indexOf(key);if(i<0)return fallback;if(!args[i+1])throw new Error(`Missing ${key}`);return args[i+1];};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const hash=async p=>{const h=createHash('sha256');for await(const chunk of createReadStream(p))h.update(chunk);return h.digest('hex');};
try{
  const input=arg('--input'),output=arg('--output'),requested=arg('--times');
  if(!input||!output||!requested)throw new Error('Usage: node reference-frames.mjs --input film.mp4 --times 0,1,2 --output new-review-folder [--width 640] [--source https://reference-post]');
  const file=await fs.realpath(input),dir=path.resolve(output),width=Number(arg('--width','640'));
  if(!Number.isInteger(width)||width<320||width>1280)throw new Error('Review width must be320–1280px');
  const times=requested.split(',').map(Number);
  if(!times.length||times.length>12||times.some(t=>!Number.isFinite(t)||t<0))throw new Error('Choose1–12 finite, nonnegative sample times');
  if((await fs.readdir(dir).catch(e=>e.code==='ENOENT'?[]:Promise.reject(e))).length)throw new Error('Output folder is not empty; choose a fresh review folder');
  const ffmpeg=arg('--ffmpeg','ffmpeg'),ffprobe=arg('--ffprobe','ffprobe');
  const probe=JSON.parse(execFileSync(ffprobe,['-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate','-of','json',file],{encoding:'utf8',timeout:10000,maxBuffer:256*1024}));
  const stream=probe.streams.find(s=>s.codec_type==='video'),duration=Number(probe.format?.duration);
  if(!stream||!Number.isFinite(duration)||duration<=0||times.some(t=>t>=duration))throw new Error('Samples must be inside a valid video duration');
  await fs.mkdir(dir,{recursive:true});
  const deadline=Date.now()+60000,frames=[];
  for(let i=0;i<times.length;i++){
    const name=`frame-${String(i+1).padStart(2,'0')}.png`,out=path.join(dir,name);
    const timeout=Math.min(15000,deadline-Date.now());if(timeout<1)throw new Error('Reference inspection reached its60-second budget');
    execFileSync(ffmpeg,['-hide_banner','-loglevel','error','-ss',String(times[i]),'-i',file,'-an','-sn','-vf',`scale=${width}:-2`,'-frames:v','1','-update','1',out],{timeout,maxBuffer:256*1024});
    frames.push({requestedTime:times[i],file:name,sha256:await hash(out)});
  }
  const report={version:1,input:{file:path.basename(file),sha256:await hash(file),duration,width:stream.width,height:stream.height,averageFps:stream.avg_frame_rate},source:arg('--source',null),samples:frames,limits:'Decoded stills at requested seek times. These do not recover hidden layers, original camera/easing, source code, exact variable-frame PTS, audio comfort or permission to reuse media.'};
  await fs.writeFile(path.join(dir,'reference.json'),JSON.stringify(report,null,2)+'\n');
  const cards=frames.map(f=>`<figure><img src="${f.file}" alt="Reference at${f.requestedTime.toFixed(3)} seconds"><figcaption>${f.requestedTime.toFixed(3)}s</figcaption></figure>`).join('');
  await fs.writeFile(path.join(dir,'index.html'),`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Reference frames</title><style>body{margin:24px;background:#f6f6f6;font:16px system-ui;color:#222}h1{font-size:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}figure{margin:0}img{width:100%;display:block;background:#ddd}figcaption{padding:8px;font-variant-numeric:tabular-nums}p{max-width:85ch;color:#555}</style><h1>${esc(path.basename(file))}</h1><p>${duration.toFixed(3)}s · ${stream.width}×${stream.height} · requested sample times. Inspect movement around these poses before inferring timing or mechanism.</p><main>${cards}</main>`);
  const cols=Math.min(3,frames.length),rows=Math.ceil(frames.length/cols),sheet=path.join(dir,'contact-sheet.jpg');
  execFileSync(ffmpeg,['-hide_banner','-loglevel','error','-framerate','1','-i',path.join(dir,'frame-%02d.png'),'-vf',`tile=${cols}x${rows}:padding=8:margin=8:color=white`,'-frames:v','1',sheet],{timeout:10000,maxBuffer:256*1024});
  console.log(JSON.stringify({ok:true,samples:frames.length,duration,report:path.join(dir,'reference.json'),gallery:path.join(dir,'index.html'),contactSheet:sheet}));
}catch(e){console.error(JSON.stringify({ok:false,error:e.message}));process.exitCode=1;}
