const playerCorBoxElement = document.getElementById("player-cor-box");
const playerNomeElement = document.getElementById("turno-player-name");
const faseAtualElement = document.getElementById("fase-nome");
const btnPassarTurno = document.getElementById("btn-passar-turno");
const btnMinhasCartas = document.getElementById("btn-minhas-cartas");
const timerDisplay = document.getElementById("timer");
const infoExercitosQtdElement = document.getElementById("info-exercitos-qtd");
let timerInterval = null;
let tempoRestante = 0;

btnMinhasCartas.addEventListener('click', toggleMinhasCartas);

function toggleMinhasCartas(){
  let divCartas = document.getElementById("hud-wrapper-second-line")
  if (divCartas.style.display === 'none') {
    divCartas.style.display = 'flex'
    btnMinhasCartas.textContent = "Ocultar Cartas"
    return
  }
  divCartas.style.display = 'none'
  btnMinhasCartas.textContent = "Minhas Cartas"
}

function atualizarHUD(
  jogadorAtual,
  jogadorCor,
  faseAtual,
  tempoTurno,
  exercitosParaPosicionar
) {
  playerNomeElement.textContent = jogadorAtual;
  faseAtualElement.textContent = faseAtual;
  playerCorBoxElement.style.backgroundColor = jogadorCor;
  infoExercitosQtdElement.textContent = exercitosParaPosicionar;

  if (faseAtual.toLowerCase() === "posicionamento") {
    //Não reiniciar o timer se ele já estiver rodando — evita reset quando o jogador posiciona exércitos
    // Aceita string numérica ou número
    const t = Number(tempoTurno);
    if (isNaN(t)) {
      // não alterar o timer
    } else {
      // se não houver timer em andamento, iniciar; se houver, só reiniciar quando o servidor indicar tempo menor
      if (timerInterval == null) {
        iniciarTimerTurno(t);
      } else if (typeof tempoRestante === "number" && t < tempoRestante) {
        // servidor reduziu o tempo restante — sincroniza
        iniciarTimerTurno(t);
      }
    }
  }
}

function formatarTempo(segundos) {
  const minutos = Math.floor(segundos / 60);
  const segs = segundos % 60;
  return `${minutos.toString().padStart(2, "0")}:${segs
    .toString()
    .padStart(2, "0")}`;
}

function iniciarTimerTurno(tempoTurno) {
  if (isNaN(tempoTurno) || tempoTurno <= 0) {
    timerDisplay.textContent = "Erro de Config.";
    return;
  }

  tempoRestante = tempoTurno;
  timerDisplay.textContent = formatarTempo(tempoRestante);

  if (timerInterval != null) {
    clearInterval(timerInterval);
  }

  timerInterval = setInterval(() => {
    tempoRestante--;
    timerDisplay.textContent = formatarTempo(tempoRestante);

    if (tempoRestante < 0) {
      clearInterval(timerInterval);
      postFinalizarTurno();
    }
  }, 1000);
}

// Reinicia o timer para um novo jogador: limpa qualquer timer atual e inicia um novo com o tempo fornecido
function redefinirTimer(tempoTurno) {
  try {
    if (timerInterval != null) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  } catch (e) {
    console.warn("Falha ao limpar timer antigo:", e);
    timerInterval = null;
  }
  // iniciar novo timer (iniciarTimerTurno cuida da validação)
  iniciarTimerTurno(tempoTurno);
}

btnPassarTurno.addEventListener("click", function () {
  postPassarTurno();
});

const objectiveCardContainer = document.getElementById('objective-card-container');
if (objectiveCardContainer) {
    objectiveCardContainer.addEventListener('click', function() {
        this.classList.toggle('flipped');
    });
}

function postTrocarCartas(jogador_cor, cartasSelecionadasParaTroca) {
  return fetch(LOCALHOST + "/partida/trocar_cartas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jogador_id: jogador_cor,
      cartas: cartasSelecionadasParaTroca,
    }),
  })
    .then((resp) => {
      if (!resp.ok) {
        return resp
          .json()
          .then((errBody) => {
            throw new Error(
              (errBody && (errBody.mensagem || errBody.message)) ||
                `HTTP ${resp.status}`
            );
          })
          .catch(() => {
            throw new Error(`HTTP ${resp.status}`);
          });
      }
      return resp.json();
    })
    .then((data) => {
      console.log("Tentativa de troca de cartas finalizada com sucesso:", data);
      fetchJogadores();
      fetchTerritorios();
      fetchEstadoAtual();
      refreshTerritorios();
      return data;
    })
    .catch((err) => {
      console.error("Erro ao tentar trocar cartas:", err.message);
      throw err;
    });
}
