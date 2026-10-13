// Language switch: the choice is remembered on this device; the first visit follows the browser.
(function () {
  function set(l) {
    document.documentElement.className = "lang-" + l;
    document.documentElement.lang = l;
    try { localStorage.setItem("lang", l); } catch (e) {}
  }
  document.querySelectorAll(".lang [data-set]").forEach(function (b) {
    b.addEventListener("click", function () { set(b.getAttribute("data-set")); });
  });
  document.querySelectorAll("[data-year]").forEach(function (e) { e.textContent = new Date().getFullYear(); });
})();
