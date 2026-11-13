(() => {
  'use strict';
  const roots=document.querySelectorAll('#ss-directory');
  const root=roots.length?roots[roots.length-1]:null;
  if(!root || root.dataset.initialized==='1') return;
  root.dataset.initialized='1';
  const keys={
    fav:'ss-veiculos:favs:v3',recent:'ss-veiculos:recent:v3',
    oldFav:'ss-veiculos:favs:v2',oldRecent:'ss-veiculos:recent:v2',
    only:'ss-veiculos:only-favs:v2'
  };
  const memory=window.__ssVeiculosMemory||(window.__ssVeiculosMemory={});
  const json=(s,fallback)=>{try {return s===null?fallback:JSON.parse(s);}catch(e){return fallback;}};
  function readLocal(key,oldKey,fallback){
    try {
      const current=localStorage.getItem(key);
      if(current!==null) return json(current,fallback);
    }catch(e){}
    let old=null;
    try {old=sessionStorage.getItem(oldKey);}catch(e){}
    if(old!==null){
      const value=json(old,fallback);
      saveLocal(key,value);
      return value;
    }
    return key in memory?memory[key]:fallback;
  }
  function saveLocal(key,value){
    memory[key]=value;
    try {localStorage.setItem(key,JSON.stringify(value));}
    catch(e){try{sessionStorage.setItem(key,JSON.stringify(value));}catch(e2){}}
  }
  function readTab(key,fallback){
    try{return json(sessionStorage.getItem(key),fallback);}
    catch(e){return key in memory?memory[key]:fallback;}
  }
  function saveTab(key,value){
    memory[key]=value;
    try{sessionStorage.setItem(key,JSON.stringify(value));}catch(e){}
  }
  const validUrl=url=>{
    if(typeof url!=='string')return false;
    try{
      const u=new URL(url);
      return u.protocol==='https:' && u.hostname==='ssveiculos.ssinformatica.net'
        && !u.port && u.pathname!=='/' && !u.username && !u.password;
    }catch(e){return false;}
  };
  const favorites=()=>new Set(
    (Array.isArray(readLocal(keys.fav,keys.oldFav,[]))?readLocal(keys.fav,keys.oldFav,[]):[])
    .filter(x=>typeof x==='string').slice(0,400)
  );
  const cards=()=>Array.from(root.querySelectorAll('.ss-card'));
  const toast=root.querySelector('.ss-toast');
  let onlyFavorites=Boolean(readTab(keys.only,false));
  function notify(message){
    if(!toast)return;
    toast.textContent=message;toast.style.display='block';
    clearTimeout(root.__ssToastTimeout);
    root.__ssToastTimeout=setTimeout(()=>{toast.style.display='none';},1800);
  }
  function resultText(count){
    const label=root.dataset.searchLabel||'';
    const unit=label?(count===1?'resultado':'resultados'):(count===1?'entidade exibida':'entidades exibidas');
    return count+' '+unit+(label?' para “'+label+'”':'');
  }
  function refreshFavorites(){
    const fav=favorites();
    const toggle=root.querySelector('[data-action="favorites-filter"]');
    if(toggle){
      toggle.setAttribute('aria-pressed',String(onlyFavorites));
      toggle.textContent=(onlyFavorites?'★ Exibir todas':'☆ Meus favoritos')+' ('+fav.size+')';
    }
    let count=0;
    cards().forEach(card=>{
      const selected=fav.has(card.dataset.key);
      card.classList.toggle('ss-card--favorite',selected);
      const button=card.querySelector('[data-action="favorite"]');
      if(button){
        button.textContent=selected?'★':'☆';
        button.setAttribute('aria-pressed',String(selected));
        const title=card.querySelector('.ss-card-title')?.textContent||'entidade';
        button.setAttribute('aria-label',(selected?'Remover dos favoritos: ':'Favoritar: ')+title);
        button.title=selected?'Remover favorito':'Favoritar';
      }
      const hidden=onlyFavorites&&!selected;
      card.classList.toggle('ss-hidden',hidden);
      if(!hidden)count++;
    });
    root.querySelectorAll('.ss-group').forEach(group=>{
      const visible=group.querySelectorAll('.ss-card:not(.ss-hidden)').length;
      group.classList.toggle('ss-hidden',visible===0);
      const slots=Math.max(1,Math.min(visible,5));
      for(let k=1;k<=5;k++) group.classList.toggle('ss-group--size-'+k,k===slots);
      const el=group.querySelector('.ss-group-title small');
      if(el)el.textContent='('+visible+' '+(visible===1?'entidade':'entidades')+')';
    });
    const empty=root.querySelector('[data-fav-empty]');
    if(empty)empty.classList.toggle('ss-hidden',!onlyFavorites || count>0);
    const counter=root.querySelector('[data-result-count]');
    if(counter)counter.textContent=resultText(count);
  }
  function recentItems(){
    const r=readLocal(keys.recent,keys.oldRecent,[]);
    return Array.isArray(r)?r.filter(item=>item&&validUrl(item.url)&&
      typeof item.name==='string'&&typeof item.key==='string').slice(0,6):[];
  }
  function refreshRecents(){
    const bar=root.querySelector('.ss-recent'),links=root.querySelector('.ss-recent-links');
    if(!bar||!links)return;
    const items=recentItems();
    links.replaceChildren();
    items.forEach(item=>{
      const a=document.createElement('a');
      a.className='ss-recent-link';
      a.href=item.url;a.target='_blank';a.rel='noopener noreferrer';
      a.textContent=item.name;a.title=item.name;
      a.dataset.action='recent-open';a.dataset.key=item.key;
      links.appendChild(a);
    });
    bar.style.display=items.length?'flex':'none';
  }
  function recordAccess(name,url,key){
    if(!validUrl(url)||!key)return;
    const items=[{name,url,key},...recentItems().filter(i=>i.key!==key)].slice(0,6);
    saveLocal(keys.recent,items);
    refreshRecents();
  }
  function showCopyFeedback(control){
    const feedback=control.parentElement?.querySelector('.ss-copy-feedback');
    if(!feedback){notify('Link copiado.');return;}
    feedback.textContent='Link copiado';
    feedback.classList.add('is-visible');
    clearTimeout(feedback.__ssDelay);
    feedback.__ssDelay=setTimeout(()=>feedback.classList.remove('is-visible'),1650);
  }
  root.addEventListener('click',async event=>{
    const control=event.target.closest('[data-action]');
    if(!control||!root.contains(control))return;
    const action=control.dataset.action;
    if(action==='favorite'){
      const f=favorites(),id=control.dataset.key;
      f.has(id)?f.delete(id):f.add(id);
      saveLocal(keys.fav,[...f]);refreshFavorites();
    }else if(action==='favorites-filter'){
      onlyFavorites=!onlyFavorites;
      saveTab(keys.only,onlyFavorites);refreshFavorites();
    }else if(action==='copy'){
      try{
        await navigator.clipboard.writeText(control.dataset.url);
        showCopyFeedback(control);
      }catch(e){window.prompt('Copie o endereço:',control.dataset.url);}
    }else if(action==='open'){
      recordAccess(control.dataset.name,control.dataset.url,control.dataset.key);
    }else if(action==='recent-open'){
      recordAccess(control.textContent,control.href,control.dataset.key);
    }else if(action==='back-top'){
      const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const options={top:0,behavior:reduce?'auto':'smooth'};
      window.scrollTo(options);
      for(const selector of ['[data-testid="stAppViewContainer"]','[data-testid="stMain"]']){
        const host=document.querySelector(selector);
        if(host&&typeof host.scrollTo==='function')host.scrollTo(options);
      }
    }
  });
  if(!window.__ssVeiculosShortcutInstalled){
    document.addEventListener('keydown',event=>{
      if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){
        const input=document.querySelector('input[type="search"]');
        if(input){event.preventDefault();input.focus();input.select();}
      }
    });
    window.__ssVeiculosShortcutInstalled=true;
  }
  const scrollTargets=['[data-testid="stAppViewContainer"]','[data-testid="stMain"]'];
  const getScroll=()=>{
    const scroll=[window.scrollY||0,document.documentElement.scrollTop||0];
    scrollTargets.forEach(selector=>{
      const host=document.querySelector(selector);
      if(host)scroll.push(host.scrollTop||0);
    });
    return Math.max(...scroll);
  };
  function updateBackTop(){
    const visible=getScroll()>340;
    document.querySelectorAll('.ss-back-top').forEach(button=>{
      button.classList.toggle('is-visible',visible);
      button.tabIndex=visible?0:-1;
      button.setAttribute('aria-hidden',String(!visible));
    });
  }
  window.__ssVeiculosUpdateBackTop=updateBackTop;
  if(!window.__ssVeiculosBackTopInstalled){
    const handler=()=>window.__ssVeiculosUpdateBackTop?.();
    window.addEventListener('scroll',handler,{passive:true});
    scrollTargets.forEach(selector=>{
      const node=document.querySelector(selector);
      if(node)node.addEventListener('scroll',handler,{passive:true});
    });
    window.__ssVeiculosBackTopInstalled=true;
  }
  if(!window.__ssVeiculosStorageListener){
    window.addEventListener('storage',event=>{
      if(event.key===keys.fav||event.key===keys.recent){
        const nodes=document.querySelectorAll('#ss-directory');
        const current=nodes[nodes.length-1];
        if(current)window.__ssVeiculosStorageRefresh?.();
      }
    });
    window.__ssVeiculosStorageListener=true;
  }
  window.__ssVeiculosStorageRefresh=()=>{refreshFavorites();refreshRecents();};
  refreshFavorites();refreshRecents();updateBackTop();
})();
