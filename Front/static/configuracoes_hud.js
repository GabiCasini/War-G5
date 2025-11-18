const playerCorBoxElement = document.getElementById('player-cor-box');
const playerNomeElement = document.getElementById('turno-player-name');
const faseAtualElement = document.getElementById('fase-nome');
const btnPassarTurno = document.getElementById('btn-passar-turno');
const timerDisplay = document.getElementById('timer');
const infoExercitosQtdElement = document.getElementById('info-exercitos-qtd');
let timerInterval = null;

function atualizarHUD(jogadorAtual, jogadorCor, faseAtual, tempoTurno, exercitosParaPosicionar) {
    playerNomeElement.textContent = jogadorAtual;
    faseAtualElement.textContent = faseAtual;
    playerCorBoxElement.style.backgroundColor = jogadorCor;
    infoExercitosQtdElement.textContent = exercitosParaPosicionar;

    if (faseAtual.toLowerCase() === 'posicionamento') {
        iniciarTimerTurno(tempoTurno);
    }
}

function formatarTempo(segundos) {
    const minutos = Math.floor(segundos / 60);
    const segs = segundos % 60;
    return `${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
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

btnPassarTurno.addEventListener('click', function() {
    postPassarTurno();
});

const objectiveCardContainer = document.getElementById('objective-card-container');
if (objectiveCardContainer) {
    objectiveCardContainer.addEventListener('click', function() {
        this.classList.toggle('flipped');
    });
}
