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

// Scroll life: compact header, progress ball, parallax, reveal-on-scroll.
(function () {
  var root = document.documentElement;
  var top = document.querySelector(".top");
  var bar = document.createElement("div");
  bar.className = "progress";
  bar.innerHTML = "<i></i><b></b>";
  if (top) top.appendChild(bar);

  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var layers = still ? [] : Array.prototype.slice.call(document.querySelectorAll("[data-parallax]"));
  var queued = false;

  function frame() {
    queued = false;
    var y = window.scrollY, max = root.scrollHeight - window.innerHeight;
    if (top) top.classList.toggle("scrolled", y > 12);
    bar.style.setProperty("--p", max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
    layers.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var off = r.top + r.height / 2 - window.innerHeight / 2;
      el.style.setProperty("--py", (off * parseFloat(el.getAttribute("data-parallax"))).toFixed(1) + "px");
    });
  }
  function onScroll() { if (!queued) { queued = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  frame();

  var items = document.querySelectorAll("[data-reveal]");
  if (still || !items.length || !("IntersectionObserver" in window)) return;
  root.setAttribute("data-motion", "");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { rootMargin: "0px 0px -12% 0px" });
  items.forEach(function (el) { io.observe(el); });
})();
