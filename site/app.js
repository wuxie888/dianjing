(function () {
  "use strict";

  var button = document.querySelector("[data-copy]");
  if (!button) return;

  button.addEventListener("click", async function () {
    var value = button.getAttribute("data-copy");
    try {
      await navigator.clipboard.writeText(value);
      button.textContent = "已复制";
      window.setTimeout(function () {
        button.textContent = "复制 clone 命令";
      }, 1800);
    } catch (_) {
      button.textContent = "请手动复制";
    }
  });
})();
