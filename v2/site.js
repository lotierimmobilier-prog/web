// Mouvements discrets : apparition au défilement, ombre de l'en-tête. Sans effet si "réduire les animations".
(function () {
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var top = document.querySelector('.top');
  if (top) {
    var onScroll = function () { top.classList.toggle('scrolled', window.scrollY > 8); };
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }
  if (reduce || !('IntersectionObserver' in window)) return;
  document.documentElement.classList.add('js-reveal');
  var SEL = '.hero > *, .wrap > h1, .wrap > h2, .cities li, .tile, .miss li, .zones li, .actu, details, .filtres, .search, .bien-carte, .id, .embed, .contact';
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  var seen = new WeakSet();
  function scan(root) {
    root.querySelectorAll(SEL).forEach(function (el, i) {
      if (seen.has(el)) return; seen.add(el);
      el.classList.add('reveal');
      el.style.transitionDelay = Math.min(i % 6, 5) * 60 + 'ms';
      io.observe(el);
    });
  }
  scan(document);
  new MutationObserver(function () { scan(document); }).observe(document.body, { childList: true, subtree: true });
})();
