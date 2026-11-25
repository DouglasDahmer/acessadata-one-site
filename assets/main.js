/* v4.6 — cabeçalho minimalista: nenhum menu duplicado ou interação necessária.
   A árvore usa links HTML nativos e funciona sem JavaScript. */
(()=>{'use strict';
 const year=document.querySelector('[data-year]');
 if(year)year.textContent=new Date().getFullYear();
})();


/* v4.1 — Aprimoramento progressivo dos 17 nós, sem alterar a árvore original.
   Os links nativos continuam funcionando mesmo com JavaScript desativado. */
(()=>{'use strict';
 const title=document.querySelector('[data-tree-feedback-title]');
 const desc=document.querySelector('[data-tree-feedback-desc]');
 const points=Array.from(document.querySelectorAll('.tree-dot'));
 if (!points.length) return;
 const initialTitle=title?.textContent||'', initialDesc=desc?.textContent||'';
 let active=null;
 const isTreePoint=element=>element && element.classList && element.classList.contains('tree-dot');

 // Desloca a descrição dos círculos nas bordas para permanecer visível na janela.
 function fitTooltip(point){
  const tip=point.querySelector('.tree-dot-tooltip');
  if (!tip) return;
  point.style.setProperty('--tooltip-shift','0px');
  const pointRect=point.getBoundingClientRect();
  const tipWidth=tip.getBoundingClientRect().width;
  const center=pointRect.left+pointRect.width/2;
  const margin=12;
  const availableWidth=Math.max(1,window.innerWidth-2*margin);
  const width=Math.min(tipWidth,availableWidth);
  const left=Math.min(Math.max(center-tipWidth/2,margin),window.innerWidth-margin-width);
  const shift=Math.round(left-(center-tipWidth/2));
  point.style.setProperty('--tooltip-shift',`${shift}px`);
 }
 function present(point){
  point.classList.remove('is-tooltip-dismissed');
  active=point;
  fitTooltip(point);
  if(title)title.textContent=point.dataset.treeLabel||'';
  if(desc)desc.textContent=point.dataset.treeDescription||'';
 }
 function restore(point){
  if(active!==point)return;
  const focused=document.activeElement;
  if(isTreePoint(focused) && !focused.classList.contains('is-tooltip-dismissed')){
   present(focused);return;
  }
  active=null;
  if(title)title.textContent=initialTitle;
  if(desc)desc.textContent=initialDesc;
 }
 points.forEach(point=>{
  point.addEventListener('mouseenter',()=>present(point));
  point.addEventListener('focus',()=>present(point));
  point.addEventListener('mouseleave',()=>restore(point));
  point.addEventListener('blur',()=>{
   point.classList.remove('is-tooltip-dismissed');
   restore(point);
  });
  point.addEventListener('keydown',event=>{
   if(event.key==='Escape'){
    point.classList.add('is-tooltip-dismissed');
    if(active===point){active=null;if(title)title.textContent=initialTitle;if(desc)desc.textContent=initialDesc;}
    event.preventDefault();
   }
  });
 });
 window.addEventListener('resize',()=>{if(active) fitTooltip(active);},{passive:true});
})();
