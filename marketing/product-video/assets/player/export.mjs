import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {randomUUID,createHash} from 'node:crypto';
import {once} from 'node:events';
const json=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function verifyBuild(out,expected){
 const bytes=await fs.readFile(path.join(out,'build-receipt.json')),hash=createHash('sha256').update(bytes).digest('hex');
 if(expected&&hash!==expected)throw Error('Player build changed during export; rebuild and retry');
 for(const entry of JSON.parse(bytes).files){const actual=createHash('sha256').update(await fs.readFile(path.join(out,entry.file))).digest('hex');if(actual!==entry.sha256)throw Error('Built file changed or corrupted: '+entry.file)}return hash;
}
async function save(file,state){const temp=file+'.tmp';await fs.writeFile(temp,JSON.stringify(state,null,2));await fs.rename(temp,file)}
export async function runExport({command,project,out,opt,serve,openCapture,exec,kit,projectDestination}){
 project=await fs.realpath(project);const jobs=await projectDestination(project,'.mist-desktop/video-player-jobs');await fs.mkdir(jobs,{recursive:true});
 if(['status','cancel'].includes(command)){const id=opt('job','');if(!/^[a-f0-9-]{36}$/.test(id))throw Error('Use the actual returned job ID');const file=path.join(jobs,id,'status.json');const state=await json(file);if(command==='cancel'&&['queued','rendering','encoding'].includes(state.status)){await fs.writeFile(path.join(jobs,id,'cancel'),'cancel');console.log(JSON.stringify({id,cancellationRequested:true}));return}console.log(JSON.stringify(state,null,2));return}
 if(command==='export'){
  const p=await json(path.join(out,'project.json')),fps=Number(opt('fps',p.fps)),from=Number(opt('from',0)),to=Number(opt('to',p.duration));
  if(!Number.isInteger(fps)||fps<1||fps>60||!Number.isFinite(from)||!Number.isFinite(to)||from<0||to<=from||to>p.duration)throw Error('Invalid export range/fps');
  const buildHash=await verifyBuild(out);const config={buildHash,id:randomUUID(),out,project,fps,from,to,ffmpeg:opt('ffmpeg',process.env.VIDEO_FFMPEG??'ffmpeg'),ffprobe:opt('ffprobe',process.env.VIDEO_FFPROBE??'ffprobe'),browser:opt('browser',process.env.VIDEO_BROWSER),width:p.width,height:p.height};
  if(p.width%2||p.height%2)throw Error('MP4 export needs even width/height');
  await exec(config.ffmpeg,['-version']);await exec(config.ffprobe,['-version']);
  const lock=path.join(jobs,'active.lock');await fs.mkdir(lock).catch(()=>{throw Error('A player render is active. Check its status before another export; preserve interrupted jobs.')});
  const dir=path.join(jobs,config.id);try{await fs.mkdir(dir);await fs.writeFile(path.join(dir,'config.json'),JSON.stringify(config));await save(path.join(dir,'status.json'),{id:config.id,status:'queued',framesDone:0,framesTotal:Math.ceil((to-from)*fps-1e-7),fullFilm:from===0&&to===p.duration});
   await fs.writeFile(path.join(lock,'job'),config.id);
   const args=[path.join(kit,'cli.mjs'),'worker','--config',path.join(dir,'config.json')];if(config.browser)args.push('--browser',config.browser);
   const log=await fs.open(path.join(dir,'worker.log'),'a');const child=spawn(process.execPath,args,{cwd:project,detached:true,stdio:['ignore',log.fd,log.fd]});await once(child,'spawn');child.unref();await log.close();console.log(JSON.stringify({jobId:config.id,status:'queued',statusCommand:'node <player-kit>/cli.mjs status --project '+project+' --job '+config.id},null,2));
  }catch(e){await fs.rm(lock,{recursive:true,force:true});throw e}return;
 }
 const config=await json(opt('config','')),dir=path.join(jobs,config.id),statusFile=path.join(dir,'status.json'),cancel=path.join(dir,'cancel');let s,c,encoder,cancelWatch,deliveredOutput;let state=await json(statusFile),stderr='';
 const update=async x=>{Object.assign(state,x,{updatedAt:new Date().toISOString()});await save(statusFile,state)};
 const cancelled=()=>fs.access(cancel).then(()=>true,()=>false);const abort=new AbortController();const checkCancel=async()=>{if(await cancelled())throw Error('Cancelled')};
 try{
  await checkCancel();await verifyBuild(config.out,config.buildHash);cancelWatch=setInterval(()=>{cancelled().then(yes=>{if(yes){encoder?.kill();abort.abort()}}).catch(()=>{})},250);cancelWatch.unref();
  const p=await json(path.join(config.out,'project.json'));const total=Math.ceil((config.to-config.from)*config.fps-1e-7);await update({status:'rendering'});
  s=await serve(config.out);c=await openCapture(s.url+'/frame.html?capture=1',config.width,config.height);
  await checkCancel();const audio=await c.evaluate('window.__sb.audio('+config.from+','+config.to+')');await checkCancel();const wav=path.join(dir,'audio.wav');await fs.writeFile(wav,Buffer.from(audio.base64,'base64'));
  const movie=path.join(dir,'video.partial.mp4'),args=['-v','error','-nostdin','-f','image2pipe','-vcodec','png','-framerate',String(config.fps),'-i','pipe:0','-i',wav,'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',String(total/config.fps),'-movflags','+faststart',movie];
  encoder=spawn(config.ffmpeg,args,{stdio:['pipe','ignore','pipe']});encoder.stderr.on('data',b=>stderr=(stderr+b).slice(-5000));const finished=once(encoder,'close');finished.catch(()=>{});let streamError;encoder.stdin.on('error',e=>streamError=e);
  for(let i=0;i<total;i++){if(await cancelled())throw Error('Cancelled');const t=Math.min(config.to,config.from+i/config.fps);const r=await c.evaluate('window.__sb.seek('+t+')');if(r.errors.length)throw Error(r.errors.join('\n'));if(c.errors.length)throw Error(c.errors.join('\n'));const png=await c.call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});if(streamError)throw streamError;if(!encoder.stdin.write(Buffer.from(png.data,'base64')))await once(encoder.stdin,'drain');if(i%5===0||i===total-1)await update({framesDone:i+1})}
  encoder.stdin.end();await update({status:'encoding'});const [code]=await finished;await checkCancel();if(code!==0)throw Error('Encoder failed: '+stderr);
  const probe=JSON.parse((await exec(config.ffprobe,['-v','error','-count_frames','-show_streams','-show_format','-of','json',movie],{signal:abort.signal})).stdout),v=probe.streams.find(s=>s.codec_type==='video'),a=probe.streams.find(s=>s.codec_type==='audio');
  const rate=v?.avg_frame_rate?.split('/').map(Number),actualFps=rate?.[1]?rate[0]/rate[1]:NaN;
  if(Math.abs(actualFps-config.fps)>.001||!v||v.width!==config.width||v.height!==config.height||Number(v.nb_read_frames)!==total||!a||Math.abs(Number(probe.format.duration)-total/config.fps)>.15)throw Error('Encoded output failed dimensions/frame-count/duration/audio checks');
  await exec(config.ffmpeg,['-v','error','-i',movie,'-f','null','-'],{maxBuffer:1024*1024,timeout:120000,signal:abort.signal});
  await checkCancel();await verifyBuild(config.out,config.buildHash);await checkCancel();const dest=await projectDestination(config.project,'exports');await fs.mkdir(dest,{recursive:true});const output=path.join(dest,'video-'+config.id+'.mp4');await fs.copyFile(movie,output,fs.constants.COPYFILE_EXCL);deliveredOutput=output;await checkCancel();const hash=createHash('sha256').update(await fs.readFile(output)).digest('hex');await checkCancel();await update({status:'done',output,sha256:hash,framesDone:total,verified:{width:v.width,height:v.height,frames:total,fps:actualFps,duration:Number(probe.format.duration),audio:true,fullDecode:true},audioMasterGain:audio.masterGain});
 }catch(e){encoder?.kill();await c?.close();c=null;if(deliveredOutput)await fs.unlink(deliveredOutput).catch(()=>{});await update({status:await cancelled()?'cancelled':'failed',error:e.message,encoder:stderr})}
 finally{clearInterval(cancelWatch);await c?.close();if(s)await new Promise(r=>(s.server.closeAllConnections(),s.server.close(r)));const lock=path.join(jobs,'active.lock');if(await fs.readFile(path.join(lock,'job'),'utf8').catch(()=>null)===config.id)await fs.rm(lock,{recursive:true,force:true})}
}
