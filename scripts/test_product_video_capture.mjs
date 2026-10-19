// Integration check: system Chrome/Edge + Node only; no models, paid APIs, or editor install.
// Run from any directory: node scripts/test_product_video_capture.mjs
import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import os from 'node:os';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
const exec=promisify(execFile);
import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const source=path.resolve(root,'../marketing/product-video/assets/flyover');
const sandbox=await fs.mkdtemp(path.join(os.tmpdir(),'mist-product-video-capture-test-'));await fs.mkdir(path.join(sandbox,'vendor'));
for(const name of ['capture-layers.mjs','capture-browser.mjs','vendor/png.cjs','vendor/pngjs-LICENSE.txt']){await fs.copyFile(path.join(source,name),path.join(sandbox,name));}
const {captureLayers}=await import(pathToFileURL(path.join(sandbox,'capture-layers.mjs')));
const profiles=()=>fs.readdir(os.tmpdir()).then(xs=>xs.filter(x=>x.startsWith('mist-source-capture-')).sort());const before=await profiles();let writes=0;
const server=http.createServer((req,res)=>{if(req.method==='POST')writes++;if(req.url==='/missing.png'){res.writeHead(404);res.end();return;}
const mode=req.url.slice(1);res.setHeader('Content-Type','text/html');res.end(`<!doctype html><html><head><style>*{box-sizing:border-box}html,body{margin:0;font-family:Arial;background:#f9f4ef}section{height:750px;padding:40px}article{width:400px;height:240px;background:#3caf83;border-radius:20px;padding:30px;${mode==='shadow'?'box-shadow:0 12px 30px #0007':''}}#lower{background:#eceeff}img{width:100px;height:100px}</style></head><body><main><section id="hero"><h1>Independent source capture fixture</h1><article id="card">Real source rectangle${mode==='visible-child'?'<span style="visibility:visible!important;display:block;background:red;width:100px;height:100px">Child</span>':''}</article>${mode==='missing'?'<img src="/missing.png">':''}</section><section id="lower"><h2>Lower source section</h2><article id="second">Second source rectangle</article></section></main><script>fetch('/write',{method:'POST'}).catch(()=>{});${mode==='growing'?`let n=0;window.addEventListener('scroll',()=>{let s=document.createElement('section');s.textContent='More '+(++n);document.querySelector('main').append(s)})`:''}</script></body></html>`)});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const url='http://127.0.0.1:'+server.address().port;
const base={width:1440,viewportHeight:900,heroSelector:'#hero',sectionSelector:'section',pieces:[{id:'card',kind:'card',selector:'#card'},{id:'second',kind:'card',selector:'#second'}]};const tests=[];
const present=p=>fs.access(p).then(()=>true,()=>false);
try{
for(const deviceScale of [1,2]){const outputDir=path.join(sandbox,'scale-'+deviceScale);const result=await captureLayers({...base,deviceScale,sourceUrl:url,outputDir});assert(result.reconstruction.exact);const report=JSON.parse(await fs.readFile(path.join(outputDir,'capture-report.json')));assert(report.blockedRequests.some(x=>x.method==='POST'));assert.equal(writes,0);assert.equal(report.tools.storyboardRequired,false);tests.push({test:'isolated no-editor capture '+deviceScale+'x',pass:true,pieces:result.pieces});}
for(const [mode,match] of [['missing',/Unsettled source images/],['shadow',/Source changed outside selected bounds/],['growing',/bounded capture/]]){const outputDir=path.join(sandbox,mode);await assert.rejects(()=>captureLayers({...base,deviceScale:1,sourceUrl:url+'/'+mode,outputDir}),match);assert(!await present(outputDir));tests.push({test:mode+' failure cleans owned output',pass:true});}
const childOutput=path.join(sandbox,'visible-child');await captureLayers({...base,deviceScale:1,sourceUrl:url+'/visible-child',outputDir:childOutput});const {default:codec}=await import(pathToFileURL(path.join(sandbox,'vendor/png.cjs')));const childBase=codec.PNG.sync.read(await fs.readFile(path.join(childOutput,'base-full.png')));const offset=(240*childBase.width+90)*4;assert.deepEqual([...childBase.data.subarray(offset,offset+3)],[249,244,239]);tests.push({test:'explicitly visible child removed from base',pass:true});
const existing=path.join(sandbox,'existing');await fs.mkdir(existing);await fs.writeFile(path.join(existing,'approved.txt'),'keep');await assert.rejects(()=>captureLayers({...base,sourceUrl:url,outputDir:existing}),/EEXIST/);assert.equal(await fs.readFile(path.join(existing,'approved.txt'),'utf8'),'keep');tests.push({test:'existing output unchanged',pass:true});
const overlap=path.join(sandbox,'overlap');await assert.rejects(()=>captureLayers({...base,sourceUrl:url,outputDir:overlap,pieces:[{id:'parent',kind:'card',selector:'#hero'},{id:'child',kind:'card',selector:'#card'}]}),/Overlapping/);assert(!await present(overlap));tests.push({test:'overlap rejects and cleans',pass:true});
const cli=path.resolve(source,'../player/cli.mjs');await exec(process.execPath,[cli,'materialize','--project',sandbox,'--dest','tools/player']);const captureConfig=path.join(sandbox,'capture-config.json');await fs.writeFile(captureConfig,JSON.stringify({...base,deviceScale:1,sourceUrl:url,outputDir:path.join(sandbox,'cli-capture')}));const captureCli=path.join(sandbox,'tools/player/cli.mjs');const cliResult=JSON.parse((await exec(process.execPath,[captureCli,'capture','--project',sandbox,'--config',captureConfig])).stdout);assert(cliResult.reconstruction.exact);assert.equal(cliResult.pieces,2);tests.push({test:'materialized CLI captures without sibling catalog or editor',pass:true});
const after=await profiles();assert.deepEqual(after,before);tests.push({test:'isolated Chrome profiles cleaned',pass:true});
console.log(JSON.stringify({tests},null,2));
}finally{server.closeAllConnections();await new Promise(r=>server.close(r));await fs.rm(sandbox,{recursive:true,force:true});}
