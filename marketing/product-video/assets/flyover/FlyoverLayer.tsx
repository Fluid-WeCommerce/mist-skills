import {useLayoutEffect,useRef} from 'react';
import {asset,ease,mix,progress,registerRenderResource} from 'storyboard';
import {createFlyoverRenderer} from './create-flyover-renderer.mjs';
import {FILM,exampleSourceTime} from './example-camera.mjs';

type Point={x:number;y:number};
type Film={width:number;height:number;focal:number};
type Props={
 three:any; t:number; layout:any; assetRoot:string; duration?:number;
 sourceTime?:(t:number)=>number; film?:Film; background?:string; sceneScale?:number;
 handoffTexture?:string; startQuad?:Point[]; landingQuad:Point[];
 matrixForQuad:(quad:Point[],width:number,height:number)=>string;
};
/** Frozen page layers, one seek-safe perspective assembly. Supply Three.js from
 * this project's licensed local vendor; no hidden global/runtime dependency.
 * Match film aspect to the destination aperture and use the same sourceTime on
 * outgoing-scene pre-roll. Caller renders destination hardware behind this layer.
 */
export function FlyoverLayer({three,t,layout,assetRoot,duration=7.6,sourceTime=exampleSourceTime,
 film=FILM,background='#f4efe8',sceneScale=1.5,handoffTexture,startQuad,landingQuad,matrixForQuad}:Props){
 const canvas=useRef<HTMLCanvasElement>(null),view=useRef<any>(null),now=useRef(t);now.current=t;
 useLayoutEffect(()=>{
  if(!canvas.current)return;
  const v=createFlyoverRenderer(three,canvas.current,layout,(file:string)=>asset(assetRoot+'/'+file),{film,background,sceneScale,handoffTexture});
  view.current=v;let alive=true;const release=registerRenderResource(v.ready);
  void v.ready.then(()=>{if(alive)v.draw(sourceTime(now.current));release();},()=>release());
  return()=>{alive=false;release();v.dispose();view.current=null;};
 },[three,layout,assetRoot,film.width,film.height,film.focal,background,sceneScale,handoffTexture,sourceTime]);
 useLayoutEffect(()=>{view.current?.draw(sourceTime(t));});
 const pull=progress(t,duration-.67,duration,ease.inOutCubic);
 const start=startQuad??[{x:0,y:0},{x:film.width,y:0},{x:film.width,y:film.height},{x:0,y:film.height}];
 const quad=start.map((p,i)=>({x:mix(p.x,landingQuad[i].x,pull),y:mix(p.y,landingQuad[i].y,pull)}));
 const gone=progress(t,duration-.18,duration,ease.smooth);
 return <div data-layered-page-flyover data-source-time={sourceTime(t)} style={{position:'absolute',left:0,top:0,width:film.width,height:film.height,transformOrigin:'0 0',transform:matrixForQuad(quad,film.width,film.height),opacity:1-gone,overflow:'hidden',pointerEvents:'none'}}>
  <canvas ref={canvas} width={film.width} height={film.height} style={{display:'block',width:film.width,height:film.height}}/>
 </div>;
}
