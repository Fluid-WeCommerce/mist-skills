import { progress, ease } from 'storyboard';
import { KineticPhrase } from './KineticPhrase';

export interface StoryCaption {
  text: string; start: number; end: number; accentWord?: string;
}
/** Film-level narration in type, separate from text inside the product UI. No autonomous clock. */
export function StoryCaptions({t, captions, font, ink, accent, x=130, y=34, width=1400, fontSize=64}:{
  t:number; captions:readonly StoryCaption[]; font:string; ink:string; accent:string;
  x?:number; y?:number; width?:number; fontSize?:number;
}) {
  return <>{captions.map((c,i)=>{
    if(t<c.start || t>=c.end)return null;
    const leave=progress(t,c.end-.35,c.end,ease.inCubic);
    return <div key={i} data-story-caption style={{position:'absolute',left:x,top:y,width,fontFamily:font,color:ink,
      opacity:1-leave,transform:`translateY(${-18*leave}px)`,pointerEvents:'none'}}>
      <KineticPhrase t={t} start={c.start} text={c.text} gap={.045} duration={.5}
        accent={accent} accentWord={c.accentWord}
        style={{fontSize,lineHeight:1.06,fontWeight:760,letterSpacing:'-.035em'}}/>
    </div>;
  })}</>;
}
