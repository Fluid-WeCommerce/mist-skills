/** Freeze a read-only public landing page into exact-position, independently liftable layers.
 * Uses an explicitly configured installed Storyboard runtime (Playwright + pngjs).
 * No package installation, login, form submission, publication, or renderer mutation.
 * Usage: node capture-layers.mjs /absolute/path/capture-config.json
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

export async function captureLayers(config) {
 const {runtimeDir,chromiumExecutable,sourceUrl,outputDir,pieces:selections,heroSelector,sectionSelector='main section[data-fluid-section]',freezeHeader,freezeStyles=''}=config;
 if(!path.isAbsolute(runtimeDir)||!path.isAbsolute(outputDir))throw new Error('runtimeDir and outputDir must be explicit absolute paths');
 const parsed=new URL(sourceUrl);if(!['https:','http:'].includes(parsed.protocol)||parsed.username||parsed.password)throw new Error('Expected public HTTP(S) source URL without credentials');
 const width=config.width??1440,viewportHeight=config.viewportHeight??900,deviceScale=config.deviceScale??2,pad=config.texturePadding??28;
 if(!Number.isInteger(width)||width<320||width>3840||!Number.isInteger(viewportHeight)||viewportHeight<320||viewportHeight>2160||![1,2].includes(deviceScale))throw new Error('Unsupported capture dimensions');
 if(!Array.isArray(selections)||selections.length<1||selections.length>24||new Set(selections.map(p=>p.id)).size!==selections.length||selections.some(p=>!/^[-a-z0-9]+$/.test(p.id)||!p.selector||!['photo','card','chip','bottle','testimonial'].includes(p.kind)))throw new Error('Expected unique safe IDs, selectors and known layer kinds');
 process.env.PLAYWRIGHT_BROWSERS_PATH=path.join(runtimeDir,'.storyboard/browsers');
 const {chromium}=await import(pathToFileURL(path.join(runtimeDir,'node_modules/playwright/index.mjs')).href);
 const {PNG}=await import(pathToFileURL(path.join(runtimeDir,'node_modules/pngjs/lib/png.js')).href);
 await fs.mkdir(outputDir,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:chromiumExecutable,args:['--force-color-profile=srgb','--disable-lcd-text','--hide-scrollbars','--mute-audio']});
 let geometry;
 const errors=[],failed=[];
 try {
  const context=await browser.newContext({viewport:{width,height:viewportHeight},deviceScaleFactor:deviceScale,reducedMotion:'reduce'});
  const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>{if(!/\.mp4(?:\?|$)/.test(r.url()))failed.push({url:r.url(),error:r.failure()?.errorText});});
  await page.route('**/*',route=>/\.mp4(?:\?|$)/.test(route.request().url())?route.abort():route.continue());
  await page.goto(sourceUrl,{waitUntil:'domcontentloaded',timeout:45000});
  await page.waitForSelector(heroSelector,{state:'visible',timeout:15000});
  await page.evaluate(()=>{
   for(const v of [...document.querySelectorAll('video')]){const img=document.createElement('img');img.src=v.poster;img.alt=v.getAttribute('aria-label')||'';img.className=v.className;img.style.cssText=v.style.cssText;img.dataset.frozenVideo='poster';if(v.poster){v.pause();v.replaceWith(img);}else{v.pause();v.removeAttribute('autoplay');}}
   for(const im of document.images){im.loading='eager';im.decoding='sync';}
  });
  await page.addStyleTag({content:'html{scroll-behavior:auto!important}*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}'+freezeStyles});
  await page.evaluate(async()=>{await document.fonts.ready;for(let y=0;y<document.documentElement.scrollHeight;y+=720){window.scrollTo(0,y);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}await Promise.all([...document.images].map(im=>im.decode().catch(()=>{})));window.scrollTo(0,0);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
  if(freezeHeader)await page.evaluate(({selector,cssVariables={},position='absolute'})=>{const el=document.querySelector(selector);if(!el)throw new Error('Missing configured source header');for(const [k,v]of Object.entries(cssVariables))el.style.setProperty(k,String(v));el.style.position=position;window.scrollTo(0,0);},freezeHeader);
  geometry=await page.evaluate(({selections,heroSelector,sectionSelector,width})=>{
   const rect=el=>{const r=el.getBoundingClientRect();return{x:r.left+scrollX,y:r.top+scrollY,width:r.width,height:r.height};};
   const sections=[...document.querySelectorAll(sectionSelector)].map(el=>({...rect(el),id:el.getAttribute('data-fluid-section')||el.id||null,title:(el.querySelector('h1,h2')?.textContent||'').trim()})).filter(r=>r.width>10&&r.height>10);
   const pieces=selections.map(({id,kind,selector,index=0})=>{const el=document.querySelectorAll(selector)[index];if(!el)throw new Error('Missing source piece '+id);el.dataset.flyoverPiece=id;return{id,kind,...rect(el),radius:parseFloat(getComputedStyle(el).borderTopLeftRadius)||0,selector,index};});
   const hero=rect(document.querySelector(heroSelector));return{width,height:Math.ceil(document.documentElement.scrollHeight),heroHeight:Math.ceil(hero.y+hero.height),sections,pieces,fonts:[...document.fonts].map(f=>({family:f.family,status:f.status})),images:[...document.images].map(im=>({url:im.currentSrc||im.src,complete:im.complete,width:im.naturalWidth,height:im.naturalHeight}))};
  },{selections,heroSelector,sectionSelector,width});
  const missing=geometry.images.filter(im=>!im.complete||im.width===0);if(missing.length)throw new Error('Unsettled source images: '+JSON.stringify(missing));
  if(geometry.pieces.some(p=>p.x<-.1||p.x+p.width>width+.1||p.y<0||p.y+p.height>geometry.height+.1))throw new Error('A selected source element is clipped beyond page bounds');
  if(geometry.heroHeight>1536)throw new Error('Hero exceeds maximum1536px tile height; choose a shorter hero selector/viewport');
  await page.screenshot({path:path.join(outputDir,'source-full.png'),fullPage:true,type:'png',animations:'disabled',caret:'hide',timeout:45000});
  await page.evaluate(()=>{for(const el of document.querySelectorAll('[data-flyover-piece]'))el.style.visibility='hidden';});
  await page.screenshot({path:path.join(outputDir,'base-full.png'),fullPage:true,type:'png',animations:'disabled',caret:'hide',timeout:45000});
  await fs.writeFile(path.join(outputDir,'frozen-source.html'),await page.content());
 } finally {await browser.close();}
 const source=PNG.sync.read(await fs.readFile(path.join(outputDir,'source-full.png'))),base=PNG.sync.read(await fs.readFile(path.join(outputDir,'base-full.png')));
 if(source.width!==width*deviceScale||source.height!==geometry.height*deviceScale||base.width!==source.width||base.height!==source.height)throw new Error('Capture dimensions differ from measured CSS coordinates');
 const writePng=async(file,png)=>fs.writeFile(path.join(outputDir,file),PNG.sync.write(png));
 function crop(src,x,y,w,h){const p=new PNG({width:w,height:h});PNG.bitblt(src,p,x,y,w,h,0,0);return p;}
 const tiles=[];let y=0,index=0;
 while(y<geometry.height){const height=Math.min(y===0?geometry.heroHeight:1536,geometry.height-y),file=`base-${index++}.png`;await writePng(file,crop(base,0,y*deviceScale,width*deviceScale,height*deviceScale));tiles.push({file,x:0,y,width,height});y+=height;}
 const pieces=[];const rebuilt=new PNG({width:base.width,height:base.height});base.data.copy(rebuilt.data);
 for(const p of geometry.pieces){
  const left=Math.floor(p.x*deviceScale),top=Math.floor(p.y*deviceScale),right=Math.ceil((p.x+p.width)*deviceScale),bottom=Math.ceil((p.y+p.height)*deviceScale);
  const tx=Math.floor(p.x)-pad,ty=Math.floor(p.y)-pad,tw=Math.ceil(p.x+p.width)+pad-tx,th=Math.ceil(p.y+p.height)+pad-ty;
  const texture=new PNG({width:tw*deviceScale,height:th*deviceScale});
  PNG.bitblt(source,texture,left,top,right-left,bottom-top,left-tx*deviceScale,top-ty*deviceScale);
  PNG.bitblt(source,rebuilt,left,top,right-left,bottom-top,left,top);
  const file=`${p.id}.png`;await writePng(file,texture);pieces.push({id:p.id,kind:p.kind,radius:p.radius,x:p.x,y:p.y,width:p.width,height:p.height,file,texture:{x:tx,y:ty,width:tw,height:th}});
 }
 let changedPixels=0,maxDelta=0;for(let i=0;i<source.data.length;i+=4){let d=0;for(let c=0;c<4;c++)d=Math.max(d,Math.abs(source.data[i+c]-rebuilt.data[i+c]));if(d>0)changedPixels++;maxDelta=Math.max(maxDelta,d);}
 const layout={width:geometry.width,height:geometry.height,heroHeight:geometry.heroHeight,sections:geometry.sections,tiles,pieces,source:sourceUrl,deviceScale,capture:'Frozen native public DOM and original source CSS/media. Video posters; source header initial state. Independent pieces hidden from base and preserved in exact source positions.'};
 await fs.writeFile(path.join(outputDir,'LandingLayers.json'),JSON.stringify(layout,null,2));
 const report={...geometry,source:sourceUrl,deviceScale,capturedAt:new Date().toISOString(),errors,failedRequests:failed,freeze:layout.capture,reconstruction:{changedPixels,maxChannelDelta:maxDelta,exact:changedPixels===0},rights:'Existing publicly served brand media captured for user-authorized unpublished local test only; no general reuse license or publication permission asserted.'};
 await fs.writeFile(path.join(outputDir,'capture-report.json'),JSON.stringify(report,null,2));
 return {layout:path.join(outputDir,'LandingLayers.json'),width:layout.width,height:layout.height,heroHeight:layout.heroHeight,tiles:tiles.length,pieces:pieces.length,reconstruction:report.reconstruction,errors};
}
if(process.argv[1]&&path.resolve(process.argv[1])===path.resolve(fileURLToPath(import.meta.url))){const config=JSON.parse(await fs.readFile(process.argv[2],'utf8'));console.log(JSON.stringify(await captureLayers(config),null,2));}
