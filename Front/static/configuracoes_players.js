
class Player {
    constructor(id, nome, cor, tipo) {
        this.playerId = "p" + id;
        this.nome = nome;
        this.cor = cor;
        this.tipo = tipo; // 'humano' ou 'ia'
    }
}

const players = [];

function adicionarPlayer(nome, cor, tipo) {
    const player = new Player(players.length + 1, nome, cor, tipo);
    players.push(player);
}

adicionarPlayer("Jogador 1", "#01B57D", "humano");
adicionarPlayer("Jogador 2", "#EC9151", "humano");
adicionarPlayer("Jogador 3", "#8E5751", "humano");