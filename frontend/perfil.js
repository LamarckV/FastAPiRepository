/* ====================================================
   Tela Perfil — envio do formulário.

   Esta tela só ESCREVE. Ela não carrega o perfil salvo ao abrir,
   e a API não precisa expor rota de leitura.
   ==================================================== */

const USER_ID = 'usuario_teste';
const ENDPOINT = '/perfil';

const API_BASE =
  window.location.protocol === 'file:' ? 'http://localhost:8000' : '';

const els = {
  badge: document.getElementById('user-badge'),
  renda: document.getElementById('renda_mensal'),
  objetivo: document.getElementById('objetivo'),
  tolerancia: document.getElementById('tolerancia_risco'),
  preferencias: document.getElementById('preferencias'),
  status: document.getElementById('status'),
  submit: document.getElementById('submit'),
  echo: document.getElementById('echo'),
  echoBody: document.getElementById('echo-body'),
};

if (els.badge) {
  els.badge.textContent = USER_ID;
}

function setStatus(text, kind) {
  if (!els.status) return;
  els.status.textContent = text;
  els.status.className = 'sheet__status' + (kind ? ` is-${kind}` : '');
}

function montarPayload() {
  const renda = els.renda ? els.renda.value.trim() : '';

  return {
    user_id: USER_ID,
    renda_mensal: renda === '' ? null : Number(renda),
    objetivo: els.objetivo ? els.objetivo.value.trim() || null : null,
    tolerancia_risco: els.tolerancia ? els.tolerancia.value || null : null,
    preferencias: els.preferencias ? els.preferencias.value.trim() || null : null,
  };
}

function mostrarResposta(dados) {
  if (!els.echoBody || !els.echo) return;
  els.echoBody.textContent = JSON.stringify(dados, null, 2);
  els.echo.hidden = false;
}

async function salvar() {
  const payload = montarPayload();

  if (els.submit) els.submit.disabled = true;
  setStatus('enviando...');
  if (els.echo) els.echo.hidden = true;

  try {
    const resposta = await fetch(API_BASE + ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    let corpo = null;
    try {
      corpo = await resposta.json();
    } catch {
      corpo = { detail: 'a resposta não era JSON' };
    }

    if (!resposta.ok) {
      setStatus(`a api recusou (${resposta.status})`, 'error');
      mostrarResposta(corpo);
      return;
    }

    setStatus('perfil salvo', 'ok');
    mostrarResposta(corpo);
  } catch (erro) {
    setStatus('não consegui falar com a api', 'error');
    mostrarResposta({ erro: String(erro) });
  } finally {
    if (els.submit) els.submit.disabled = false;
  }
}

if (els.submit) {
  els.submit.addEventListener('click', salvar);
}
