/** Optional original synthesized demo score, no recordings or dependencies.
 * Run only when original music is appropriate to the brief. Does not replace
 * a user's selected/licensed track. Node 22+. Creates new files, never replaces.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
const seconds=Number(process.argv[2] ?? 45);
if(!Number.isFinite(seconds)||seconds<5||seconds>180)throw Error('Choose duration5–180seconds');
const sr=48000, frames=Math.ceil(seconds*sr),left=new Float32Array(frames),right=new Float32Array(frames);
const beat=60/100, midi=n=>440*2**((n-69)/12);
function add(at,length,fn,volume=1,pan=0){const start=Math.round(at*sr),len=Math.min(Math.ceil(length*sr),frames-start);for(let j=Math.max(0,-start);j<len;j++){const v=fn(j/sr)*volume;left[start+j]+=v*Math.sqrt((1-pan)/2);right[start+j]+=v*Math.sqrt((1+pan)/2);}}
function key(at,n,length=1.6,vol=.17,pan=0){const f=midi(n);add(at,length,t=>{const attack=Math.min(1,t/.006);const tone=Math.sin(2*Math.PI*f*t)*Math.exp(-t*2.5)+.23*Math.sin(2*Math.PI*f*2.002*t)*Math.exp(-t*5)+.09*Math.sin(2*Math.PI*f*3*t)*Math.exp(-t*8);return attack*tone},vol,pan);}
function bass(at,n,vol=.2){const f=midi(n);add(at,.48,t=>Math.min(1,t/.018)*Math.exp(-t*8)*(Math.sin(2*Math.PI*f*t)+.15*Math.sin(2*Math.PI*f*2*t)),vol,0);}
let seed=74941;const noise=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/2147483648-1;};
function hat(at,vol=.016,pan=.3){let last=0;add(at,.09,t=>{const n=noise(),v=n-last;last=n;return v*Math.exp(-t*70)*Math.min(1,t/.002)},vol,pan);}
function kick(at){add(at,.22,t=>Math.sin(2*Math.PI*(48*t+5*(1-Math.exp(-t*35))))*Math.exp(-t*24)*Math.min(1,t/.003),.17);}
const chords=[[50,57,60,64,69],[46,53,57,60,65],[53,60,64,67,72],[48,55,60,62,67]];
const bars=Math.ceil(seconds/(beat*4));
for(let bar=0;bar<bars;bar++){
 const at=bar*4*beat,chord=chords[Math.floor(bar/2)%4];
 for(const off of [.0,1.5,2.75]){chord.slice(1,4).forEach((n,k)=>key(at+off*beat+k*.017,n,1.65,.105,[-.4,.1,.45][k]));}
 bass(at,chord[0]);bass(at+1.75*beat,chord[0]+12,.13);bass(at+2.5*beat,chord[0],.17);
 if(bar>0){kick(at);kick(at+2.5*beat);for(let k=0;k<8;k++)hat(at+k*.5*beat+(k%2?.025:0),k%2?.012:.02,k%2?.45:-.3);}
 if(bar%2===1){const phrase=[chord[4],chord[3],chord[2]+12,chord[3]];phrase.forEach((n,k)=>key(at+(k*.75+.5)*beat,n,1.1,.075,k%2?.32:-.32));}
}
let energy=0,peak=0;for(let i=0;i<frames;i++){energy+=(left[i]**2+right[i]**2)/2;peak=Math.max(peak,Math.abs(left[i]),Math.abs(right[i]));}
const gain=Math.min(.095/Math.sqrt(energy/frames),.52/peak);
for(let i=0;i<frames;i++){const t=i/sr,fade=Math.min(1,t/.5)*Math.min(1,Math.max(0,(seconds-t)/2));left[i]*=gain*fade;right[i]*=gain*fade;}
function wav(l,r){const n=l.length,b=Buffer.alloc(44+n*4);b.write('RIFF');b.writeUInt32LE(b.length-8,4);b.write('WAVEfmt ',8);b.writeUInt32LE(16,16);b.writeUInt16LE(1,20);b.writeUInt16LE(2,22);b.writeUInt32LE(sr,24);b.writeUInt32LE(sr*4,28);b.writeUInt16LE(4,32);b.writeUInt16LE(16,34);b.write('data',36);b.writeUInt32LE(n*4,40);for(let i=0;i<n;i++){b.writeInt16LE(Math.round(Math.max(-1,Math.min(1,l[i]))*32767),44+i*4);b.writeInt16LE(Math.round(Math.max(-1,Math.min(1,r[i]))*32767),46+i*4);}return b;}
const output=path.resolve('video/music/original-score.wav');await fs.mkdir(path.dirname(output),{recursive:true});await fs.writeFile(output,wav(left,right),{flag:'wx'});
const count=Math.ceil(.065*sr),cl=new Float32Array(count),cr=new Float32Array(count);for(let i=0;i<count;i++){const t=i/sr;cl[i]=cr[i]=.045*(noise()*.35+Math.sin(2*Math.PI*1250*t)*.65)*Math.exp(-t*100)*Math.min(1,t/.001);}
const click=path.resolve('video/sounds/soft-click.wav');await fs.mkdir(path.dirname(click),{recursive:true});await fs.writeFile(click,wav(cl,cr),{flag:'wx'});
console.log(JSON.stringify({seconds,sampleRate:sr,music:'music/original-score.wav',effect:'sounds/soft-click.wav',provenance:'Original deterministic synthesized notes and percussion; no third-party recording. Optional demo score; use licensed preferred music when supplied.',bpm:100},null,2));
