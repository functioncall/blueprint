(function(){
  "use strict";
  var pop = document.getElementById('pop');
  function esc(s){ return (s||'').replace(/[&<>"]/g, function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

  // ── scenario switcher (dropdown in the header) ──────────────────────────────
  var cards     = Array.prototype.slice.call(document.querySelectorAll('.card'));
  var mitems    = Array.prototype.slice.call(document.querySelectorAll('.mitem'));
  var menu      = document.getElementById('switchMenu');
  var switchBtn = document.getElementById('switchBtn');
  var crumbTitle= document.getElementById('crumbTitle');
  var barCount  = document.getElementById('barCount');

  function closeMenu(){ if(menu){ menu.hidden = true; } if(switchBtn){ switchBtn.setAttribute('aria-expanded','false'); } }
  function select(sid){
    var card = null;
    cards.forEach(function(c){ var on = c.dataset.card === sid; c.classList.toggle('active', on); if(on) card = c; });
    mitems.forEach(function(m){ m.classList.toggle('active', m.dataset.target === sid); });
    if(card && crumbTitle) crumbTitle.textContent = card.dataset.title || '';
    closeMenu(); pop.hidden = true;
  }
  mitems.forEach(function(m){
    m.addEventListener('click', function(e){ e.stopPropagation(); select(m.dataset.target); });
  });

  if(barCount) barCount.textContent = cards.length + (cards.length === 1 ? ' scenario' : ' scenarios');
  var act = document.querySelector('.card.active') || cards[0];
  if(act) select(act.dataset.card);

  // open/close the dropdown
  if(switchBtn && menu && mitems.length){
    switchBtn.addEventListener('click', function(e){
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      switchBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', closeMenu);
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeMenu(); });
  }

  // keyboard: ↑/↓ or j/k to cycle scenarios
  document.addEventListener('keydown', function(e){
    if(cards.length < 2) return;
    if(e.target && /^(INPUT|TEXTAREA)$/.test(e.target.tagName)) return;
    var dir = (e.key === 'ArrowDown' || e.key === 'j') ? 1
            : (e.key === 'ArrowUp'   || e.key === 'k') ? -1 : 0;
    if(!dir) return;
    var ai = cards.findIndex(function(c){ return c.classList.contains('active'); });
    var nx = Math.max(0, Math.min(cards.length - 1, (ai < 0 ? 0 : ai) + dir));
    select(cards[nx].dataset.card); e.preventDefault();
  });

  // ── colour lens (per card; one active at a time) ──────────────────────────
  function setLens(card, lens){
    var dia = card.querySelector('.diagram');
    dia.className = 'diagram';
    card.querySelectorAll('.msg.lit').forEach(function(m){ m.classList.remove('lit'); });
    card.querySelectorAll('.legend').forEach(function(l){ l.hidden = true; });
    var lg;
    if(lens === 'none'){ dia.classList.add('lens-none'); lg = card.querySelector('.lg-none'); }
    else if(lens.indexOf('path-') === 0){
      dia.classList.add('lens-path');
      card.querySelectorAll('.msg.p-' + lens.slice(5)).forEach(function(m){ m.classList.add('lit'); });
      lg = card.querySelector('.lg-' + lens);
    }
    else if(lens === 'cost'){ dia.classList.add('lens-cost'); lg = card.querySelector('.lg-cost'); }
    else if(lens === 'lat'){ dia.classList.add('lens-lat'); lg = card.querySelector('.lg-lat'); }
    if(lg) lg.hidden = false;
    card.querySelectorAll('.lens').forEach(function(b){ b.classList.toggle('on', b.dataset.lens === lens); });
  }

  // ── in-browser PNG export — stitch header + body SVGs onto one canvas ──────
  function svgImg(svg){
    return new Promise(function(res){
      var img = new Image();
      img.onload = function(){ res(img); };
      img.src = 'data:image/svg+xml;charset=utf-8,' +
                encodeURIComponent(new XMLSerializer().serializeToString(svg));
    });
  }
  function exportPNG(card){
    var hs = card.querySelector('.head svg'), bs = card.querySelector('.scroll svg');
    var W = +hs.getAttribute('width'), HH = +hs.getAttribute('height'), BH = +bs.getAttribute('height');
    var sc = 2, cv = document.createElement('canvas');
    cv.width = W * sc; cv.height = (HH + BH) * sc;
    var cx = cv.getContext('2d'); cx.scale(sc, sc);
    Promise.all([svgImg(hs), svgImg(bs)]).then(function(imgs){
      cx.drawImage(imgs[0], 0, 0);
      cx.drawImage(imgs[1], 0, HH);
      var a = document.createElement('a');
      a.download = (card.dataset.card || 'diagram') + '.png';
      a.href = cv.toDataURL('image/png'); a.click();
    });
  }

  // ── wire each card (lenses, export, hover-dim) ─────────────────────────────
  cards.forEach(function(card){
    var pngBtn = card.querySelector('.png');
    if(pngBtn) pngBtn.addEventListener('click', function(){ exportPNG(card); });
    card.querySelectorAll('.lens').forEach(function(b){
      b.addEventListener('click', function(){ setLens(card, b.dataset.lens); });
    });
    var dia = card.querySelector('.diagram');
    dia.addEventListener('mouseover', function(e){
      var g = e.target.closest('.msg'); if(g){ dia.classList.add('hov'); g.classList.add('hl'); }
    });
    dia.addEventListener('mouseout', function(e){
      var g = e.target.closest('.msg');
      if(g){ g.classList.remove('hl'); if(!dia.querySelector('.msg.hl')) dia.classList.remove('hov'); }
    });
  });

  // ── click-a-message detail popover ─────────────────────────────────────────
  document.addEventListener('click', function(e){
    var g = e.target.closest('.msg');
    if(!g){ pop.hidden = true; return; }
    var full = g.dataset.full;
    var h = '<b>' + esc(full || '(message)') + '</b>';
    if(g.dataset.metrics) h += '<div class="k">' + esc(g.dataset.metrics) + '</div>';
    if(g.dataset.src) h += '<div class="k">' + esc(g.dataset.src) + '</div>';
    pop.innerHTML = h; pop.hidden = false;
    var x = Math.min(e.clientX + 12, innerWidth - pop.offsetWidth - 8);
    var y = Math.min(e.clientY + 12, innerHeight - pop.offsetHeight - 8);
    pop.style.left = x + 'px'; pop.style.top = y + 'px';
  });
})();
