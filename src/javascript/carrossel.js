var swiper = new Swiper(".swiper", {
loop: true,
  grabCursor: true,
  slidesPerView: 3, // Alterado para 'auto' no padrão
  centeredSlides: true, // Centraliza o slide ativo (opcional, mas pode melhorar o visual com 'auto')
  spaceBetween: 16, // Valor padrão para o espaço entre slides
  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },
  pagination: {
    el: ".swiper-pagination",
    clickable: true
  },
  breakpoints: {
    640: {
      slidesPerView: 1,
      spaceBetween: 18
    },
    768: {
      slidesPerView: 2,
      spaceBetween: 18
    },
    1024: {
      slidesPerView: 3,
      spaceBetween: 24
    }
  }
});