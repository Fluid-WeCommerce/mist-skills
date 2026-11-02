import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

// Hash provenance and check company identity; this does not assess visual quality or approve marketing claims.
const argv=process.argv.slice(2);
const option=(name,fallback)=>{const i=argv.indexOf(name);if(i<0)return fallback;if(!argv[i+1])throw new Error(`Missing ${name}`);return argv[i+1];};
const root=path.resolve(option('--root','.'));
const company=option('--company');
const sourceDir=option('--source-dir','video');
const key=s=>String(s).normalize('NFKC').trim().toLowerCase();
const normalize=s=>s.normalize('NFKC').replace(/\s+/g,' ').trim();
async function inside(name){
  if(typeof name!=='string'||!name||path.isAbsolute(name)||name.includes('\\')||name.split('/').includes('..'))throw new Error(`Invalid project-relative path: ${name}`);
  const p=await fs.realpath(path.join(root,name));const r=path.relative(await fs.realpath(root),p);
  if(r.startsWith('..')||path.isAbsolute(r))throw new Error(`Path escapes project: ${name}`);
  return p;
}
async function json(name){return JSON.parse(await fs.readFile(await inside(name),'utf8'));}
try{
  if(!company)throw new Error('--company must come from the active company context, not from an example or the film brief');
  const map=await json(option('--map',`${sourceDir}/source-map.json`));
  const brief=await json(`${sourceDir}/brief.json`);
  if(map.version!==1||key(map.company)!==key(company)||key(brief.company)!==key(company))throw new Error(`Company mismatch: active=${company}; map=${map.company}; brief=${brief.company}`);
  if(!Array.isArray(map.sourceOrigins)||!map.sourceOrigins.length)throw new Error('Declare the active company sourceOrigins');
  const origins=new Set(map.sourceOrigins.map(x=>new URL(x).origin));
  if(!Array.isArray(map.assets)||!map.assets.length)throw new Error('No traced company assets');
  const records=new Map();
  for(const a of map.assets){
    if(records.has(a.file))throw new Error(`Duplicate source record: ${a.file}`);
    if(!['company-source','company-capture','ui-reconstruction','neutral'].includes(a.kind))throw new Error(`Unknown provenance: ${a.file}`);
    if(a.kind!=='neutral'&&!origins.has(new URL(a.sourcePage).origin))throw new Error(`Foreign company source page: ${a.file}`);
    if(a.kind==='company-source'&&!/^https:\/\//.test(a.sourceUrl??''))throw new Error(`Missing original asset URL: ${a.file}`);
    const bytes=await fs.readFile(await inside(a.file));
    const actual=createHash('sha256').update(bytes).digest('hex');
    if(actual!==a.sha256)throw new Error(`Asset differs from its source record: ${a.file}`);
    records.set(a.file,a);
  }
  const project=await json(`${sourceDir}/project.json`);
  for(const file of project.requiredAssets??[]){
    if(file.startsWith('assets/')&&!records.has(`${sourceDir}/${file}`))throw new Error(`Untraced required visual: ${file}`);
  }
  const brandDir=path.join(root,sourceDir,'assets/brand');
  const walk=async dir=>{for(const ent of await fs.readdir(dir,{withFileTypes:true})){const p=path.join(dir,ent.name);if(ent.isDirectory())await walk(p);else if(!records.has(path.relative(root,p).split(path.sep).join('/')))throw new Error(`Untraced company media: ${p}`);}};
  await walk(brandDir);
  for(const c of map.copy??[]){
    if(!origins.has(new URL(c.sourcePage).origin))throw new Error(`Foreign company copy: ${c.text}`);
    const source=await fs.readFile(await inside(c.sourceFile),'utf8');
    if(c.editorial && (typeof c.sourceQuote!=='string'||!c.sourceQuote.trim()))throw new Error(`Editorial copy needs its underlying source quote: ${c.text}`);
    if(!normalize(source).includes(normalize(c.editorial?c.sourceQuote:c.text)))throw new Error(`Copy absent from frozen company source: ${c.text}`);
  }
  console.log(JSON.stringify({ok:true,company,assets:records.size,copy:(map.copy??[]).length,sourceOrigins:[...origins],proof:'Company identity, declared visual input hashes and traced copy; visual review still required.'},null,2));
}catch(e){console.error(JSON.stringify({ok:false,error:e.message}));process.exitCode=1;}
