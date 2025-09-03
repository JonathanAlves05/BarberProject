const API_BASE_URL = 'http://127.0.0.1:8000';

function formatarDataHora(dataHoraStr) {
  if (!dataHoraStr) return '';
  const data = new Date(dataHoraStr);
  if (isNaN(data)) return dataHoraStr;
  const dia = String(data.getDate()).padStart(2, '0');
  const mes = String(data.getMonth() + 1).padStart(2, '0');
  const ano = data.getFullYear();
  const hora = String(data.getHours()).padStart(2, '0');
  const min = String(data.getMinutes()).padStart(2, '0');
  return `${dia}/${mes}/${ano} ${hora}:${min}`;
}

async function carregarAgendamentos() {
  const barbeiroId = document.getElementById('barbeiro-id').value;
  const resp = await fetch(`${API_BASE_URL}/barbeiros/${barbeiroId}/agendamentos/`);
  const agendamentos = await resp.json();
  const div = document.getElementById('agendamentos');
  div.innerHTML = '';
  agendamentos.forEach(ag => {
    div.innerHTML += `
      <div class="agendamento-card">
        <label>Cliente:</label> ${ag.cliente_nome}<br>
        <label>Data/Hora:</label> ${formatarDataHora(ag.data_hora)}<br>
        <label>Status:</label>
        <input type="text" id="status-${ag.id}" value="${ag.status}">
        <button onclick="editarAgendamento(${ag.id})">Salvar</button>
        <span id="salvo-${ag.id}" class="status-salvo" style="display:none;">Salvo!</span>
      </div>
    `;
  });
}

async function editarAgendamento(id) {
  const resp = await fetch(`${API_BASE_URL}/agendamentos/${id}`);
  const agendamento = await resp.json();
  agendamento.status = document.getElementById('status-' + id).value;
  await fetch(`${API_BASE_URL}/agendamentos/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(agendamento)
  });
  const salvo = document.getElementById('salvo-' + id);
  salvo.style.display = 'inline';
  setTimeout(() => salvo.style.display = 'none', 1500);
}
async function carregarAgendamentos() {
  const barbeiroId = document.getElementById('barbeiro-id').value;
  const resp = await fetch(`${API_BASE_URL}/barbeiros/${barbeiroId}/agendamentos/`);
  const agendamentos = await resp.json();
  const div = document.getElementById('agendamentos');
  div.innerHTML = '';
  agendamentos.forEach(ag => {
    div.innerHTML += `
      <div class="agendamento-card">
        <label>Cliente:</label> ${ag.cliente_nome}<br>
        <label>Data/Hora:</label> ${formatarDataHora(ag.data_hora)}<br>
        <label>Status:</label>
        <input type="text" id="status-${ag.id}" value="${ag.status}">
        <button onclick="editarAgendamento(${ag.id})">Salvar</button>
        <button onclick="excluirAgendamento(${ag.id})" style="margin-left:8px;color:#fff;background:#d9534f;">Excluir</button>
        <span id="salvo-${ag.id}" class="status-salvo" style="display:none;">Salvo!</span>
      </div>
    `;
  });
}

// ...existing code...

async function editarAgendamento(id) {
  const resp = await fetch(`${API_BASE_URL}/agendamentos/${id}`);
  const agendamento = await resp.json();
  agendamento.status = document.getElementById('status-' + id).value;
  await fetch(`${API_BASE_URL}/agendamentos/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(agendamento)
  });
  const salvo = document.getElementById('salvo-' + id);
  salvo.style.display = 'inline';
  setTimeout(() => salvo.style.display = 'none', 1500);
}

// Adicione esta função ao final do arquivo
async function excluirAgendamento(id) {
  if (!confirm('Tem certeza que deseja excluir este horário?')) return;
  await fetch(`${API_BASE_URL}/agendamentos/${id}`, {
    method: 'DELETE'
  });
  carregarAgendamentos();
}