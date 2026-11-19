/* Galerías:
   - carrusel de fotos en cada tarjeta de alojamiento (flechas, puntos y deslizar);
   - visor a pantalla completa (lightbox) para alojamientos y espacios comunes.
   Las fotos salen del HTML: la pista de cada tarjeta (.lodge-track) y los <template>
   de cada espacio (#galeria-<nombre>). Las fotos marcadas con data-provisoria
   muestran la etiqueta "Imagen referencial". */
(function () {
  'use strict';

  // Convierte una lista de <img> en fotos para el visor (src = versión grande)
  var fotosDe = function (imgs) {
    return Array.prototype.map.call(imgs, function (img) {
      return {
        src: img.getAttribute('src'),
        alt: img.getAttribute('alt') || '',
        provisoria: img.hasAttribute('data-provisoria')
      };
    });
  };

  // ===== Carrusel de cada tarjeta =====
  document.querySelectorAll('[data-gallery]').forEach(function (galeria) {
    var pista = galeria.querySelector('.lodge-track');
    var imgs = pista.querySelectorAll('img');
    var puntos = galeria.querySelectorAll('.lodge-dots button');
    var contador = galeria.querySelector('.lodge-counter .cur');
    var total = imgs.length;
    var idx = 0;

    var ir = function (n) {
      idx = (n + total) % total;
      galeria.dataset.index = idx; // el visor abre en la foto que se está viendo
      pista.style.transform = 'translateX(-' + (idx * 100) + '%)';
      puntos.forEach(function (p, k) { p.classList.toggle('active', k === idx); });
      if (contador) contador.textContent = idx + 1;
      galeria.classList.toggle('es-provisoria', imgs[idx].hasAttribute('data-provisoria'));
    };

    galeria.querySelector('.prev').addEventListener('click', function () { ir(idx - 1); });
    galeria.querySelector('.next').addEventListener('click', function () { ir(idx + 1); });
    puntos.forEach(function (p, k) {
      p.addEventListener('click', function () { ir(k); });
    });

    // Con el dedo: deslizar cambia de foto; un toque (sin mover el dedo) abre el visor al tiro.
    // Se abre aquí y no en el "click" porque en celular ese click a veces no llega al primer
    // toque (el navegador lo gasta en efectos de :hover o lo pierde si la tarjeta se movió).
    var x0 = 0, y0 = 0, dx = 0, dy = 0, arrastrando = false;
    galeria.addEventListener('touchstart', function (e) {
      x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; dx = 0; dy = 0; arrastrando = true;
    }, { passive: true });
    galeria.addEventListener('touchmove', function (e) {
      if (!arrastrando) return;
      dx = e.touches[0].clientX - x0; dy = e.touches[0].clientY - y0;
    }, { passive: true });
    galeria.addEventListener('touchend', function (e) {
      if (!arrastrando) return;
      arrastrando = false;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) { ir(idx + (dx < 0 ? 1 : -1)); return; }
      var esToque = Math.abs(dx) < 10 && Math.abs(dy) < 10;
      if (esToque && !e.target.closest('.lodge-nav, .lodge-dots')) {
        e.preventDefault(); // evita el click que vendría después y abriría el visor dos veces
        abrirTarjeta(e.target);
      }
    });
    galeria.addEventListener('touchcancel', function () { arrastrando = false; });
  });

  // ===== Visor a pantalla completa =====
  var visor = document.getElementById('lightbox');
  var foto = document.getElementById('lbImg');
  var titulo = document.getElementById('lbTitle');
  var etiquetaRef = document.getElementById('lbRef');
  var actual = document.getElementById('lbCur');
  var total = document.getElementById('lbTotal');
  var puntos = document.getElementById('lbDots');
  var cerrar = document.getElementById('lbClose');

  var fotos = [];
  var idx = 0;
  var abierto = false;
  var disparador = null;

  var precargar = function (src) { var i = new Image(); i.src = src; };

  var pintarPuntos = function () {
    puntos.innerHTML = '';
    fotos.forEach(function (_, k) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Foto ' + (k + 1));
      b.addEventListener('click', function () { ir(k); });
      puntos.appendChild(b);
    });
  };

  var mostrar = function (conTransicion) {
    var f = fotos[idx];
    var poner = function () {
      foto.src = f.src;
      foto.alt = f.alt;
      foto.classList.remove('swapping');
    };
    if (conTransicion) {
      foto.classList.add('swapping');
      setTimeout(poner, 120);
    } else {
      poner();
    }
    etiquetaRef.hidden = !f.provisoria;
    actual.textContent = idx + 1;
    Array.prototype.forEach.call(puntos.children, function (b, k) { b.classList.toggle('active', k === idx); });
    // precargar las vecinas para que el cambio sea inmediato
    precargar(fotos[(idx + 1) % fotos.length].src);
    precargar(fotos[(idx - 1 + fotos.length) % fotos.length].src);
  };

  var ir = function (n) {
    idx = (n + fotos.length) % fotos.length;
    mostrar(true);
  };

  var abrir = function (lista, nombre, inicio, origen) {
    if (!lista.length) return;
    fotos = lista;
    idx = inicio || 0;
    disparador = origen;
    titulo.textContent = nombre;
    total.textContent = fotos.length;
    visor.setAttribute('aria-label', 'Galería de ' + nombre.split(' · ')[0]);
    pintarPuntos();
    mostrar(false);
    visor.setAttribute('aria-hidden', 'false');
    document.body.classList.add('lb-open');
    abierto = true;
    requestAnimationFrame(function () { cerrar.focus(); });
  };

  var cerrarVisor = function () {
    visor.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('lb-open');
    abierto = false;
    if (disparador && typeof disparador.focus === 'function') disparador.focus();
  };

  // Abre el visor de la tarjeta donde está t, en la foto que se está viendo
  var abrirTarjeta = function (t) {
    var tarjeta = t.closest('.lodge');
    var galeria = tarjeta.querySelector('[data-gallery]');
    abrir(
      fotosDe(galeria.querySelectorAll('.lodge-track img')),
      galeria.dataset.title,
      parseInt(galeria.dataset.index || '0', 10),
      t.closest('button') || tarjeta.querySelector('.lodge-gallery-btn')
    );
  };

  // Abrir: botón "Ver galería" o clic en la foto de una tarjeta; botón de un espacio
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (abierto) return;
    var enTarjeta = t.closest('[data-open-gallery], .lodge-img');
    if (enTarjeta) {
      if (t.closest('.lodge-nav, .lodge-dots')) return; // esos controles mueven el carrusel
      abrirTarjeta(t);
      return;
    }
    var espacio = t.closest('[data-open-space]');
    if (espacio) {
      var plantilla = document.getElementById('galeria-' + espacio.dataset.openSpace);
      if (plantilla) abrir(fotosDe(plantilla.content.querySelectorAll('img')), plantilla.dataset.title, 0, espacio);
    }
  });

  cerrar.addEventListener('click', cerrarVisor);
  document.getElementById('lbPrev').addEventListener('click', function () { ir(idx - 1); });
  document.getElementById('lbNext').addEventListener('click', function () { ir(idx + 1); });

  // Clic en el fondo (fuera de la foto) cierra
  visor.addEventListener('click', function (e) { if (e.target === visor) cerrarVisor(); });

  // Teclado: Esc cierra, flechas cambian de foto y Tab no sale del visor
  var ENFOCABLES = 'button, [href], [tabindex]:not([tabindex="-1"])';
  document.addEventListener('keydown', function (e) {
    if (!abierto) return;
    if (e.key === 'Escape') { e.preventDefault(); cerrarVisor(); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); ir(idx - 1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); ir(idx + 1); }
    else if (e.key === 'Tab') {
      var lista = Array.prototype.filter.call(visor.querySelectorAll(ENFOCABLES), function (el) {
        return !el.disabled && el.offsetParent !== null;
      });
      if (!lista.length) return;
      var primero = lista[0];
      var ultimo = lista[lista.length - 1];
      if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus(); }
      else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus(); }
    }
  });

  // Deslizar con el dedo
  var x0 = 0, dx = 0, arrastrando = false;
  visor.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; dx = 0; arrastrando = true; }, { passive: true });
  visor.addEventListener('touchmove', function (e) { if (arrastrando) dx = e.touches[0].clientX - x0; }, { passive: true });
  visor.addEventListener('touchend', function () {
    if (arrastrando && Math.abs(dx) > 50) ir(idx + (dx < 0 ? 1 : -1));
    arrastrando = false;
  });
})();
