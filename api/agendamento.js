document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('appointment-form');
  if (!form) return;

  // Preencher barbeiros
  fetch('http://127.0.0.1:8000/barbeiros/')
    .then(resp => resp.json())
    .then(barbeiros => {
      const select = form.barbeiro;
      barbeiros.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.id;
        opt.textContent = b.nome;
        select.appendChild(opt);
      });
    });

  // Preencher serviços
  fetch('http://127.0.0.1:8000/servicos/')
    .then(resp => resp.json())
    .then(servicos => {
      const select = form.servico;
      servicos.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = s.nome;
        select.appendChild(opt);
      });
    });

  form.barbeiro.addEventListener('change', function() {
  form.data.value = '';
  form.hora.innerHTML = '<option value="">Selecione</option>';
  // Não faz mais nada, todas as datas ficam disponíveis
});

// Preencher horários disponíveis ao escolher data
form.data.addEventListener('change', atualizarHorarios);

function atualizarHorarios() {
  const barbeiroId = form.barbeiro.value;
  const data = form.data.value;
  const selectHora = form.hora;
  selectHora.innerHTML = '<option value="">Selecione</option>';
  if (!barbeiroId || !data) return;
  fetch(`http://127.0.0.1:8000/barbeiros/${barbeiroId}/horarios_disponiveis/?data=${data}`)
    .then(resp => resp.json())
    .then(horarios => {
      horarios.forEach(hora => {
        const opt = document.createElement('option');
        opt.value = hora;
        opt.textContent = hora;
        selectHora.appendChild(opt);
      });
    });
}

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const dataHora = form.data.value + 'T' + form.hora.value;
    const data = {
      cliente_nome: form.nome.value,
      cliente_telefone: form.telefone.value,
      servico_id: form.servico.value,
      barbeiro_id: form.barbeiro.value,
      data_hora: dataHora,
      observacoes: form.obs.value,
      status: "confirmado"
    };
    try {
      const resp = await fetch('http://127.0.0.1:8000/agendamentos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (resp.ok) {
        alert('Agendamento realizado com sucesso!');
        form.reset();
      } else {
        alert('Erro ao agendar. Tente novamente.');
      }
    } catch (err) {
      alert('Erro de conexão com o servidor.');
    }
  });
});
