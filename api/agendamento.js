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

  // Preencher horários disponíveis ao escolher barbeiro e data
  form.data.addEventListener('change', atualizarHorarios);
  form.barbeiro.addEventListener('change', atualizarHorarios);

  function atualizarHorarios() {
    const barbeiroId = form.barbeiro.value;
    const data = form.data.value;
    const selectHora = form.hora;
    selectHora.innerHTML = '<option value="">Selecione</option>';
    if (!barbeiroId || !data) return;
    fetch(`http://127.0.0.1:8000/horarios_disponiveis/?barbeiro_id=${barbeiroId}&data=${data}`)
      .then(resp => resp.json())
      .then(horarios => {
        horarios.forEach(h => {
          // Gera opções de horários de 30 em 30 minutos dentro do intervalo disponível
          let inicio = h.hora_inicio;
          let fim = h.hora_fim;
          let [hIni, mIni] = inicio.split(':').map(Number);
          let [hFim, mFim] = fim.split(':').map(Number);
          let dateIni = new Date(`2000-01-01T${inicio}`);
          let dateFim = new Date(`2000-01-01T${fim}`);
          while (dateIni <= dateFim) {
            const horaStr = dateIni.toTimeString().slice(0,5);
            const opt = document.createElement('option');
            opt.value = horaStr;
            opt.textContent = horaStr;
            selectHora.appendChild(opt);
            dateIni.setMinutes(dateIni.getMinutes() + 30);
          }
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