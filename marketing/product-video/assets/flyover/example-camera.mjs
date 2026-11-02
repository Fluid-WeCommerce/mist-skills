export const FILM={width:1920,height:1080,duration:9.97,focal:1880*1080/1152};
const clamp=v=>Math.max(0,Math.min(1,v));
export const smooth=(a,b,t)=>{const p=clamp((t-a)/(b-a));return p*p*(3-2*p);};
export const mix=(a,b,p)=>a+(b-a)*p;
const speeds=[[0,0],[.6,.5],[1.25,.5],[1.6,1],[7.3,1],[8.3,.12]];
const primitive=u=>u**6-3*u**5+2.5*u**4;
export function normalizedSpeed(t){for(let i=1;i<speeds.length;i++){const[a,x]=speeds[i-1],[b,y]=speeds[i];if(t<=b){const u=clamp((t-a)/(b-a)),q=u*u*u*(10+u*(-15+6*u));return mix(x,y,q);}}return .12;}
export function integratedSpeed(t){let sum=0;for(let i=1;i<speeds.length;i++){const[a,x]=speeds[i-1],[b,y]=speeds[i];if(t<=a)return sum;const u=clamp((t-a)/(b-a));sum+=(b-a)*(x*u+(y-x)*primitive(u));if(t<=b)return sum;}return sum+Math.max(0,t-8.3)*.12;}
function riseProgress(t){const x=Math.max(0,Math.min(1.5,t-7.75)),a=.6,hold=.6,decel=.3,area=.5*a+hold+.5*decel;let v=0;if(x<a)v=.5*x*x/a;else if(x<a+hold)v=.5*a+(x-a);else{const u=x-a-hold;v=.5*a+hold+u-.5*u*u/decel;}return clamp(v/area);}
export function flightY(t,layout){const from=layout.heroHeight*.45,to=layout.height-450;return from+(to-from)*integratedSpeed(Math.min(8.3,Math.max(0,t)))/integratedSpeed(8.3);}
export function timeAtPageY(y,layout){let a=0,b=8.3;for(let n=0;n<40;n++){const m=(a+b)/2;if(flightY(m,layout)<y)a=m;else b=m;}return(a+b)/2;}
export function cameraPose(t,layout,film=FILM){const h=film.height,f=film.focal,margin=(film.fitMargin??84)/2,whole=layout.height*f/(h-2*margin),flightD=mix(1640,1700,smooth(0,8.3,t));let distance=flightD,tilt=56*Math.PI/180,focusY=flightY(t,layout),phase='flight';
if(t>=7.75){phase='rise';distance=Math.exp(mix(Math.log(flightD),Math.log(whole),riseProgress(t)));tilt*=1-smooth(8.15,8.95,t);const bottom=h/2-margin;const pinned=layout.height-bottom*distance/(f*Math.cos(tilt)+bottom*Math.sin(tilt));focusY=mix(focusY,pinned,smooth(7.75,8.35,t));}
if(t>=9.25){phase='overhead';distance=whole/(1+.035*smooth(9.25,9.47,t));tilt=0;focusY=layout.height-(h/2-margin)*distance/f;}
const finalWidth=film.width,finalD=1440*f/finalWidth;
if(t>=9.47){phase='dive';const p=clamp((t-9.47)/.5),q=p<.5?2*p*p:1-2*(1-p)*(1-p);const d0=whole/1.035,top0=h-margin-layout.height*f/d0;distance=Math.exp(mix(Math.log(d0),Math.log(finalD),q));const top=mix(top0,0,smooth(0,.25,p));focusY=(h/2-top)*distance/f;tilt=0;}
if(t>=9.97){phase='monitor-handoff';distance=finalD;focusY=(h/2)*distance/f;}
return{phase,distance,tilt,focusY,x:0,y:-focusY-distance*Math.sin(tilt),z:distance*Math.cos(tilt),speed:normalizedSpeed(t),tailHaze:smooth(9.47,9.89,t),maskHeight:mix(layout.height,layout.heroHeight,smooth(9.78,9.97,t)),radius:mix(24,43,smooth(9.47,9.97,t))};}

// Example film clock from the slower approved cut. These times belong to the
// source path above; adapt them together for another page/story.
export const EXAMPLE_TIMING=Object.freeze({preRoll:.5,duration:7.6});
export function exampleSourceTime(t){
  const lead=EXAMPLE_TIMING.preRoll,rate=1.5,footer=7.3/rate-lead,rise=4.75;
  if(t<=-lead)return 0;
  if(t<=footer)return(t+lead)*rate;
  if(t<=rise){const span=rise-footer,p=(t-footer)/span;
    return(2*p**3-3*p**2+1)*7.3+(p**3-2*p**2+p)*span*rate
      +(-2*p**3+3*p**2)*7.75+(p**3-p**2)*span;
  }
  return Math.min(9.97,7.75+t-rise);
}
