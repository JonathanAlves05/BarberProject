// Abrir modal ao clicar no botão ou menu
  document.querySelectorAll('a[href="/apibarbearia/src/index.html"], a[href="#agendamento"]').forEach(el => {
    el.addEventListener('click', function(e) {
      e.preventDefault();
      document.getElementById('modal-agendamento').classList.add('active');
    });
  });

  // Fechar modal ao clicar no X
  document.getElementById('close-modal').onclick = function() {
    document.getElementById('modal-agendamento').classList.remove('active');
  };

  // Fechar modal ao clicar fora do conteúdo
  document.getElementById('modal-agendamento').onclick = function(e) {
    if (e.target === this) this.classList.remove('active');
  };