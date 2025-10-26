let jogadorAtual = null;
let faseAtual = null;
let jogadorCorAtual = null;
const LOCALHOST = 'http://127.0.0.1:5000';


function fetchJogadores() {
  return fetch(LOCALHOST + '/partida/jogadores', { method: 'GET' })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    })
    .then(data => {
    //   console.log('jogadores', data.jogadores);
      for (let jogador of data.jogadores) {
        adicionarPlayer(jogador.nome, jogador.cor, jogador.tipo);
      }
      return data.jogadores;
    })
    .catch(err => {
      console.error('Erro ao buscar jogadores:', err.message);
      throw err;
    });
}


function fetchTerritorios() {
  return fetch(LOCALHOST + '/partida/territorios', { method: 'GET' })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    })
    .then(data => {
      territorios = data.territorios;
      colorirTerritoriosNoMapa();
      desenharExercitosNoMapa()
      return data.territorios;
    })
    .catch(err => {
      console.error('Erro ao buscar territórios:', err.message);
      throw err;
    });
}


function fetchEstadoAtual() {
  return fetch(LOCALHOST + '/partida/estado_atual', { method: 'GET' })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    })
    .then(data => {
        jogadorAtual = data.turno.jogador_cor;
        faseAtual = data.turno.fase;
        let faseAtualStringPrimeiraMaiuscula = faseAtual.charAt(0).toUpperCase() + faseAtual.slice(1);
        let corHexJogador = players.find(p => p.cor === jogadorAtual).corHex;
        atualizarHUD(data.turno.jogador_nome, corHexJogador, faseAtualStringPrimeiraMaiuscula);
        console.log(data)
      return data;
    })
    .catch(err => {
      console.error('Erro estado atual:', err.message);
      throw err;
    });
}


function postPassarTurno() {
  return fetch(LOCALHOST + '/partida/finalizar_turno', { method: 'POST' })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    })
    .then(data => {
      console.log('Turno finalizado com sucesso:', data);
      fetchJogadores();
      fetchTerritorios();
      fetchEstadoAtual();
      return data;
    })
    .catch(err => {
      console.error('Erro ao finalizar turno:', err.message);
      throw err;
    });
}


function postPosicionarExercitos(jogador_cor, territorio, quantidade) {
  return fetch(LOCALHOST + '/partida/posicionamento', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jogador_id: jogador_cor, territorio: territorio, quantidade: quantidade })
  })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    })
    .then(data => {
      console.log('Exércitos posicionados com sucesso:', data);
      fetchTerritorios();
      return data;
    })
    .catch(err => {
      console.error('Erro ao posicionar exércitos:', err.message);
      throw err;
    });
}


fetchJogadores();
fetchTerritorios();
fetchEstadoAtual();