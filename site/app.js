(function () {
  "use strict";

  function selectProcess(name, focus) {
    var steps = document.querySelectorAll("[data-process-step]");
    var panels = document.querySelectorAll("[data-process-panel]");
    steps.forEach(function (step) {
      var active = step.getAttribute("data-process-step") === name;
      step.setAttribute("aria-pressed", active ? "true" : "false");
      if (active && focus) step.focus();
    });
    panels.forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-process-panel") !== name;
    });
  }

  document.querySelectorAll("[data-process-step]").forEach(function (step) {
    step.addEventListener("click", function () {
      selectProcess(step.getAttribute("data-process-step"), false);
    });
  });

  function selectCommand(name, focus) {
    var tabs = document.querySelectorAll("[data-command-tab]");
    var panels = document.querySelectorAll("[data-command-panel]");
    tabs.forEach(function (tab) {
      var active = tab.getAttribute("data-command-tab") === name;
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    panels.forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-command-panel") !== name;
    });
  }

  document.querySelectorAll("[data-command-tab]").forEach(function (tab) {
    tab.addEventListener("click", function () {
      selectCommand(tab.getAttribute("data-command-tab"), false);
    });
    tab.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
      event.preventDefault();
      var next = tab.getAttribute("data-command-tab") === "install" ? "audit" : "install";
      selectCommand(next, true);
    });
  });

  if (window.location.hash === "#audit") {
    selectCommand("audit", false);
  }

  document.querySelectorAll("[data-copy]").forEach(function (button) {
    button.addEventListener("click", async function () {
      var value = button.getAttribute("data-copy");
      var label = button.getAttribute("data-copy-label") || "复制命令";
      try {
        await navigator.clipboard.writeText(value);
        button.textContent = "已复制";
        window.setTimeout(function () {
          button.textContent = label;
        }, 1800);
      } catch (_) {
        button.textContent = "请手动复制";
      }
    });
  });

  window.addEventListener("hashchange", function () {
    if (window.location.hash === "#audit") {
      selectCommand("audit", false);
    }
  });
})();
