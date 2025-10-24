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
      console.log('jogadores', data.jogadores);
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
      console.log('territórios', data.territorios);
      territorios = data.territorios;
      console.log('territorios global', territorios);
      colorirTerritoriosNoMapa();
      desenharExercitosNoMapa()
      return data.territorios;
    })
    .catch(err => {
      console.error('Erro ao buscar territórios:', err.message);
      throw err;
    });
}

fetchJogadores();
fetchTerritorios();