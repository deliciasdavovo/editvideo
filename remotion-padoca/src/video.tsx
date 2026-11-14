import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, Img, staticFile} from 'remotion';
const shots=[
 {file:'croissant.jpg',from:0,to:150,caption:''},
 {file:'trouxinha.jpg',from:150,to:300,caption:''},
 {file:'mesa.jpg',from:300,to:450,caption:''},
 {file:'croissant.jpg',from:450,to:600,caption:''},
 {file:'mesa.jpg',from:600,to:750,caption:'Delícias da Vovó'}
];
export const Padoca=()=>{const f=useCurrentFrame();return <AbsoluteFill style={{backgroundColor:'#171a13'}}>{shots.map((s,i)=>{const local=f-s.from;if(local<0||f>=s.to)return null;const opacity=interpolate(local,[0,10,140,150],[0,1,1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});const scale=interpolate(local,[0,150],[1.03,1.17]);return <AbsoluteFill key={i} style={{opacity,overflow:'hidden'}}><Img src={staticFile(s.file)} style={{width:'100%',height:'100%',objectFit:'cover',transform:`scale(${scale})`}}/><AbsoluteFill style={{background:'linear-gradient(transparent 55%,rgba(14,18,13,.65))'}}/>{s.caption&&<div style={{position:'absolute',bottom:260,width:'100%',textAlign:'center',color:'#fff4df',fontFamily:'Georgia',fontSize:78,fontWeight:700}}>{s.caption}<div style={{fontFamily:'sans-serif',fontSize:34,marginTop:25}}>Desde 2005 · Paixão em servir!</div></div>}</AbsoluteFill>})}</AbsoluteFill>};
