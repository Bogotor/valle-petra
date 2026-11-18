/* Selector de modo claro / oscuro ("Día / Noche del valle").
   Se carga en <head> sin defer: fija data-theme antes de pintar, así la página no
   parpadea en claro cuando corresponde el modo oscuro. La elección se recuerda en
   localStorage; si no hay, se sigue la preferencia del sistema.
   También marca <html class="js"> para que las animaciones de entrada solo se
   apliquen cuando hay JavaScript (sin JS, todo el contenido queda visible). */
(function () {
  'use strict';

  var root = document.documentElement;
  root.classList.add('js');

  // localStorage puede fallar (modo privado, almacenamiento bloqueado): sin él, solo no se recuerda
  function leer(clave) {
    try { return localStorage.getItem(clave); } catch (e) { return null; }
  }
  function guardar(clave, valor) {
    try { localStorage.setItem(clave, valor); } catch (e) { /* sin persistencia */ }
  }

  var sistemaOscuro = window.matchMedia('(prefers-color-scheme: dark)').matches;
  root.setAttribute('data-theme', leer('vp-theme') || (sistemaOscuro ? 'dark' : 'light'));

  document.addEventListener('DOMContentLoaded', function () {
    var boton = document.getElementById('themeToggle');
    if (!boton) return;

    // Pulso de ayuda: se apaga si ya se usó antes, al usarlo o a los 12 segundos
    if (leer('vp-theme-touched')) boton.classList.remove('hint');
    setTimeout(function () { boton.classList.remove('hint'); }, 12000);

    boton.addEventListener('click', function () {
      boton.classList.remove('hint');
      guardar('vp-theme-touched', '1');
      var siguiente = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', siguiente);
      guardar('vp-theme', siguiente);
    });
  });
})();
