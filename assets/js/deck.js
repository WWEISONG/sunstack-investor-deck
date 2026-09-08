/* SunStack investor deck — keyboard nav, progress rail, print helper. */
(function () {
  'use strict';

  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  if (!slides.length) return;

  var rail = document.getElementById('rail');
  var progress = document.getElementById('progress');
  var hint = document.getElementById('hint');
  var current = 0;

  /* ---- build the dot rail ---- */
  slides.forEach(function (s, i) {
    var b = document.createElement('button');
    b.type = 'button';
    b.title = (i + 1) + '. ' + (s.dataset.title || '');
    b.setAttribute('aria-label', 'Go to slide ' + (i + 1) + ': ' + (s.dataset.title || ''));
    b.addEventListener('click', function () { go(i); });
    rail.appendChild(b);
  });
  var dots = Array.prototype.slice.call(rail.children);

  function go(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    slides[i].scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function paint(i) {
    if (i === current) return;
    current = i;
    dots.forEach(function (d, j) { d.setAttribute('aria-current', j === i ? 'true' : 'false'); });
    progress.style.width = ((i + 1) / slides.length * 100) + '%';
    document.body.classList.toggle('on-dark', slides[i].classList.contains('dark'));
    if (history.replaceState) history.replaceState(null, '', '#' + slides[i].id);
  }

  /* ---- track which slide is in view ---- */
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      var best = null;
      entries.forEach(function (e) {
        if (!best || e.intersectionRatio > best.intersectionRatio) best = e;
      });
      if (best && best.isIntersecting) paint(slides.indexOf(best.target));
    }, { threshold: [0.5, 0.75] });
    slides.forEach(function (s) { io.observe(s); });
  } else {
    window.addEventListener('scroll', function () {
      var mid = window.scrollY + window.innerHeight / 2, idx = 0;
      slides.forEach(function (s, i) { if (s.offsetTop <= mid) idx = i; });
      paint(idx);
    }, { passive: true });
  }

  /* ---- keyboard ---- */
  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target;
    if (t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;

    switch (e.key) {
      case 'ArrowDown': case 'ArrowRight': case 'PageDown': case ' ':
        e.preventDefault(); go(current + 1); break;
      case 'ArrowUp': case 'ArrowLeft': case 'PageUp':
        e.preventDefault(); go(current - 1); break;
      case 'Home': e.preventDefault(); go(0); break;
      case 'End':  e.preventDefault(); go(slides.length - 1); break;
      case 'p': case 'P': e.preventDefault(); window.print(); break;
      default:
        if (/^[0-9]$/.test(e.key)) { e.preventDefault(); go(parseInt(e.key, 10) - 1); }
    }
    dismissHint();
  });

  /* ---- fade the hint away once they get it ---- */
  var hintTimer = setTimeout(dismissHint, 7000);
  function dismissHint() {
    clearTimeout(hintTimer);
    if (hint) hint.classList.add('gone');
  }
  window.addEventListener('scroll', dismissHint, { passive: true, once: true });

  /* ---- deep link on load ---- */
  paint(0);
  if (location.hash) {
    var target = document.querySelector(location.hash);
    if (target && target.classList.contains('slide')) {
      requestAnimationFrame(function () { target.scrollIntoView(); });
    }
  }
})();
