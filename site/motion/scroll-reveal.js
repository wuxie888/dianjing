/* motion-anything: scroll-reveal · Apache-2.0 */
(function () {
  "use strict";
  function revealAll() {
    document.querySelectorAll("[data-reveal]").forEach(function (el) { el.classList.add("is-in"); });
  }
  function init() {
    var els = document.querySelectorAll("[data-reveal]");
    if (!els.length) return;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !("IntersectionObserver" in window)) {
      revealAll();
      return;
    }
    els.forEach(function (el) {
      var d = el.getAttribute("data-reveal-delay");
      if (d) el.style.setProperty("--reveal-delay", parseInt(d, 10) + "ms");
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -10% 0px" });
    els.forEach(function (el) { io.observe(el); });
  }
  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
