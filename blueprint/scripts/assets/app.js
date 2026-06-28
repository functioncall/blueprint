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

  // ── click-a-message detail card ────────────────────────────────────────────
  // Tiers: WHY headline · readable route/step/phase sub-line · guard · prose body
  // (what-changes / on-failure) · fact chips (sends/auth/ordering/cost) · src+age footer.
  // Header + footer are deterministic; the body shows only the AI `detail` keys present.
  function row(label, val){
    return '<div class="p-row"><span class="pl">' + esc(label) + '</span><span>' + esc(val) + '</span></div>';
  }
  function chip(val){ return '<span class="chip">' + esc(val) + '</span>'; }
  function buildCard(g){
    var d = g.dataset, h = '';
    // headline = the WHY; with no detail, lead with the readable route (a normal arrow) or the
    // label itself (self/note, where the label is the substance) — never repeat a normal arrow's label.
    var contentLed = (d.type === 'note' || d.type === 'self');
    var head = d.why || (contentLed ? d.full : d.route) || d.full || '(message)';
    h += '<div class="p-why">' + esc(head) + '</div>';
    var sub = [];
    if(d.route && d.route !== head) sub.push(d.route);
    if(d.step)  sub.push('step ' + d.step);
    if(d.phase) sub.push(d.phase);
    if(sub.length) h += '<div class="p-route">' + esc(sub.join('  ·  ')) + '</div>';
    if(d.frag) h += '<div class="p-guard">⋔ ' + esc(d.frag) + '</div>';
    var body = '';
    if(d.effects) body += row('Changes', d.effects);
    if(d.fails)   body += row('On fail', d.fails);
    if(body) h += '<div class="p-body">' + body + '</div>';
    var chips = '';
    if(d.sends)    chips += chip(d.sends);
    if(d.auth)     chips += chip(d.auth);
    if(d.ordering) chips += chip(d.ordering);
    if(d.metrics)  chips += chip(d.metrics);
    if(chips) h += '<div class="p-chips">' + chips + '</div>';
    var foot = [];
    if(d.src) foot.push(d.src);
    var card = g.closest('.card'), age = card && card.dataset.updated;
    if(age) foot.push(age);                                   // research age → staleness + AI-derived signal
    if(foot.length) h += '<div class="p-foot">' + esc(foot.join('  ·  ')) + '</div>';
    return h;
  }
  document.addEventListener('click', function(e){
    if(pop.contains(e.target)) return;                        // clicks INSIDE the card never dismiss it
    var g = e.target.closest('.msg');
    if(!g){ pop.hidden = true; return; }
    pop.classList.remove('docked');
    pop.innerHTML = buildCard(g);
    pop.hidden = false;
    pop.style.left = '0px'; pop.style.top = '0px';            // measure at a known origin
    if(pop.offsetHeight > innerHeight - 24){                  // too tall to float → dock + scroll
      pop.classList.add('docked'); return;
    }
    var x = Math.max(8, Math.min(e.clientX + 12, innerWidth - pop.offsetWidth - 8));
    var y = Math.max(8, Math.min(e.clientY + 12, innerHeight - pop.offsetHeight - 8));
    pop.style.left = x + 'px'; pop.style.top = y + 'px';
  });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') pop.hidden = true; });
})();
