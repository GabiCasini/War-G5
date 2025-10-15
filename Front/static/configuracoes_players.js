
class Player {
    constructor(nome, cor, tipo) {
        this.nome = nome;
        this.cor = cor;
        this.tipo = tipo; // 'humano' ou 'ia'
    }
}

const players = [];

function buildPlayers() {
    players.length = 0; // reset

    const qtd_humanos_el = document.getElementById('qtd_humanos');
    const qtd_ai_el = document.getElementById('qtd_ai');

    const qtd_humanos = qtd_humanos_el ? parseInt(qtd_humanos_el.value) : 0;
    const qtd_ai = qtd_ai_el ? parseInt(qtd_ai_el.value) : 0;
    const total = qtd_humanos + qtd_ai;

    for (let i = 1; i <= total; i++) {
        const nomeInput = document.querySelector(`#p${i} input`) || document.querySelector(`input[name=\"nome_player_${i}\"]`);
        const nome = nomeInput ? nomeInput.value : `Jogador ${i}`;

        const corInput = document.getElementById(`input_cor_p${i}`);
        const cor = corInput ? corInput.value : null;

        const tipo = (i <= qtd_humanos) ? 'humano' : 'ai';

        players.push(new Player(nome, cor, tipo));
    }

    console.log(`Total players: ${players.length}`, players);
    return players;
}

window.buildPlayers = buildPlayers;
window.getPlayers = () => players;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#initDialog form');
    if (form) {
        form.addEventListener('submit', () => {
            buildPlayers();
        });
    }
});