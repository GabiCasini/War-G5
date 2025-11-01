
class Player {
    constructor(id, nome, cor, tipo) {
        this.playerId = id;
        this.nome = nome;
        this.cor = cor;
        this.corHex = atribuiCorHexJogador(cor);
        this.tipo = tipo;
        this.exercitosDisponiveisPosicionamento = 0;
    }
}

let players = [];

function adicionarPlayer(nome, cor, tipo) {
    const player = new Player(players.length + 1, nome, cor, tipo);
    players.push(player);
}

function atribuiCorHexJogador(cor) {
    if (cor === "verde") {
        return "#4CAF50";
    } else if (cor === "laranja") {
        return "#FF9800";
    } else if (cor === "vermelho") {
        return "#F44336";
    }
    else if (cor === "azul") {
        return "#2196F3";
    }
    else if (cor === "roxo") {
        return "#9C27B0";
    }
    else if (cor === "amarelo") {
        return "#FFEB3B";
    }
}

function atualizarExercitosParaPosicionar(corJogador, quantidade) {
    const jogador = players.find(p => p.cor === corJogador);
    if (jogador) {
        jogador.exercitosDisponiveisPosicionamento = quantidade;
    }
}