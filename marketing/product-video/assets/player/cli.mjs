#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import http from 'node:http';
import {spawn,execFile} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {promisify} from 'node:util';
import {randomUUID,createHash} from 'node:crypto';
import {once} from 'node:events';
import {transform,parse,init} from './compiler.mjs';
const kit=path.dirname(fileURLToPath(import.meta.url));
const exec=promisify(execFile),json=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const argv=process.argv.slice(2),command=argv.shift()??'help';
const opt=(k,f)=>{const i=argv.indexOf('--'+k);return i<0?f:argv[i+1]??f};
const exists=p=>fs.access(p).then(()=>true,()=>false);
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function inside(root,p){const rel=path.relative(root,p);return rel!==''&&!rel.startsWith('..'+path.sep)&&rel!=='..'&&!path.isAbsolute(rel)}
function relative(s){if(typeof s!=='string'||!s||s.includes('\\')||s.split('/').some(x=>x==='..'||x==='.')||path.isAbsolute(s))throw Error('Expected a safe relative path: '+s);return s}
async function regularTree(dir){const out=[];for(const e of await fs.readdir(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isSymbolicLink())throw Error('Symlinks are not portable: '+p);if(e.isDirectory())out.push(...await regularTree(p));else if(e.isFile())out.push(p);}return out}
async function copyTree(a,b){for(const f of await regularTree(a)){const dst=path.join(b,path.relative(a,f));await fs.mkdir(path.dirname(dst),{recursive:true});if(process.platform==='darwin'&&(await fs.stat(f)).size>1024*1024){try{await exec('/bin/cp',['-c',f,dst]);continue}catch{}}await fs.copyFile(f,dst,fs.constants.COPYFILE_FICLONE)}}
function number(s,min,max,label){const n=Number(s);if(!Number.isFinite(n)||n<min||n>max)throw Error('Invalid '+label);return n}
export async function projectDestination(projectRoot,name){
 const root=await fs.realpath(projectRoot),target=path.resolve(root,name);let parent=target;const tail=[];
 while(!await exists(parent)){tail.unshift(path.basename(parent));const next=path.dirname(parent);if(next===parent)throw Error('Invalid output path');parent=next}
 const canonical=path.join(await fs.realpath(parent),...tail);
 if(!inside(root,canonical))throw Error('Output escapes project through an existing directory or symlink');return canonical;
}
export async function build(projectRoot=process.cwd(),sourceName='video',outName='video-player'){
 const project=await fs.realpath(projectRoot),source=await fs.realpath(path.resolve(project,sourceName)),finalOut=await projectDestination(project,outName);let out=finalOut;
 if(!inside(project,source)||!inside(project,out)||inside(source,out)||inside(out,source)||source===out)throw Error('Source and output must be separate project subdirectories');
 if(await exists(path.join(project,'.mist-desktop/video-player-jobs/active.lock')))throw Error('A player export owns this build; wait for it or cancel the returned job before rebuilding');
 let marker=path.join(out,'.video-player-owned.json');
 if(await exists(out)){if(!await exists(marker)|| (await json(marker)).source!==source)throw Error('Output is not owned by this builder; choose an empty new directory');}
 await regularTree(source); // reject symlinks before following imports or copying media
 const p=await json(path.join(source,'project.json'));
 p.width=number(p.width,64,7680,'width');p.height=number(p.height,64,4320,'height');p.fps=number(p.fps,1,120,'fps');if(![p.width,p.height,p.fps].every(Number.isInteger))throw Error('Canvas dimensions and FPS must be integers');
 if(!Array.isArray(p.scenes)||!p.scenes.length||p.scenes.length>100)throw Error('Expected 1–100 scenes');
 const ids=new Set();let start=0;
 const scenes=p.scenes.map((s,index)=>{if(!/^[a-z0-9][a-z0-9-]{0,63}$/.test(s.id)||ids.has(s.id))throw Error('Invalid/duplicate scene ID');ids.add(s.id);const duration=number(s.duration,.01,600,'scene duration');const v={...s,duration,index,start};start+=duration;return v});
 for(const file of p.requiredAssets??[]){relative(file);if(!await exists(path.join(source,file)))throw Error('Missing required asset: '+file)}
 await fs.mkdir(path.dirname(finalOut),{recursive:true});out=await fs.mkdtemp(finalOut+'.build-');marker=path.join(out,'.video-player-owned.json');
 try{await fs.writeFile(marker,JSON.stringify({source,version:1}));
 const manifest={...p,scenes,duration:start,renderer:'three',runtimeVersion:'0.1.0',soundFiles:{}};
 for(const dir of ['assets','music','sounds'])if(await exists(path.join(source,dir)))await copyTree(path.join(source,dir),path.join(out,dir));
 if(await exists(path.join(source,'music-analysis.json')))manifest.musicAnalysis=await json(path.join(source,'music-analysis.json'));
 if(await exists(path.join(source,'sounds')))for(const f of await regularTree(path.join(source,'sounds'))){if(/\.(wav|mp3|ogg|m4a|flac)$/i.test(f)){const name=path.parse(f).name;if(manifest.soundFiles[name])throw Error('Ambiguous sound name: '+name);manifest.soundFiles[name]='sounds/'+path.relative(path.join(source,'sounds'),f).split(path.sep).join('/')}}
 if(p.music?.file&&!await exists(path.join(source,'music',relative(p.music.file))))throw Error('Missing music file');
 if(typeof init==='function')await init();else await init;
 const emitted=new Map();
 async function resolve(from,name){const base=path.resolve(path.dirname(from),name);if(!inside(source,base))throw Error('Import escapes video source: '+name);
  for(const c of [base,...['.ts','.tsx','.js','.mjs','.json'].map(x=>base+x),...['index.ts','index.tsx','index.js'].map(x=>path.join(base,x))])if(await fs.stat(c).then(x=>x.isFile(),()=>false))return c;
  throw Error('Missing import '+name+' in '+path.relative(source,from));}
 async function compile(file){if(emitted.has(file))return emitted.get(file);const rel=path.relative(source,file).split(path.sep).join('/'),dest='modules/'+rel+'.js';emitted.set(file,dest);
  let code;if(file.endsWith('.json'))code='export default '+JSON.stringify(await json(file))+';';else{code=await fs.readFile(file,'utf8');if(/\.tsx?$/.test(file))code=transform(code,{transforms:['typescript','jsx'],jsxRuntime:'automatic',production:true,filePath:rel}).code;
   const [imports]=parse(code);const changes=[];
   for(const im of imports){if(im.type==='import.meta'||im.type==='import-meta'||im.type==='meta'||im.d===-2)continue;const name=im.specifier??im.n;if(!name)throw Error('Computed module imports are not supported: '+rel);const a=im.start??im.s,b=im.end??im.e;
    if(name.startsWith('.')){const next=await compile(await resolve(file,name));let target=path.posix.relative(path.posix.dirname(dest),next);if(!target.startsWith('.'))target='./'+target;const original=code.slice(a,b);changes.push([a,b,/^["']/.test(original)?JSON.stringify(target):target]);}
    else if(!['storyboard','react','react/jsx-runtime','react-dom','react-dom/client'].includes(name))throw Error('Unbundled dependency '+name+'; include its permitted files in video/components');}
   for(const [a,b,value] of changes.sort((a,b)=>b[0]-a[0]))code=code.slice(0,a)+value+code.slice(b);
  }
  await fs.mkdir(path.dirname(path.join(out,dest)),{recursive:true});await fs.writeFile(path.join(out,dest),code);return dest;
 }
 for(const s of scenes)s.module='./'+await compile(path.join(source,'scenes',s.id+'.tsx'));
 await copyTree(path.join(kit,'runtime'),path.join(out,'runtime'));await copyTree(path.join(kit,'licenses'),path.join(out,'licenses'));
 for(const f of ['index.html','frame.html','viewer.mjs','frame.mjs'])await fs.copyFile(path.join(kit,f),path.join(out,f));
 await fs.writeFile(path.join(out,'project.json'),JSON.stringify(manifest,null,2));
 const ledger=[];for(const f of await regularTree(out)){if(f===marker||path.basename(f)==='build-receipt.json')continue;ledger.push({file:path.relative(out,f).split(path.sep).join('/'),sha256:createHash('sha256').update(await fs.readFile(f)).digest('hex')})}
 await fs.writeFile(path.join(out,'build-receipt.json'),JSON.stringify({version:1,source,path:finalOut,files:ledger,duration:start,builtAt:new Date().toISOString()},null,2));
 const previous=finalOut+'.previous-'+randomUUID();if(await exists(finalOut))await fs.rename(finalOut,previous);
 try{await fs.rename(out,finalOut)}catch(e){if(await exists(previous))await fs.rename(previous,finalOut);throw e}
 if(await exists(previous))await fs.rm(previous,{recursive:true,force:true});
 return {out:finalOut,duration:start,scenes:scenes.length,modules:emitted.size,renderer:'three',storyboardServerRequired:false};
 }catch(e){await fs.rm(out,{recursive:true,force:true});throw e}
}
const mime={'.html':'text/html','.mjs':'text/javascript','.js':'text/javascript','.json':'application/json','.css':'text/css','.woff2':'font/woff2','.woff':'font/woff','.glb':'model/gltf-binary','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.wav':'audio/wav','.mp4':'video/mp4','.webp':'image/webp','.gif':'image/gif','.jpeg':'image/jpeg','.avif':'image/avif','.mp3':'audio/mpeg','.ogg':'audio/ogg','.m4a':'audio/mp4','.flac':'audio/flac','.ttf':'font/ttf'};
export async function serve(root,port=0){root=await fs.realpath(root);const server=http.createServer(async(req,res)=>{try{
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return}
  const host=req.headers.host??'';if(!/^(127\.0\.0\.1|localhost):\d+$/.test(host)){res.writeHead(403).end();return}
  let name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);if(name==='/')name='/index.html';const p=path.resolve(root,'.'+name);
  if(!inside(root,p)||!inside(root,await fs.realpath(p))){res.writeHead(403).end();return}
  const bytes=await fs.readFile(p);res.writeHead(200,{'Content-Type':mime[path.extname(p)]??'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(req.method==='HEAD'?undefined:bytes);
 }catch{res.writeHead(404).end('Not found')}});await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',resolve)});return {server,url:'http://127.0.0.1:'+server.address().port}}
export async function browserPath(){const custom=opt('browser',process.env.VIDEO_BROWSER);if(custom){if(!await exists(custom))throw Error('Configured browser missing');return custom}
 const candidates=process.platform==='darwin'?['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']:process.platform==='win32'?[path.join(process.env.PROGRAMFILES??'C:/Program Files','Google/Chrome/Application/chrome.exe'),path.join(process.env['PROGRAMFILES(X86)']??'C:/Program Files (x86)','Microsoft/Edge/Application/msedge.exe')]:['/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'];
 for(const p of candidates)if(await exists(p))return p;return null;
}
export async function openCapture(url,width,height){const executable=await browserPath();if(!executable)throw Error('Chrome/Edge not found. Set --browser to an existing Chromium executable.');
 const profile=await fs.mkdtemp(path.join(os.tmpdir(),'mist-video-player-'));const args=['--headless=new','--disable-gpu-shader-disk-cache','--disk-cache-size=1048576','--media-cache-size=1048576','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--remote-debugging-port=0','--remote-debugging-address=127.0.0.1','--user-data-dir='+profile,'--hide-scrollbars','--mute-audio','--force-color-profile=srgb','--disable-background-timer-throttling','--disable-renderer-backgrounding','--no-first-run','--no-default-browser-check','--window-size='+width+','+height,'about:blank'];
 if(process.platform==='darwin')args.push('--use-angle=metal');if(process.platform==='win32')args.push('--use-angle=d3d11');
 const child=spawn(executable,args,{stdio:['ignore','ignore','pipe']});let diagnostic='';child.stderr.on('data',d=>{diagnostic=(diagnostic+d).slice(-4000)});child.on('error',e=>diagnostic=e.message);
 let socket;const close=async()=>{socket?.close();if(child.exitCode===null&&child.signalCode===null){const exited=once(child,'exit').catch(()=>{});child.kill();await Promise.race([exited,wait(3000)]);}await fs.rm(profile,{recursive:true,force:true}).catch(()=>{})};
 try{let port;for(let n=0;n<150;n++){try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{}if(child.exitCode!==null)break;await wait(100)}if(!port)throw Error('Browser startup failed: '+diagnostic);
 const targets=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();const target=targets.find(x=>x.type==='page');if(!target)throw Error('No isolated capture page');socket=new WebSocket(target.webSocketDebuggerUrl);await Promise.race([once(socket,'open'),wait(10000).then(()=>{throw Error('Browser debugger connection timed out')})]);
 let id=0;const pending=new Map();const errors=[],resourceOrigins=new Set();
 socket.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(m.error.message)):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text+': '+(m.params.exceptionDetails.exception?.description??''))});
 const call=(method,params={})=>new Promise((resolve,reject)=>{const key=++id,timer=setTimeout(()=>{pending.delete(key);reject(Error(method+' timed out'))},60000);pending.set(key,{resolve,reject,timer});socket.send(JSON.stringify({id:key,method,params}))});
 socket.addEventListener('close',()=>{for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('Capture browser closed'))}pending.clear()});
 await call('Page.enable');await call('Runtime.enable');await call('Network.enable');
 socket.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Network.requestWillBeSent'&&/^https?:/.test(m.params.request.url)){const origin=new URL(m.params.request.url).origin;resourceOrigins.add(origin);if(origin!==new URL(url).origin)errors.push('Scene requested a resource outside this player: '+m.params.request.url)}if(m.method==='Network.loadingFailed'&&!m.params.canceled)errors.push('Resource load failed: '+m.params.errorText);if(m.method==='Network.responseReceived'&&m.params.response.status>=400&&!m.params.response.url.endsWith('/favicon.ico'))errors.push('Resource '+m.params.response.status+': '+m.params.response.url)});await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});await call('Page.navigate',{url});
 const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description??r.exceptionDetails.text);return r.result.value};
 for(let n=0;n<300;n++){if(errors.length)throw Error(errors.join('\n'));if(await evaluate('Boolean(window.__sb)'))break;await wait(100)}if(errors.length)throw Error(errors.join('\n'));if(!await evaluate('Boolean(window.__sb)'))throw Error('Player initialization timed out');await evaluate('window.__sb.ready.then(()=>true)');
 return {call,evaluate,errors,resourceOrigins,close};
 }catch(e){await close();throw e}
}
export async function captureFrames(root,times,destination){const p=await json(path.join(root,'project.json')),s=await serve(root);let c;try{c=await openCapture(s.url+'/frame.html?capture=1',p.width,p.height);const files=[];for(const t of times){number(t,0,p.duration,'frame time');const result=await c.evaluate('window.__sb.seek('+t+')');if(result.errors.length)throw Error(result.errors.join('\n'));const shot=await c.call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});const file=path.join(destination,'frame-'+String(t).replace('.','_')+'.png');await fs.writeFile(file,Buffer.from(shot.data,'base64'));files.push(file)}if(c.errors.length)throw Error(c.errors.join('\n'));return files}finally{await c?.close();await new Promise(r=>(s.server.closeAllConnections(),s.server.close(r)))}}
async function main(){const project=path.resolve(opt('project',process.cwd())),source=opt('source','video'),out=path.resolve(project,opt('out','video-player'));
 if(command==='materialize'){
  const dest=await projectDestination(project,opt('dest','tools/video-player'));
  if(await exists(dest))throw Error('Keep the existing kit; choose a new destination for an upgrade');
  await fs.mkdir(dest,{recursive:true});
  for(const dir of ['runtime','licenses'])await copyTree(path.join(kit,dir),path.join(dest,dir));
  for(const file of ['cli.mjs','compiler.mjs','export.mjs','index.html','frame.html','viewer.mjs','frame.mjs','package.json','provenance.json','package-fragment.json'])await fs.copyFile(path.join(kit,file),path.join(dest,file));
  console.log(JSON.stringify({kit:dest,installRequired:false,storyboardServerRequired:false}));return;
 }
 if(command==='build'){console.log(JSON.stringify(await build(project,source,opt('out','video-player')),null,2));return}
 if(command==='preview'){const p=await json(path.join(out,'project.json'));const s=await serve(out,Number(opt('port',0)));console.log(JSON.stringify({url:s.url,duration:p.duration,stop:'Ctrl+C'}));for(const sig of ['SIGINT','SIGTERM'])process.once(sig,()=>s.server.close(()=>process.exit(0)));return}
 if(command==='doctor'){const browser=await browserPath(),ffmpeg=opt('ffmpeg',process.env.VIDEO_FFMPEG??'ffmpeg');let encoder=false;try{await exec(ffmpeg,['-version']);encoder=true}catch{}let probe=false;try{await exec(opt('ffprobe',process.env.VIDEO_FFPROBE??'ffprobe'),['-version']);probe=true}catch{}console.log(JSON.stringify({node:process.version,browser,ffmpeg:encoder?ffmpeg:null,previewReady:true,exportReady:!!browser&&encoder&&probe,storyboardServerRequired:false},null,2));return}
 if(command==='frames'){const dest=path.resolve(project,opt('dest','player-checks'));await fs.mkdir(dest,{recursive:true});const times=String(opt('times','0')).split(',').map(Number);if(times.length>4)throw Error('Capture at most four frames per call');console.log(JSON.stringify({files:await captureFrames(out,times,dest)},null,2));return}
 if(['export','worker','status','cancel'].includes(command)){const {runExport}=await import('./export.mjs');await runExport({command,argv,project,out,opt,serve,openCapture,exec,kit,projectDestination});return}
 console.log('node cli.mjs materialize|build|preview|doctor|frames|export|status|cancel --project <project> --source video --out video-player');
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))main().catch(e=>{console.error(JSON.stringify({ok:false,error:e.message}));process.exitCode=1});
