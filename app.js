const KEY='videoedit-projects-v1';let projects=[],selected=null;const $=id=>document.getElementById(id);const uid=()=>Math.random().toString(36).slice(2)+Date.now().toString(36);const escapeHTML=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));try{projects=JSON.parse(localStorage.getItem(KEY)||'[]')}catch{};const current=()=>projects.find(p=>p.id===selected);function save(){try{localStorage.setItem(KEY,JSON.stringify(projects));$('notice').textContent='Salvo neste navegador.'}catch{$('notice').textContent='Armazenamento cheio. Exporte o projeto para preservar seus arquivos.'}}function render(){const p=current();$('projects').innerHTML=projects.map(x=>'<button class="project '+(x.id===selected?'active':'')+'" data-id="'+x.id+'">'+escapeHTML(x.title)+'</button>').join('');$('empty').hidden=!!p;$('editor').hidden=!p;if(!p)return;$('projectTitle').value=p.title;$('script').value=p.script;$('seconds').value=p.seconds||3;$('wpm').value=p.wpm||140;renderScenes()}function renderScenes(){const p=current();if(!p)return;$('sceneCount').textContent=p.scenes.length+' cenas';$('scenes').innerHTML=p.scenes.map((s,i)=>'<article class="scene" data-index="'+i+'"><div class="meta"><span>Cena '+(i+1)+'</span><span>'+p.scenes.slice(0,i).reduce((a,x)=>a+Number(x.duration||3),0).toFixed(1)+'s</span></div>'+(s.image?'<img class="preview" src="'+s.image+'" alt="Imagem da cena">':'<div class="preview">+ Adicionar imagem</div>')+'<input type="file" accept="image/*,.gif" aria-label="Imagem da cena '+(i+1)+'"><textarea aria-label="Texto da cena">'+escapeHTML(s.text)+'</textarea><input class="notes" placeholder="Movimento / transição / notas" value="'+escapeHTML(s.notes||'')+'"><div class="controls"><label>Duração <input type="number" min="0.5" max="60" step="0.5" value="'+s.duration+'"></label><button data-act="up" title="Mover para cima">↑</button><button data-act="down" title="Mover para baixo">↓</button><button data-act="remove" title="Excluir cena">×</button></div></article>').join('')}function splitText(text,seconds,wpm){const words=text.trim().split(/\s+/).filter(Boolean);if(!words.length)return[];const target=Math.max(3,Math.round(seconds*wpm/60));let chunks=[],buffer=[];for(const word of words){buffer.push(word);if(buffer.length>=target&&(/[.!?;:]$/.test(word)||buffer.length>=target+3)){chunks.push(buffer.join(' '));buffer=[]}}if(buffer.length){if(chunks.length&&buffer.length<3)chunks[chunks.length-1]+=' '+buffer.join(' ');else chunks.push(buffer.join(' '))}return chunks.map(t=>({id:uid(),text:t,duration:seconds,notes:'',image:null}))}function download(blob,name){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.append(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove()},1000)}$('newProject').onclick=()=>{const p={id:uid(),title:'Novo vídeo',script:'',seconds:3,wpm:140,scenes:[]};projects.unshift(p);selected=p.id;save();render()};$('projects').onclick=e=>{const b=e.target.closest('[data-id]');if(b){selected=b.dataset.id;render()}};$('projectTitle').oninput=e=>{current().title=e.target.value;save();$('projects').querySelector('.active').textContent=e.target.value};$('script').oninput=e=>{current().script=e.target.value;save()};$('seconds').onchange=e=>{current().seconds=Math.max(1,Number(e.target.value)||3);save()};$('wpm').onchange=e=>{current().wpm=Math.max(60,Number(e.target.value)||140);save()};$('split').onclick=()=>{const p=current();if(p.scenes.length&&!confirm('Substituir cenas existentes? As imagens associadas a elas serão removidas.'))return;p.scenes=splitText(p.script,Number(p.seconds),Number(p.wpm));save();renderScenes()};$('deleteProject').onclick=()=>{if(!confirm('Excluir este projeto deste navegador?'))return;projects=projects.filter(p=>p.id!==selected);selected=projects[0]?.id||null;save();render()};$('scenes').addEventListener('input',e=>{const card=e.target.closest('.scene');if(!card)return;const s=current().scenes[Number(card.dataset.index)];if(e.target.tagName==='TEXTAREA')s.text=e.target.value;else if(e.target.classList.contains('notes'))s.notes=e.target.value;else if(e.target.type==='number')s.duration=Math.max(.5,Number(e.target.value)||3);save()});$('scenes').addEventListener('change',e=>{if(e.target.type!=='file')return;const file=e.target.files[0];if(!file)return;if(!file.type.startsWith('image/')){alert('Selecione uma imagem ou GIF.');return}const i=Number(e.target.closest('.scene').dataset.index),reader=new FileReader();reader.onload=()=>{current().scenes[i].image=reader.result;save();renderScenes()};reader.readAsDataURL(file)});$('scenes').addEventListener('click',e=>{const b=e.target.closest('[data-act]');if(!b)return;const p=current(),i=Number(b.closest('.scene').dataset.index),act=b.dataset.act;if(act==='remove')p.scenes.splice(i,1);if(act==='up'&&i>0)[p.scenes[i-1],p.scenes[i]]=[p.scenes[i],p.scenes[i-1]];if(act==='down'&&i<p.scenes.length-1)[p.scenes[i+1],p.scenes[i]]=[p.scenes[i],p.scenes[i+1]];save();renderScenes()});$('export').onclick=async()=>{const p=current();if(!p)return;if(typeof JSZip==='undefined'){alert('A biblioteca de ZIP não carregou. Verifique a conexão com a internet.');return}const zip=new JSZip(),assets=zip.folder('imagens'),scenes=p.scenes.map((s,i)=>{const item={numero:i+1,inicio_segundos:p.scenes.slice(0,i).reduce((a,x)=>a+Number(x.duration),0),duracao_segundos:Number(s.duration),texto:s.text,instrucoes:s.notes||'',imagem:null};if(s.image){const m=s.image.match(/^data:(image\/[^;]+);base64,(.*)$/);if(m){const ext=({'image/jpeg':'jpg','image/png':'png','image/gif':'gif','image/webp':'webp','image/avif':'avif'})[m[1]]||'png';item.imagem='imagens/cena-'+String(i+1).padStart(3,'0')+'.'+ext;assets.file(item.imagem.split('/')[1],m[2],{base64:true})}}return item});zip.file('projeto.json',JSON.stringify({nome:p.title,formato:'9:16',cenas:scenes},null,2));zip.file('roteiro.txt',p.script);if(narrationData&&narrationProject===p.id){const m=narrationData.match(/^data:([^;]+);base64,(.*)$/);if(m){const ext=narrationName.split('.').pop().replace(/[^a-z0-9]/gi,'')||'mp3';zip.file('narracao.'+ext,m[2],{base64:true})}}zip.file('INSTRUCOES_PARA_IA.md','# Montagem do vídeo — '+p.title+'\n\nMonte um vídeo vertical 9:16 usando as imagens da pasta imagens e os tempos e textos em projeto.json. Respeite a ordem, duração e instruções de cada cena. Não invente imagens ausentes. Use transições discretas quando não houver instrução. Entregue MP4 H.264, 1080x1920. Caso não haja áudio, solicite a narração ou crie uma montagem silenciosa.\n');const blob=await zip.generateAsync({type:'blob'});download(blob,(p.title.replace(/[^a-z0-9_-]/gi,'-')||'videoedit')+'.zip')};selected=projects[0]?.id||null;render();

/* Prévia temporizada das imagens e legendas */
let previewTime=0,previewPlaying=false,previewFrame=0,previewLast=0,previewProjectId=null;
const previewDuration=()=>current()?.scenes.reduce((sum,s)=>sum+Math.max(.5,Number(s.duration)||3),0)||0;
const clock=t=>{const n=Math.floor(Math.max(0,t));return String(Math.floor(n/60)).padStart(2,'0')+':'+String(n%60).padStart(2,'0')};
function updatePreview(){
 const p=current(),scenes=p?.scenes||[],total=previewDuration();
 if(previewProjectId!==selected){previewProjectId=selected;previewTime=0;previewPlaying=false}
 if(previewTime>total)previewTime=total;
 let index=0,elapsed=0;
 for(let i=0;i<scenes.length;i++){const duration=Math.max(.5,Number(scenes[i].duration)||3);if(previewTime<elapsed+duration||i===scenes.length-1){index=i;break}elapsed+=duration}
 const scene=scenes[index],img=$('playerImage'),placeholder=$('playerPlaceholder'),caption=$('playerCaption');
 if(scene?.image){if(img.src!==scene.image)img.src=scene.image;img.hidden=false;placeholder.hidden=true}
 else{img.hidden=true;img.removeAttribute('src');placeholder.hidden=false;placeholder.textContent=scene?'Cena '+(index+1)+' — sem imagem':'Adicione imagens às cenas para visualizar o vídeo'}
 caption.textContent=scene?.text||'';
 caption.hidden=!$('showCaptions').checked||!scene;
 $('playerScene').textContent=scene?'Cena '+(index+1)+' de '+scenes.length:'Nenhuma cena';
 $('playerClock').textContent=clock(previewTime)+' / '+clock(total);
 $('playerSeek').value=total?Math.round(previewTime/total*1000):0;
 $('playerPlay').textContent=previewPlaying?'❚❚ Pausar':'▶ Reproduzir';
 $('playerPlay').disabled=!scenes.length;
 $('playerPrev').disabled=!scenes.length;
 $('playerNext').disabled=!scenes.length;
}
function stopPreview(){previewPlaying=false;previewLast=0;cancelAnimationFrame(previewFrame);updatePreview()}
function previewTick(timestamp){if(!previewPlaying)return;if(previewLast)previewTime+=(timestamp-previewLast)/1000;previewLast=timestamp;const total=previewDuration();if(previewTime>=total){previewTime=total;previewPlaying=false}updatePreview();if(previewPlaying)previewFrame=requestAnimationFrame(previewTick)}
$('playerPlay').onclick=()=>{if(previewPlaying){stopPreview();return}if(previewTime>=previewDuration())previewTime=0;previewPlaying=true;previewLast=0;previewFrame=requestAnimationFrame(previewTick);updatePreview()};
$('playerSeek').oninput=e=>{previewTime=previewDuration()*Number(e.target.value)/1000;previewLast=0;updatePreview()};
$('showCaptions').onchange=updatePreview;
function skipPreview(direction){const scenes=current()?.scenes||[];if(!scenes.length)return;let starts=[],t=0;for(const s of scenes){starts.push(t);t+=Math.max(.5,Number(s.duration)||3)}if(direction>0){previewTime=starts.find(start=>start>previewTime+.05)??starts[starts.length-1]}else{previewTime=[...starts].reverse().find(start=>start<previewTime-.1)??0}previewLast=0;updatePreview()}
$('playerPrev').onclick=()=>skipPreview(-1);
$('playerNext').onclick=()=>skipPreview(1);
const originalRender=render;render=function(){stopPreview();originalRender();updatePreview()};
const originalRenderScenes=renderScenes;renderScenes=function(){originalRenderScenes();updatePreview()};
$('projects').addEventListener('click',()=>{previewTime=0;stopPreview()});
$('newProject').addEventListener('click',()=>{previewTime=0;stopPreview()});
$('split').addEventListener('click',()=>{previewTime=0;stopPreview()});
$('scenes').addEventListener('input',updatePreview);
$('scenes').addEventListener('change',()=>setTimeout(updatePreview,50));
$('scenes').addEventListener('click',()=>setTimeout(updatePreview,0));
document.addEventListener('visibilitychange',()=>{if(document.hidden&&previewPlaying)stopPreview()});
updatePreview();


/* Organização livre: imagens em lote, roteiro preservado */
$('bulkImages').addEventListener('change',async e=>{
 const p=current(),files=Array.from(e.target.files||[]).filter(f=>f.type.startsWith('image/'));if(!p||!files.length)return;
 const images=await Promise.all(files.map(file=>new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result);reader.onerror=reject;reader.readAsDataURL(file)})));
 for(const image of images)p.scenes.push({id:uid(),text:'',duration:Number(p.seconds)||3,notes:'',image});
 save();renderScenes();e.target.value='';$('notice').textContent=images.length+' imagens adicionadas. Arraste para organizar a ordem.';
});
let dragScene=null;
$('scenes').addEventListener('dragstart',e=>{const card=e.target.closest('.scene');if(!card)return;dragScene=Number(card.dataset.index);card.classList.add('dragging');e.dataTransfer.effectAllowed='move'});
$('scenes').addEventListener('dragover',e=>{if(dragScene===null)return;e.preventDefault();e.dataTransfer.dropEffect='move'});
$('scenes').addEventListener('drop',e=>{e.preventDefault();const target=e.target.closest('.scene');if(!target||dragScene===null)return;const to=Number(target.dataset.index),p=current();if(dragScene!==to){const [item]=p.scenes.splice(dragScene,1);p.scenes.splice(to,0,item);save();renderScenes()}dragScene=null});
$('scenes').addEventListener('dragend',()=>{dragScene=null;document.querySelectorAll('.dragging').forEach(el=>el.classList.remove('dragging'))});
const sceneCards=renderScenes;
renderScenes=function(){sceneCards();document.querySelectorAll('#scenes .scene').forEach(card=>{card.draggable=true;card.title='Arraste este cartão para mudar a ordem das imagens';const textarea=card.querySelector('textarea');if(textarea)textarea.placeholder='Legenda opcional (não altera o roteiro original)'});updatePreview()};
renderScenes();

/* Narração para escuta e exportação: mantida nesta sessão */
let narrationData=null,narrationName='',narrationProject=null;
const audioEl=$('narrationAudio');
function syncAudioUI(){const valid=narrationData&&narrationProject===selected;$('audioName').textContent=valid?narrationName:'Narração não carregada nesta sessão';audioEl.hidden=!valid;if(!valid){audioEl.pause();audioEl.removeAttribute('src');audioEl.load()}else if(audioEl.src!==narrationData){audioEl.src=narrationData}}
$('narrationFile').addEventListener('change',e=>{const file=e.target.files?.[0];if(!file)return;if(!file.type.startsWith('audio/')&&!/\.(mp3|wav|m4a)$/i.test(file.name)){alert('Escolha um arquivo de áudio.');return}const reader=new FileReader();reader.onload=()=>{narrationData=reader.result;narrationName=file.name;narrationProject=selected;syncAudioUI();$('notice').textContent='Narração carregada. Ela será incluída no ZIP se você exportar agora.'};reader.readAsDataURL(file)});
$('projects').addEventListener('click',syncAudioUI);
$('newProject').addEventListener('click',syncAudioUI);
$('playerPlay').addEventListener('click',()=>{if(narrationProject!==selected||!narrationData)return;if(previewPlaying){audioEl.currentTime=Math.min(previewTime,audioEl.duration||previewTime);audioEl.play().catch(()=>{})}else audioEl.pause()});
$('playerSeek').addEventListener('input',()=>{if(narrationProject===selected&&narrationData&&Number.isFinite(audioEl.duration))audioEl.currentTime=Math.min(previewTime,audioEl.duration)});
$('playerPrev').addEventListener('click',()=>{if(narrationProject===selected&&narrationData&&Number.isFinite(audioEl.duration))audioEl.currentTime=Math.min(previewTime,audioEl.duration)});
$('playerNext').addEventListener('click',()=>{if(narrationProject===selected&&narrationData&&Number.isFinite(audioEl.duration))audioEl.currentTime=Math.min(previewTime,audioEl.duration)});
audioEl.addEventListener('pause',()=>{});
syncAudioUI();
