const playerCorBoxElement = document.getElementById('player-cor-box');
const playerNomeElement = document.getElementById('turno-player-name');
const faseAtualElement = document.getElementById('fase-nome');


function atualizarHUD(jogadorAtual, jogadorCor, faseAtual) {
    playerNomeElement.textContent = jogadorAtual;
    faseAtualElement.textContent = faseAtual;

    playerCorBoxElement.style.backgroundColor = jogadorCor;
}

