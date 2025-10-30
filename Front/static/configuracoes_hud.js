const playerCorBoxElement = document.getElementById('player-cor-box');
const playerNomeElement = document.getElementById('turno-player-name');
const faseAtualElement = document.getElementById('fase-nome');
const btnPassarTurno = document.getElementById('btn-passar-turno');

function atualizarHUD(jogadorAtual, jogadorCor, faseAtual) {
    playerNomeElement.textContent = jogadorAtual;
    faseAtualElement.textContent = faseAtual;
    playerCorBoxElement.style.backgroundColor = jogadorCor;
}


btnPassarTurno.addEventListener('click', function() {
    postPassarTurno();
});

