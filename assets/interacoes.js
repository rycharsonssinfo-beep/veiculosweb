(() => {
  'use strict';
  const roots = document.querySelectorAll('#ss-directory');
  const root = roots.length ? roots[roots.length - 1] : null;
  if (!root || root.dataset.initialized === '1') return;
  root.dataset.initialized = '1';
  const keys = {fav:'ss-veiculos:favs:v2',recent:'ss-veiculos:recent:v2',only:'ss-veiculos:only-favs:v2'};
  const memory = window.__ssVeiculosMemory || (window.__ssVeiculosMemory={});
  const read = (key, fallback) => {
    try { const raw = window.sessionStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; }
    catch (e) { return key in memory ? memory[key] : fallback; }
  };
  const save = (key, value) => {
    memory[key] = value;
    try { window.sessionStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  };
  const getFavorites = () => new Set(read(keys.fav, []));
  const cardList = () => Array.from(root.querySelectorAll('.ss-card'));
  let onlyFavorites = Boolean(read(keys.only, false));
  const toast = root.querySelector('.ss-toast');
  const notify = (message) => {
    toast.textContent = message; toast.style.display='block';
    clearTimeout(root.__ssToastTimeout);
    root.__ssToastTimeout = setTimeout(() => {toast.style.display='none'}, 2400);
  };
  function refreshFavorites() {
    const favorites = getFavorites();
    const toggle = root.querySelector('[data-action="favorites-filter"]');
    toggle.setAttribute('aria-pressed', String(onlyFavorites));
    toggle.textContent = (onlyFavorites ? '★ Exibir todas' : '☆ Meus favoritos') + ' ('+favorites.size+')';
    let visible = 0;
    cardList().forEach(card => {
      const selected = favorites.has(card.dataset.key);
      const button = card.querySelector('[data-action="favorite"]');
      if (button) {
        button.textContent = selected ? '★' : '☆';
        button.setAttribute('aria-pressed', String(selected));
        button.setAttribute('aria-label', (selected?'Remover dos favoritos: ':'Favoritar: ')+card.querySelector('.ss-card-title').textContent);
        button.title = selected?'Remover favorito':'Favoritar';
      }
      const hide = onlyFavorites && !selected;
      card.classList.toggle('ss-hidden',hide);
      if (!hide) visible++;
    });
    root.querySelectorAll('.ss-group').forEach(group => {
      group.classList.toggle('ss-hidden', !group.querySelector('.ss-card:not(.ss-hidden)'));
    });
    const empty = root.querySelector('[data-fav-empty]');
    if (empty) empty.classList.toggle('ss-hidden', visible > 0);
    const count = root.querySelector('[data-result-count]');
    if (count) count.textContent = visible+' '+(visible===1?'entidade exibida':'entidades exibidas');
  }
  function recordAccess(name,url,key) {
    if (!url || !url.startsWith('https://ssveiculos.ssinformatica.net/')) return;
    const previous = read(keys.recent, []);
    const history = [{name,url,key},...previous.filter(item => item.key !== key)].slice(0,6);
    save(keys.recent,history);
    refreshRecents();
  }
  function refreshRecents() {
    const items = read(keys.recent, []);
    const bar = root.querySelector('.ss-recent');
    const container = root.querySelector('.ss-recent-links');
    container.replaceChildren();
    bar.style.display = items.length ? 'block':'none';
    items.forEach(item => {
      if (!item.url || !item.url.startsWith('https://ssveiculos.ssinformatica.net/')) return;
      const link = document.createElement('a');
      link.className = 'ss-recent-link';
      link.href=item.url; link.target='_blank'; link.rel='noopener noreferrer';
      link.textContent=item.name; link.title=item.name;
      link.dataset.action='recent-open';link.dataset.key=item.key;
      container.appendChild(link);
    });
  }
  root.addEventListener('click', async (event) => {
    const control = event.target.closest('[data-action]');
    if (!control || !root.contains(control)) return;
    const action=control.dataset.action;
    if(action==='favorite'){
      const fav=getFavorites();
      fav.has(control.dataset.key)?fav.delete(control.dataset.key):fav.add(control.dataset.key);
      save(keys.fav,[...fav]); refreshFavorites();
    }
    if(action==='favorites-filter'){
      onlyFavorites=!onlyFavorites;
      save(keys.only,onlyFavorites); refreshFavorites();
    }
    if(action==='copy'){
      try {await navigator.clipboard.writeText(control.dataset.url);notify('Link copiado.');}
      catch (e) { window.prompt('Copie o endereço:',control.dataset.url); }
    }
    if(action==='open'){
      recordAccess(control.dataset.name,control.dataset.url,control.dataset.key);
    }
    if(action==='recent-open'){
      recordAccess(control.textContent,control.href,control.dataset.key);
    }
  });
  if (!window.__ssVeiculosShortcutInstalled) {
    document.addEventListener('keydown', (event) => {
      if ((event.ctrlKey||event.metaKey) && event.key.toLowerCase()==='k') {
        const input=document.querySelector('input[type="search"]');
        if (input) {event.preventDefault(); input.focus(); input.select();}
      }
    });
    window.__ssVeiculosShortcutInstalled=true;
  }
  refreshFavorites(); refreshRecents();
})();
