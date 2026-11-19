/* Animaciones y navegación:
   - menú con fondo al bajar y menú a pantalla completa en celular;
   - aparición de elementos al entrar en pantalla (.reveal, .title-rise);
   - escalonado de grillas (.stagger);
   - parallax del encabezado (se desactiva con "reducir movimiento");
   - año del pie. */
(function () {
  'use strict';

  // ===== Menú: fondo sólido al bajar =====
  var header = document.getElementById('siteHeader');
  // En páginas sin foto de encabezado (data-solido) el menú va siempre con fondo
  var solido = header.hasAttribute('data-solido');
  var alBajar = function () { header.classList.toggle('scrolled', solido || window.scrollY > 24); };
  alBajar();
  window.addEventListener('scroll', alBajar, { passive: true });

  // ===== Menú de celular =====
  var menuBtn = document.getElementById('menuBtn');
  var menu = document.getElementById('mobileMenu');
  var abrirMenu = function (abierto) {
    menuBtn.classList.toggle('open', abierto);
    menu.classList.toggle('open', abierto);
    header.classList.toggle('menu-abierto', abierto); // logo y X visibles sobre el menú
    menuBtn.setAttribute('aria-expanded', abierto ? 'true' : 'false');
    menuBtn.setAttribute('aria-label', abierto ? 'Cerrar menú' : 'Abrir menú');
    menu.inert = !abierto; // cerrado, sus enlaces no reciben foco
    document.body.style.overflow = abierto ? 'hidden' : '';
  };
  menuBtn.addEventListener('click', function () { abrirMenu(!menu.classList.contains('open')); });
  menu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { abrirMenu(false); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.classList.contains('open')) {
      abrirMenu(false);
      menuBtn.focus();
    }
  });

  // ===== Aparición al entrar en pantalla =====
  var alEntrar = function (elementos, margenInferior) {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px ' + margenInferior + ' 0px' });
    elementos.forEach(function (el) { io.observe(el); });
  };
  alEntrar(document.querySelectorAll('.reveal, .title-rise'), '-60px');

  // ===== Escalonado de grillas: 90 ms entre tarjetas =====
  var grupos = document.querySelectorAll('.stagger');
  grupos.forEach(function (grupo) {
    Array.prototype.forEach.call(grupo.children, function (hijo, i) {
      hijo.style.setProperty('--rd', (i * 90) + 'ms');
    });
  });
  alEntrar(grupos, '-40px');

  // ===== Parallax del encabezado (foto y texto a distinta velocidad) =====
  var fondo = document.getElementById('heroBg');
  var texto = document.querySelector('.hero .wrap');
  var reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (fondo && !reducido) {
    var pendiente = false;
    var mover = function () {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(function () {
        var sy = window.scrollY;
        var vh = window.innerHeight;
        var y = Math.min(sy, vh);
        fondo.style.transform = 'translate3d(0, ' + (y * 0.32) + 'px, 0) scale(' + (1 + y * 0.0006) + ')';
        if (texto) {
          var k = Math.max(0, 1 - sy / (vh * 0.85));
          texto.style.transform = 'translate3d(0, ' + (-y * 0.08) + 'px, 0)';
          texto.style.opacity = (0.2 + 0.8 * k).toFixed(3);
        }
        pendiente = false;
      });
    };
    window.addEventListener('scroll', mover, { passive: true });
    mover();
  }

  // ===== iOS: activa :active al tocar =====
  // Safari en iPhone no aplica :active a elementos que no son enlaces si la página no
  // escucha toques; este oyente vacío basta (lo usan las tarjetas de reservas).
  document.addEventListener('touchstart', function () {}, { passive: true });

  // ===== Año del pie =====
  var anio = document.getElementById('year');
  if (anio) anio.textContent = new Date().getFullYear();
})();
