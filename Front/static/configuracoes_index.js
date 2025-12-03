const initDialog = document.getElementById('initDialog');
const openInitBtn = document.getElementById('openInitDialog');
const menuDialog = document.getElementById('menuDialog');
const openMenuBtn = document.getElementById('openMenuDialog');
const continueBtn = document.getElementById('continueBtn');
const backBtn = document.getElementById('backBtn');
const closeInitDialogBtn = document.getElementById('closeInitDialogBtn');
const closeMenuDialogBtn = document.getElementById('closeMenuDialogBtn');
const audio = document.getElementById("audio");
const dialogP1 = document.getElementById('dialogP1');
const dialogP2 = document.getElementById('dialogP2');
const volumeSlider = document.getElementById('volume-slider');
const p4 = document.getElementById('p4');
const cor_p4 = document.getElementById('cor_p4');
const p5 = document.getElementById('p5');
const cor_p5 = document.getElementById('cor_p5');
const p6 = document.getElementById('p6');
const cor_p6 = document.getElementById('cor_p6');
const textElement = document.getElementById("pageText");
const pages = [
    "Os territórios são distribuídos da maneira mais igualitária possível entre os jogadores, \
    contendo 1 exército cada um. Os jogadores começam sem cartas de troca, \
    e os objetivos são sorteados de forma que não exista 2 ou mais jogadores com o mesmo objetivo. \
    <br><br>\
    No primeiro turno de cada jogador, é possível apenas posicionar exércitos nos seus territórios, \
    já nos demais turnos será possível atacar e reposicionar. A ordem dos turnos é definida no início da partida, \
    e não será alterada até o fim da mesma. \
    <br><br>\
    Cada jogador recebe um número de exércitos equivalente à metade da quantidade de territórios que ele possui, \
    arredondado para baixo, entretanto, mesmo que ele possua 5 ou menos territórios, \
    a quantidade mínima de exércitos recebidos por turno (3 exércitos) deve ser respeitada.",

    "Caso o jogador possua um continente inteiro dominado no início de seu turno, \
    ele recebe o bônus equivalente ao determinado continente, e só poderá posicionar os exércitos de bônus naquele continente específico. \
    <br><br>\
    Caso o jogador possua 3 cartas iguais, ou 3 cartas diferentes (a carta coringa assume qualquer símbolo necessário para a realização da troca), \
    ele pode trocar essas 3 cartas selecionadas por mais exércitos. Essa troca só pode ser feita durante a fase de posicionamento, \
    e o número de exércitos concedidos é comutativo e aumenta a cada troca realizada, de acordo com a seguinte ordem: 4, 6, 8, 10, 12, 15, 20, 25, 30… \
    <br><br>\
    Cada carta possui o nome de um território nela (com exceção da coringa), e caso ela seja utilizada na troca e o jogador possua aquele território, \
    serão adicionados automaticamente 2 exércitos naquele território específico. \
    <br><br>\
    Na fase de ataque, o jogador pode realizar quantos ataques quiser, basta que ele possua algum território com mais de 1 exército que faça fronteira com algum território inimigo.",

    "Ao escolher um território elegível para ataque, e após isso, escolher um alvo elegível, o sistema deve sortear os valores (de 1 a 6) dos dados correspondentes de cada jogador (atacante e defensor) para poder calcular o resultado do ataque. \
    A quantidade de dados de cada jogador varia de acordo com o número de exércitos em cada território, de acordo com a seguinte tabela: \
    <br><br>\
    <table border='1' cellpadding='5' style='border-collapse: collapse; margin: auto;'>\
        <thead>\
        <tr>\
            <th>Exércitos no território</th>\
            <th>Dados do atacante</th>\
            <th>Dados do defensor</th>\
        </tr>\
        </thead>\
        <tbody>\
        <tr>\
            <td>1</td>\
            <td>Não pode atacar</td>\
            <td>1</td>\
        </tr>\
        <tr>\
            <td>2</td>\
            <td>1</td>\
            <td>2</td>\
        </tr>\
        <tr>\
            <td>3</td>\
            <td>2</td>\
            <td>3</td>\
        </tr>\
        <tr>\
            <td>4+</td>\
            <td>3</td>\
            <td>3</td>\
        </tr>\
        </tbody>\
    </table>\
    <br><br>\
    Para cada ataque realizado, no máximo 3 exércitos serão perdidos (somando ataque e defesa). Para definir quantos exércitos cada território perderá, \
    o sistema deve ordenar os valores sorteados dos dados de cada jogador, e então realizar as comparações, de forma que o valor mais alto de um jogador seja sempre comparado com o valor mais alto do outro jogador.",

    "Caso o número de dados dos jogadores seja diferente, o número de comparações e consequentemente o número de exércitos perdidos naquele ataque (somando ataque e defesa) será igual à quantidade de dados do jogador que possuir menos dados, \
    ou seja, caso o atacante possua 3 dados e o defensor possua 2, o maior valor obtido pela defesa será comparado com o maior valor obtido pelo ataque, e o segundo maior valor da defesa será comparado com o segundo maior valor do ataque, \
    logo, apenas 2 exércitos serão perdidos nesse ataque. \
    <br><br>\
    Caso o valor do ataque seja maior, a defesa perde 1 exército, caso contrário, o ataque perde um exército, portanto, é possível que tanto o ataque quanto a defesa percam exércitos durante um único ataque. \
    <br><br>\
    Caso o território de defesa perca todos os seus exércitos, o atacante terá conquistado aquele território, e deverá escolher quantos exércitos do território de ataque ele deseja passar para o território conquistado (de 1 a 3 exércitos), \
    respeitando a regra de que cada território deve possuir obrigatoriamente pelo menos 1 exército. \
    <br><br>\
    Caso um jogador seja eliminado, suas cartas passarão para o jogador que tomou seu último território (respeitando o limite de no máximo 5 cartas por jogador).",

    "Ao final da fase de ataque, caso o jogador tenha conquistado pelo menos 1 território, ele ganha uma carta. \
    <br><br>\
    Após o fim da fase de ataque, inicia-se a fase de reposicionamento. Nesse momento, o jogador deve poder passar exércitos de um território para outro, \
    contanto que eles possuam uma fronteira entre si. Além disso, o sistema deve garantir que cada território só possa repassar um número de exércitos equivalente à quantidade que ele tinha no início da fase de reposicionamento - 1, \
    ou seja, caso um território possua 10 exércitos no início da fase de reposicionamento, ele só poderá repassar 9 exércitos. \
    <br><br>\
    A cada posicionamento/reposicionamento realizado pelo jogador, o sistema deve conferir se o jogador do turno completou seu objetivo ou não. \
    <br><br>\
    Após cada conquista de território realizada por um jogador, o sistema deve conferir se qualquer jogador completou seu objetivo ou não, respeitando a seguinte ordem:\
    <br><br>\
    1: Jogador do turno atual.\
    <br>\
    2: Todos os outros jogadores, seguindo a ordem dos turnos.",
];
let currentPage = 0;

openInitBtn.addEventListener('click', () => {
    audio.play();
    initDialog.showModal();
    dialogP1.style.display = 'block';
    continueBtn.style.display = 'block';
    dialogP2.style.display = 'none';
    navigator.sendBeacon("/partida/resetar_partida");
});

closeInitDialogBtn.addEventListener('click', () => {
    initDialog.close();
    p4.style.display = 'none';
    cor_p4.style.display = 'none';
    p5.style.display = 'none';
    cor_p5.style.display = 'none';
    p6.style.display = 'none';
    cor_p6.style.display = 'none';
});

openMenuBtn.addEventListener('click', () => {
    menuDialog.showModal();
});

closeMenuDialogBtn.addEventListener('click', () => {
    currentPage = 0;
    updatePage()
    menuDialog.close();
});

backBtn.addEventListener('click', () => {
    dialogP1.style.display = 'block';
    continueBtn.style.display = 'block';
    dialogP2.style.display = 'none';
    p4.style.display = 'none';
    cor_p4.style.display = 'none';
    p5.style.display = 'none';
    cor_p5.style.display = 'none';
    p6.style.display = 'none';
    cor_p6.style.display = 'none';
});

continueBtn.addEventListener('click', () => {
    validado = validate_num_players(); // TODO: move validations to Validation class
    if (!validado) {
    alert("O número total de jogadores deve ser entre 3 e 6.");
    return;
    }

    num_players = get_num_players()
    if (num_players >= 4){
    p4.style.display = 'flex';
    cor_p4.style.display = 'flex';
    } if (num_players >= 5){
    p5.style.display = 'flex';
    cor_p5.style.display = 'flex';
    } if (num_players >= 6){
    p6.style.display = 'flex';
    cor_p6.style.display = 'flex';
    }
    
    dialogP1.style.display = 'none';
    continueBtn.style.display = 'none';
    dialogP2.style.display = 'block';
});

function validate_num_players() {
    const total_players = get_num_players();
    return total_players >= 3 && total_players <= 6;
}

function get_num_players() {
    const qtd_humanos = parseInt(document.getElementById('qtd_humanos').value);
    const qtd_ai = parseInt(document.getElementById('qtd_ai').value);
    return qtd_humanos + qtd_ai;
}

let dragged = null;
const colors = document.querySelectorAll('.color');

colors.forEach(color => {
    color.addEventListener('dragstart', e => {
        dragged = e.target;
    });

    color.addEventListener('dragover', e => {
        e.preventDefault();
    });

    color.addEventListener('drop', e => {
        e.preventDefault();
        if (dragged !== e.target) {
            // troca visual de cores
            const tempColor = dragged.style.backgroundColor;
            dragged.style.backgroundColor = e.target.style.backgroundColor;
            e.target.style.backgroundColor = tempColor;

            // troca também o nome/identificador lógico da cor (data-color)
            const tempName = dragged.dataset.color;
            dragged.dataset.color = e.target.dataset.color;
            e.target.dataset.color = tempName;

            // Salvando mudanças no campo de input para form (usar nomes em pt-br)
            const playerDragged = document.getElementById('input_' + dragged.id);
            const playerDroped = document.getElementById('input_' + e.target.id);
            playerDragged.value = dragged.dataset.color;
            playerDroped.value = e.target.dataset.color;
        }
    });
});

volumeSlider.addEventListener('input', () => {
    audio.volume = volumeSlider.value;
    if (audio.volume == 0) {
    audio.muted = true;
    } else {
    audio.muted = false;
    }
});

function updatePage() {
    textElement.innerHTML = pages[currentPage];
}

document.getElementById("prev").addEventListener("click", () => {
    if (currentPage > 0) {
        currentPage--;
        updatePage();
    }
});

document.getElementById("next").addEventListener("click", () => {
    if (currentPage < pages.length - 1) {
        currentPage++;
        updatePage();
    }
});