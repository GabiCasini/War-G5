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
        let exercitosParaPosicionar = data.exercitos_disponiveis.total;
        tempoTurno = data.turno.tempo_turno;
        let faseAtualStringPrimeiraMaiuscula = faseAtual.charAt(0).toUpperCase() + faseAtual.slice(1);
        let corHexJogador = players.find(p => p.cor === jogadorAtual).corHex;
        atualizarExercitosParaPosicionar(jogadorAtual,exercitosParaPosicionar);
        atualizarHUD(data.turno.jogador_nome, corHexJogador, faseAtualStringPrimeiraMaiuscula, tempoTurno, exercitosParaPosicionar);
        console.log(data)
      return data;
    })
    .catch(err => {
      console.error('Erro estado atual:', err.message);
      throw err;
    });
}


function postPassarTurno() {
  return fetch(LOCALHOST + '/partida/avancar_turno', { method: 'POST' })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    })
    .then(data => {
      console.log('Turno passado com sucesso:', data);
      fetchJogadores();
      fetchTerritorios();
      fetchEstadoAtual();
      refreshTerritorios();
      return data;
    })
    .catch(err => {
      console.error('Erro ao passar turno:', err.message);
      throw err;
    });
}

function postFinalizarTurno() {
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
      refreshTerritorios();
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
    body: JSON.stringify({ jogador_id: jogador_cor, territorio: territorio, exercitos: quantidade })
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
      fetchEstadoAtual();
      fetchEstadoAtual();
      return data;
    })
    .catch(err => {
      console.error('Erro ao posicionar exércitos:', err.message);
      throw err;
    });
}


function postAtaque(jogador_cor, territorio_origem, territorio_ataque) {
  return fetch(LOCALHOST + '/partida/ataque', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jogador_id: jogador_cor, territorio_origem: territorio_origem, territorio_ataque: territorio_ataque })
  })
    .then(resp => {
      if (!resp.ok) {
        return resp.json()
          .then(errBody => { throw new Error((errBody && (errBody.mensagem || errBody.message)) || `HTTP ${resp.status}`); })
          .catch(() => { throw new Error(`HTTP ${resp.status}`); });
      }
      return resp.json();
    }
    )
    .then(data => {
      console.log('Ataque realizado com sucesso:', data);
      
      if (data.rolagens_ataque && data.rolagens_defesa) {
        mostrarResultadoAtaque(data);
      } else {
        alert(data.territorio_conquistado ? 'Território conquistado!' : 'Ataque finalizado.');
        fetchTerritorios();
        fetchEstadoAtual();
      }
      
      return data;
    })
    .catch(err => {
      console.error('Erro ao realizar ataque:', err.message);
      alert(`Erro no ataque: ${err.message}`);
      throw err;
    });
}


function postReposicionamento(jogador_cor, territorio_origem, territorio_destino, quantidade) {
  return fetch(LOCALHOST + '/partida/reposicionamento', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jogador_id: jogador_cor, territorio_origem: territorio_origem, territorio_destino: territorio_destino, exercitos: quantidade })
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
      console.log('Reposicionamento realizado com sucesso:', data);
      fetchTerritorios();
      fetchEstadoAtual();
      return data;
    })
    .catch(err => {
      console.error('Erro ao realizar reposicionamento:', err.message);
      alert(`Erro no reposicionamento: ${err.message}`);
      throw err;
    });
}


function mostrarResultadoAtaque(data) {
  const dialog = document.getElementById('ataqueResultadoDialog');
  const titulo = document.getElementById('ataqueResultadoTitulo');
  const imgsAtaque = document.getElementById('dados-ataque-imgs');
  const imgsDefesa = document.getElementById('dados-defesa-imgs');
  const resultadoTexto = document.getElementById('ataqueResultadoTexto');
  const btnFechar = document.getElementById('ataqueResultadoFechar');

  imgsAtaque.innerHTML = '';
  imgsDefesa.innerHTML = '';

  if (data.rolagens_ataque && Array.isArray(data.rolagens_ataque)) {
    data.rolagens_ataque.forEach(num => {
      const img = document.createElement('img');
      img.src = `static/d${num}.png`;
      img.alt = `Dado ${num}`;
      imgsAtaque.appendChild(img);
    });
  }

  if (data.rolagens_defesa && Array.isArray(data.rolagens_defesa)) {
    data.rolagens_defesa.forEach(num => {
      const img = document.createElement('img');
      img.src = `static/d${num}.png`;
      img.alt = `Dado ${num}`;
      imgsDefesa.appendChild(img);
    });
  }

  let mensagem = `Ataque perdeu: ${data.perdas_ataque}. Defesa perdeu: ${data.perdas_defesa}.<br>`;
  if (data.territorio_conquistado) {
    titulo.textContent = 'Território Conquistado!';
    mensagem += '<strong>O ataque foi bem-sucedido!</strong>';
  } else {
    titulo.textContent = 'Combate Realizado';
    if (data.perdas_ataque > data.perdas_defesa) {
        mensagem += '<strong>A defesa venceu a troca.';
    } else if (data.perdas_defesa > data.perdas_ataque) {
        mensagem += '<strong>O ataque venceu a troca.';
    } else {
        mensagem += '<strong>Houve um empate na troca (defesa vence).';
    }
  }
  resultadoTexto.innerHTML = mensagem;

  btnFechar.onclick = () => {
    dialog.close();
    fetchTerritorios();
    fetchEstadoAtual();
  };

  dialog.showModal();
}


fetchJogadores();
fetchTerritorios();
fetchEstadoAtual();