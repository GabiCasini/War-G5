const playerCorBoxElement = document.getElementById("player-cor-box");
const playerNomeElement = document.getElementById("turno-player-name");
const faseAtualElement = document.getElementById("fase-nome");
const btnPassarTurno = document.getElementById("btn-passar-turno");
const btnMinhasCartas = document.getElementById("btn-minhas-cartas");
const timerDisplay = document.getElementById("timer");
const infoExercitosQtdElement = document.getElementById("info-exercitos-qtd");
let timerInterval = null;
let tempoRestante = 0;

let listaCartasSelecionadas = [];

document.getElementById("hud-wrapper-second-line").style.display = 'none'
btnMinhasCartas.addEventListener('click', toggleMinhasCartas);

function toggleMinhasCartas(){
  let divCartas = document.getElementById("hud-wrapper-second-line")
  if (divCartas.style.display === 'none') {
    divCartas.style.display = 'flex'
    btnMinhasCartas.textContent = "Ocultar Cartas"
    // btnTrocarCartas.style.display = 'flex'
    return
  }
  divCartas.style.display = 'none'
  btnMinhasCartas.textContent = "Minhas Cartas"
  // btnTrocarCartas.style.display = 'none'
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

  let formattedCartas = cartasSelecionadasParaTroca.map(carta => [formatTextoCarta(carta[0]), carta[1]]);

  return fetch(LOCALHOST + "/partida/trocar_cartas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jogador_id: jogador_cor,
      cartas: formattedCartas,
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
      desmarcaTodasCartasTroca();
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

function toggleCartaTroca(elemento) {
  
  let formaCarta = elemento.classList[0].split('-')[1];
  let textoCarta = elemento.querySelector('.texto-imagem-carta').textContent;

  

  if (elemento.classList.contains('carta-selecionada')) {
    // Remover seleção
    elemento.classList.remove('carta-selecionada');
    listaCartasSelecionadas = listaCartasSelecionadas.filter(carta => carta[0] !== formaCarta);
  } else {
    if (listaCartasSelecionadas.length >= 2) {
      let cartasDiferentes = new Set(listaCartasSelecionadas.map(carta => carta[0]));
      cartasDiferentes.add(formaCarta);

      let numCartasIguais = listaCartasSelecionadas.filter(carta => carta[0] === formaCarta).length + 1;

      if ((cartasDiferentes.size === 3) || (numCartasIguais === 3) || (formaCarta === 'coringa')) {

        if (faseAtual !== "posicionamento") {
          alert("Você só pode trocar cartas na fase de posicionamento.");
          return;
        }
        // Três cartas diferentes selecionadas
        elemento.classList.add('carta-selecionada');
        listaCartasSelecionadas.push([formaCarta, textoCarta]);
        alert("trocando cartas...")
        postTrocarCartas(jogadorAtual, listaCartasSelecionadas);
        return;
      }
    // Verificar se todas as cartas selecionadas são iguais à nova carta
      for (let carta of listaCartasSelecionadas) {
        if (carta[0] !== formaCarta) {
          
        }
    }
    // Adicionar seleção
    alert("Combinação inválida. Selecione três cartas iguais ou três cartas diferentes.");
    desmarcaTodasCartasTroca();
    return;

    }
    // Adicionar seleção
    elemento.classList.add('carta-selecionada');
    listaCartasSelecionadas.push([formaCarta, textoCarta]);
  }

}



function constroiCartasTroca(listaCartas) {

  const wrapperCartas = document.getElementById('wrapper-cartas');
  wrapperCartas.innerHTML = ''; // Limpa cartas existentes

  listaCartas.forEach((carta, index) => {

    let textCarta = carta[1];
    let cartaForma = carta[0];

    if (cartaForma === 'Círculo') {
      cartaForma = 'circulo';
    } else if (cartaForma === 'Quadrado') {
      cartaForma = 'quadrado';
    } else if (cartaForma === 'Triângulo') {
      cartaForma = 'triangulo';
    } else if (cartaForma === 'Coringa') {
      cartaForma = 'coringa';
    }

    const cartaDiv = document.createElement('div');
    cartaDiv.classList.add(`carta-${cartaForma}`);
    cartaDiv.classList.add('cartas-troca');
    cartaDiv.setAttribute('onclick', 'toggleCartaTroca(this)');
    cartaDiv.setAttribute('id', `carta-troca-${index + 1}`);

    const img = document.createElement('img');
    img.src = `/static/Carta_objetivo_${cartaForma}.svg`;
    img.alt = 'Verso da Carta';
    img.classList.add('carta-troca-imagem');

    const textoDiv = document.createElement('div');
    textoDiv.classList.add('texto-imagem-carta');
    textoDiv.textContent = textCarta || '';

    cartaDiv.appendChild(img);
    cartaDiv.appendChild(textoDiv);

    wrapperCartas.appendChild(cartaDiv);
    
  });
}

function desmarcaTodasCartasTroca() {
  const cartas = document.querySelectorAll('.cartas-troca');
  cartas.forEach(carta => {
    carta.classList.remove('carta-selecionada');
  });
  listaCartasSelecionadas = [];
}


function formatTextoCarta(texto){
  if (texto === "circulo"){
    return "Círculo";
  } else if (texto === "quadrado"){
    return "Quadrado";
  } else if (texto === "triangulo"){
    return "Triângulo";
  } else if (texto === "coringa"){
    return "Coringa";
  }
}