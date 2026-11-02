import{FILM,cameraPose,timeAtPageY,smooth,mix}from './example-camera.mjs';
const vertex=`varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`;
const fragment=`uniform sampler2D map;uniform vec2 tileSize;uniform vec2 tileOrigin;uniform float maskHeight;uniform float radius;uniform float haze;uniform float heroHeight;varying vec2 vUv;void main(){vec2 p=tileOrigin+vec2(vUv.x*tileSize.x,(1.-vUv.y)*tileSize.y);vec2 halfSize=vec2(720.,maskHeight*.5);vec2 q=abs(p-vec2(720.,maskHeight*.5))-(halfSize-radius);float d=length(max(q,0.))+min(max(q.x,q.y),0.)-radius;vec4 c=texture2D(map,vUv);c.a*=1.-smoothstep(-.8,.8,d);if(p.y>heroHeight+.1)c.rgb=mix(c.rgb,vec3(.947,.956,.956),haze);if(c.a<.001)discard;gl_FragColor=c;}`;
const dofFragment=`uniform vec3 backdrop;uniform sampler2D sceneColor;uniform sampler2D sceneDepth;uniform vec2 resolution;uniform float cameraNear;uniform float cameraFar;uniform float focus;uniform float baseLod;varying vec2 vUv;
float depthAt(vec2 uv){float d=texture2D(sceneDepth,uv).x;return cameraNear*cameraFar/(cameraFar-d*(cameraFar-cameraNear));}
vec3 background(vec2 uv){float vignette=clamp(length((uv-.5)*vec2(1.05,1.2)),0.,1.);return backdrop*(1.-vignette*.025);}
vec3 sampleAt(vec2 uv,float lod){vec4 c=textureLod(sceneColor,uv,lod);return c.rgb+background(uv)*(1.-c.a);}
void main(){float d=depthAt(vUv);float coc=d<focus?75.*(focus-d)/max(d,1.):6.*(d-focus)/max(d,1.);coc=clamp(coc,0.,120.);float lod=baseLod+clamp(log2(max(1.,coc*.18)),0.,6.);vec3 color=sampleAt(vUv,baseLod);float weight=1.;for(int i=0;i<40;i++){float n=float(i)+.5;float a=n*2.39996323;vec2 off=vec2(cos(a),sin(a))*sqrt(n/40.)*coc/resolution;float w=1.;color+=sampleAt(clamp(vUv+off,0.,1.),lod)*w;weight+=w;}gl_FragColor=vec4(color/weight,1.);
#include <colorspace_fragment>
}`;
function rounded(THREE,w,h,r){const s=new THREE.Shape(),x=-w/2,y=-h;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,-r);s.quadraticCurveTo(x+w,0,x+w-r,0);s.lineTo(x+r,0);s.quadraticCurveTo(x,0,x,-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);return s;}
/** Three.js is supplied by the caller; no installed global or company-specific imports.
 * layout uses a 1440px page coordinate system. All motion is resolved from draw(t).
 */
export function createFlyoverRenderer(THREE,canvas,layout,asset,options={}){
 const film={...FILM,...options.film};
 const background=new THREE.Color(options.background ?? '#f4efe8');

 const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true,preserveDrawingBuffer:true});renderer.setSize(film.width,film.height,false);renderer.setPixelRatio(1);renderer.setClearColor('#000000',0);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NoToneMapping;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(2*Math.atan(film.height/(2*film.focal))*180/Math.PI,film.width/film.height,50,100000);scene.add(new THREE.AmbientLight('#ffffff',1));
 const light=new THREE.DirectionalLight('#fffaf3',2.2);light.castShadow=true;light.shadow.mapSize.set(2048,2048);light.shadow.camera.left=-1800;light.shadow.camera.right=1800;light.shadow.camera.top=2600;light.shadow.camera.bottom=-2600;light.shadow.camera.near=100;light.shadow.camera.far=12000;light.shadow.normalBias=1;light.shadow.bias=-.00004;light.shadow.radius=4;scene.add(light,light.target);
 const floor=new THREE.Mesh(new THREE.PlaneGeometry(40000,60000),new THREE.ShadowMaterial({color:'#1a2133',opacity:.2}));floor.position.set(0,-layout.height/2,-16);floor.receiveShadow=true;scene.add(floor);
 // The backing needs real clearance from the texture, even at the full-page distance.
 const paper=new THREE.Mesh(new THREE.ExtrudeGeometry(rounded(THREE,1440,layout.height,24),{depth:5,bevelEnabled:true,bevelSize:1,bevelThickness:1,bevelSegments:2,steps:1,curveSegments:12}),new THREE.MeshStandardMaterial({color:'#fffcf5',roughness:1}));paper.position.z=-10;paper.castShadow=true;scene.add(paper);
 const receiving=new THREE.Mesh(new THREE.PlaneGeometry(1440,layout.height),new THREE.ShadowMaterial({color:'#1a2133',opacity:.22,transparent:true,depthWrite:false}));receiving.position.set(0,-layout.height/2,.8);receiving.receiveShadow=true;receiving.renderOrder=2;scene.add(receiving);
 // Supersample the scene before the DOF pass: default-canvas antialiasing does
 // not affect an offscreen target, especially when the page is only 140px wide.
 const sceneScale=options.sceneScale ?? 1.5,targetWidth=film.width*sceneScale,targetHeight=film.height*sceneScale;
 const target=new THREE.WebGLRenderTarget(targetWidth,targetHeight,{minFilter:THREE.LinearMipmapLinearFilter,magFilter:THREE.LinearFilter,generateMipmaps:true,depthBuffer:true});target.texture.generateMipmaps=true;target.depthTexture=new THREE.DepthTexture(targetWidth,targetHeight,THREE.UnsignedIntType);
 const postScene=new THREE.Scene(),postCamera=new THREE.OrthographicCamera(-1,1,1,-1,0,1);const post=new THREE.ShaderMaterial({vertexShader:vertex,fragmentShader:dofFragment,depthTest:false,depthWrite:false,uniforms:{backdrop:{value:background},sceneColor:{value:target.texture},sceneDepth:{value:target.depthTexture},resolution:{value:new THREE.Vector2(film.width,film.height)},cameraNear:{value:camera.near},cameraFar:{value:camera.far},focus:{value:1360},baseLod:{value:Math.log2(sceneScale)}}});postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),post));
 const loads=[],textures=[],pageTiles=[],pieces=[];const anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());
 const texture=file=>{const image=new Image(),tex=new THREE.Texture(image);tex.colorSpace=THREE.SRGBColorSpace;tex.minFilter=THREE.LinearMipmapLinearFilter;tex.magFilter=THREE.LinearFilter;tex.anisotropy=anisotropy;textures.push(tex);loads.push(new Promise((resolve,reject)=>{image.onload=()=>{tex.needsUpdate=true;resolve();};image.onerror=()=>reject(Error('Texture failed '+file));}));image.src=asset(file);return tex;};
 for(const tile of layout.tiles){const map=texture(tile.file);const material=new THREE.ShaderMaterial({vertexShader:vertex,fragmentShader:fragment,transparent:true,depthWrite:true,uniforms:{map:{value:map},tileSize:{value:new THREE.Vector2(tile.width,tile.height)},tileOrigin:{value:new THREE.Vector2(tile.x,tile.y)},maskHeight:{value:layout.height},radius:{value:24},haze:{value:0},heroHeight:{value:layout.heroHeight}}});const mesh=new THREE.Mesh(new THREE.PlaneGeometry(tile.width,tile.height),material);mesh.position.set(tile.x+tile.width/2-720,-tile.y-tile.height/2,.1);mesh.renderOrder=1;scene.add(mesh);pageTiles.push({tile,mesh,material});}
 for(const p of layout.pieces){const tex=texture(p.file),group=new THREE.Group();
 // A source-measured radius is optional. Legacy captures without one keep
 // their original silhouette; do not silently round every company's rectangles.
 const radius=p.motion?.radius??p.radius;
 let alpha=null;
 if(Number.isFinite(radius)){
  const mask=document.createElement('canvas'),density=2;
  mask.width=p.texture.width*density;mask.height=p.texture.height*density;
  const ctx=mask.getContext('2d');ctx.scale(density,density);ctx.fillStyle='#000';ctx.fillRect(0,0,p.texture.width,p.texture.height);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.roundRect(p.x-p.texture.x,p.y-p.texture.y,p.width,p.height,Math.max(0,Math.min(radius,p.width/2,p.height/2)));ctx.fill();
  alpha=new THREE.CanvasTexture(mask);alpha.minFilter=THREE.LinearMipmapLinearFilter;alpha.anisotropy=anisotropy;textures.push(alpha);
 }
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(p.texture.width,p.texture.height),new THREE.MeshBasicMaterial({map:tex,alphaMap:alpha,transparent:true,alphaTest:.02,side:THREE.DoubleSide,depthWrite:true}));mesh.position.set(p.texture.x+p.texture.width/2-(p.x+p.width/2),-(p.texture.y+p.texture.height/2)+(p.y+p.height/2),0);mesh.castShadow=true;group.add(mesh);let edge;
 if(['card','testimonial'].includes(p.kind)){edge=new THREE.Mesh(new THREE.BoxGeometry(p.width,p.height,1),new THREE.MeshStandardMaterial({color:'#fffdfb',roughness:.8}));edge.position.z=-3;edge.castShadow=true;group.add(edge);}
 scene.add(group);pieces.push({p,group,mesh,edge,at:timeAtPageY(p.y+p.height/2,layout)});}
 let handoff;
 if(options.handoffTexture){
   const map=texture(options.handoffTexture),material=new THREE.MeshBasicMaterial({map,transparent:true,depthWrite:false,toneMapped:false});
   handoff=new THREE.Mesh(new THREE.PlaneGeometry(1440,1440*film.height/film.width),material);
   handoff.position.set(0,-720*film.height/film.width,4);handoff.renderOrder=6;scene.add(handoff);
 }
 let loaded=false,disposed=false,lastT=0,lastHeight=layout.height,lastRadius=24;const ready=Promise.all(loads).then(()=>{loaded=true;draw(lastT);});
 function draw(t){lastT=t;if(!loaded||disposed)return;const pose=cameraPose(t,layout,film);
 // Follow the camera distance with the clipping planes. A fixed 50–100000 range
 // loses subpixel layer separation during the 18k-unit overhead move.
 camera.near=Math.max(100,pose.distance*.12);camera.far=pose.distance+layout.height+3000;camera.updateProjectionMatrix();
 post.uniforms.cameraNear.value=camera.near;post.uniforms.cameraFar.value=camera.far;
 camera.position.set(pose.x,pose.y,pose.z);camera.lookAt(0,-pose.focusY,0);camera.updateMatrixWorld();light.position.set(-1300,-pose.focusY+900,2800);light.target.position.set(0,-pose.focusY,0);light.target.updateMatrixWorld();
 if(Math.abs(pose.maskHeight-lastHeight)>.01||Math.abs(pose.radius-lastRadius)>.01){paper.geometry.dispose();paper.geometry=new THREE.ExtrudeGeometry(rounded(THREE,1440,pose.maskHeight,pose.radius),{depth:5,bevelEnabled:true,bevelSize:1,bevelThickness:1,bevelSegments:2,steps:1,curveSegments:12});lastHeight=pose.maskHeight;lastRadius=pose.radius;}
 receiving.scale.y=pose.maskHeight/layout.height;receiving.position.y=-pose.maskHeight/2;
 for(const {tile,mesh,material}of pageTiles){mesh.visible=tile.y<pose.maskHeight&&!(handoff&&t>=9.47&&tile.y===0);material.uniforms.maskHeight.value=pose.maskHeight;material.uniforms.radius.value=pose.radius;material.uniforms.haze.value=pose.tailHaze;}
 // Per-subject depth is expressed in source-page units. Bottom pivots keep tall
 // photographs/cards above the page rather than letting their lower edge cut through it.
 let focusWeight=0,focusDistance=pose.distance;
 const forward=new THREE.Vector3();camera.getWorldDirection(forward);
 for(const {p,group,mesh,edge,at}of pieces){
  const hero=p.id.startsWith('hero-'),m=p.motion??{};
  const arrival=at+(m.offset??0),entry=smooth(hero ? .1 : arrival-.85,hero ? 1.25 : arrival-.05,t);
  const settle=hero?0:smooth(arrival+.7,arrival+1.5,t),env=entry*(1-settle)*(1-smooth(9.47,9.97,t));
  // Keep the starter's established defaults; art direction overrides each subject.
  const baseLift=hero?64:p.kind==='photo'?78:p.kind==='testimonial'?112:p.kind==='bottle'?65:30;
  const baseAngle=hero?30:p.kind==='photo'?26:p.kind==='testimonial'||p.kind==='bottle'?30:14;
  const lift=(m.lift??baseLift)*env;
  const angle=(m.angle??baseAngle)*Math.PI/180*env;
  const hinge=m.pivot==='bottom',half=p.height/2;
  group.position.set(p.x+p.width/2-720,-p.y-half-(hinge?half*(1-Math.cos(angle)):0),3+lift+(hinge?half*Math.sin(angle):0));
  group.rotation.x=angle;
  mesh.material.opacity=p.y>layout.heroHeight?1-pose.tailHaze:1;
  group.visible=p.y<pose.maskHeight&&!(p.y>layout.heroHeight&&pose.tailHaze>.999);
  if(edge){const thick=mix(2,m.thickness??8,env);edge.scale.z=thick;edge.position.z=-thick/2-.3;edge.material.opacity=mesh.material.opacity;edge.material.transparent=true;}
  // Follow the lifted subject as it crosses the centre, then return focus to the page.
  // Weight fades continuously and vanishes before the full-page rise.
  const w=(1-smooth(.2,.8,Math.abs(t-arrival)))*env*(1-smooth(7.6,8.3,t));
  if(w>focusWeight){focusWeight=w;focusDistance=new THREE.Vector3().subVectors(group.position,camera.position).dot(forward);}
 }

 if(handoff){handoff.material.opacity=1;handoff.visible=t>=9.47;}
 post.uniforms.focus.value=mix(pose.distance,focusDistance,focusWeight);renderer.setRenderTarget(target);renderer.clear();renderer.render(scene,camera);renderer.setRenderTarget(null);renderer.clear();renderer.render(postScene,postCamera);canvas.dataset.flyoverPhase=pose.phase;canvas.dataset.flyoverDistance=String(pose.distance);canvas.dataset.flyoverPageY=String(pose.focusY);
 }
 function dispose(){disposed=true;scene.traverse(o=>{o.geometry?.dispose();const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):[];ms.forEach(m=>m.dispose());});postScene.traverse(o=>o.geometry?.dispose());post.dispose();target.dispose();textures.forEach(t=>t.dispose());renderer.dispose();renderer.forceContextLoss();}
 return{ready,draw,dispose};
}
