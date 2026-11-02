// Isolated source-page CDP session. Existing system browser; no editor/npm/browser download.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {spawn} from 'node:child_process';
import {once} from 'node:events';

async function browserPath(){
 if(process.env.VIDEO_BROWSER)return process.env.VIDEO_BROWSER;
 const candidates=process.platform==='darwin'?['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge']:process.platform==='win32'?[path.join(process.env.PROGRAMFILES??'C:/Program Files','Google/Chrome/Application/chrome.exe'),path.join(process.env['PROGRAMFILES(X86)']??'C:/Program Files (x86)','Microsoft/Edge/Application/msedge.exe'),path.join(process.env.LOCALAPPDATA??'C:/Users/Default/AppData/Local','Google/Chrome/Application/chrome.exe')]:['/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'];
 for(const p of candidates)if(await fs.access(p).then(()=>true,()=>false))return p;return null;
}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
export async function openSourcePage(url,width,height,{deviceScale=1,browser}={}){const executable=browser??await browserPath();if(!executable)throw Error('Chrome/Edge not found. Set --browser to an existing Chromium executable.');
 const profile=await fs.mkdtemp(path.join(os.tmpdir(),'mist-source-capture-'));const args=['--headless=new','--disable-gpu-shader-disk-cache','--disk-cache-size=1048576','--media-cache-size=1048576','--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions','--remote-debugging-port=0','--remote-debugging-address=127.0.0.1','--user-data-dir='+profile,'--hide-scrollbars','--mute-audio','--force-color-profile=srgb','--disable-background-timer-throttling','--disable-renderer-backgrounding','--no-first-run','--no-default-browser-check','--window-size='+width+','+height,'about:blank'];
 if(process.platform==='darwin')args.push('--use-angle=metal');if(process.platform==='win32')args.push('--use-angle=d3d11');
 const child=spawn(executable,args,{stdio:['ignore','ignore','pipe']});let diagnostic='';child.stderr.on('data',d=>{diagnostic=(diagnostic+d).slice(-4000)});child.on('error',e=>diagnostic=e.message);
 let socket;const close=async()=>{socket?.close();if(child.exitCode===null&&child.signalCode===null){const exited=once(child,'exit').catch(()=>{});child.kill();await Promise.race([exited,wait(3000)]);}await fs.rm(profile,{recursive:true,force:true}).catch(()=>{})};
 try{let port;for(let n=0;n<150;n++){try{port=(await fs.readFile(path.join(profile,'DevToolsActivePort'),'utf8')).split('\n')[0];break}catch{}if(child.exitCode!==null)break;await wait(100)}if(!port)throw Error('Browser startup failed: '+diagnostic);
 const targets=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();const target=targets.find(x=>x.type==='page');if(!target)throw Error('No isolated capture page');socket=new WebSocket(target.webSocketDebuggerUrl);await Promise.race([once(socket,'open'),wait(10000).then(()=>{throw Error('Browser debugger connection timed out')})]);
 let id=0;const pending=new Map();const errors=[],resourceOrigins=new Set(),failed=[],blocked=[];
 socket.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);clearTimeout(p.timer);m.error?p.reject(Error(m.error.message)):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text+': '+(m.params.exceptionDetails.exception?.description??''))});
 const call=(method,params={})=>new Promise((resolve,reject)=>{const key=++id,timer=setTimeout(()=>{pending.delete(key);reject(Error(method+' timed out'))},60000);pending.set(key,{resolve,reject,timer});socket.send(JSON.stringify({id:key,method,params}))});
 socket.addEventListener('close',()=>{for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('Capture browser closed'))}pending.clear()});
 await call('Page.enable');await call('Runtime.enable');await call('Network.enable');
 socket.addEventListener('message',e=>{const m=JSON.parse(e.data);
 if(m.method==='Network.requestWillBeSent'&&/^https?:/.test(m.params.request.url))resourceOrigins.add(new URL(m.params.request.url).origin);
 if(m.method==='Network.loadingFailed'&&!m.params.canceled)failed.push({error:m.params.errorText});
 if(m.method==='Network.responseReceived'&&m.params.response.status>=400&&!m.params.response.url.endsWith('/favicon.ico'))failed.push({url:m.params.response.url,status:m.params.response.status});
 if(m.method==='Fetch.requestPaused'){
  const {request,requestId}=m.params,deny=!['GET','HEAD'].includes(request.method)||/\.mp4(?:\?|$)/i.test(request.url);
  if(deny)blocked.push({url:request.url,method:request.method});
  call(deny?'Fetch.failRequest':'Fetch.continueRequest',deny?{requestId,errorReason:'BlockedByClient'}:{requestId}).catch(e=>errors.push(e.message));
 }
 });
 await call('Fetch.enable',{patterns:[{urlPattern:'*'}]});
 await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:deviceScale,mobile:false});
 await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
 const navigation=await call('Page.navigate',{url});if(navigation.errorText)throw Error(navigation.errorText);
 const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description??r.exceptionDetails.text);return r.result.value};
 for(let n=0;n<450;n++){if(await evaluate('document.readyState!=="loading" && location.href!=="about:blank"'))break;await wait(100)}
 if(!await evaluate('document.readyState!=="loading" && location.href!=="about:blank"'))throw Error('Source navigation timed out');
 return {call,evaluate,errors,failed,blocked,resourceOrigins,close};
 }catch(e){await close();throw e}
}
