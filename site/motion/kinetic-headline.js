/* motion-anything: kinetic-headline · Apache-2.0 */
(function () {
  "use strict";
  function split(el) {
    var mode = el.getAttribute("data-kinetic") || "words";
    var text = el.textContent;
    el.textContent = "";
    var step = mode === "letters" ? 40 : 70;
    var units = mode === "letters" ? text.split("") : text.split(/(\s+)/);
    var i = 0;
    units.forEach(function (u) {
      if (u === "") return;
      if (/^\s+$/.test(u)) {
        var sp = document.createElement("span");
        sp.className = "k-space";
        el.appendChild(sp);
        return;
      }
      var s = document.createElement("span");
      s.className = "k-unit";
      s.textContent = u;
      s.style.setProperty("--k-delay", i * step + "ms");
      i++;
      el.appendChild(s);
    });
  }
  function init() {
    var els = document.querySelectorAll("[data-kinetic]");
    if (!els.length) return;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    els.forEach(function (el) {
      el.classList.add("k-anim-" + (el.getAttribute("data-kinetic-anim") || "rise"));
      split(el);
    });
    if (reduce) {
      els.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        els.forEach(function (el) { el.classList.add("is-in"); });
      });
    });
  }
  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
