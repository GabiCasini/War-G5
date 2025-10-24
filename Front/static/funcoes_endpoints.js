const LOCALHOST = 'http://127.0.0.1:5000';

async function fetchJogadores() {
  try {
    const resp = await fetch('http://127.0.0.1:5000/partida/jogadores', { method: 'GET' });
    if (!resp.ok) {
      const errBody = await resp.json().catch(() => null);
      throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`);
    }
    const data = await resp.json();
    console.log('jogadores', data.jogadores);
    return data.jogadores;
  } catch (err) {
    console.error('Erro ao buscar jogadores:', err.message);
    throw err;
  }
}

// exemplo de chamada
fetchJogadores();

    