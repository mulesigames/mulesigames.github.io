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

// Home: the big studio logo in the hero shrinks into the header's top-left corner as the page scrolls.
(function () {
  var hero = document.querySelector(".hero-logo"), dock = document.querySelector(".brand .dock");
  if (!hero || !dock) return;
  var fly = new Image();
  fly.className = "fly-logo";
  fly.alt = "";
  fly.src = hero.currentSrc || hero.src;
  document.body.appendChild(fly);
  document.documentElement.classList.add("flying");
  var queued = false;
  function ease(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
  function frame() {
    queued = false;
    var a = hero.getBoundingClientRect(), b = dock.getBoundingClientRect();
    if (!a.width) return;
    // docked once the hero logo's middle has scrolled up to the header
    var span = Math.max(1, a.top + window.scrollY + a.height * 0.55 - b.bottom);
    var t = ease(Math.min(1, Math.max(0, window.scrollY / span)));
    var w = a.width + (b.width - a.width) * t;
    var x = a.left + (b.left - a.left) * t, y = a.top + (b.top - a.top) * t;
    fly.style.width = a.width + "px";
    fly.style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px) scale(" + (w / a.width).toFixed(4) + ")";
    fly.style.filter = t > 0.9 ? "none" : "";
  }
  function onChange() { if (!queued) { queued = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", onChange, { passive: true });
  window.addEventListener("resize", onChange);
  hero.addEventListener("load", onChange);
  // header shrinks with a transition: follow the dock while it moves
  document.querySelector(".top").addEventListener("transitionend", onChange);
  dock.addEventListener("transitionend", onChange);
  frame();
})();
