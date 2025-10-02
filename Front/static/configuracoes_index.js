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

openInitBtn.addEventListener('click', () => {
    audio.play();
    initDialog.showModal();
    dialogP1.style.display = 'block';
    continueBtn.style.display = 'block';
    dialogP2.style.display = 'none';
});

closeInitDialogBtn.addEventListener('click', () => {
    initDialog.close();
});

openMenuBtn.addEventListener('click', () => {
    menuDialog.showModal();
});

closeMenuDialogBtn.addEventListener('click', () => {
    menuDialog.close();
});

backBtn.addEventListener('click', () => {
    dialogP1.style.display = 'block';
    continueBtn.style.display = 'block';
    dialogP2.style.display = 'none';
});

continueBtn.addEventListener('click', () => {
    validado = validate_num_players(); // TODO: move validations to Validation class
    if (!validado) {
    alert("O número total de jogadores deve ser entre 3 e 6.");
    return;
    }

    const p4 = document.getElementById('p4');
    const cor_p4 = document.getElementById('cor_p4');
    const p5 = document.getElementById('p5');
    const cor_p5 = document.getElementById('cor_p5');
    const p6 = document.getElementById('p6');
    const cor_p6 = document.getElementById('cor_p6');
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
            const tempColor = dragged.style.backgroundColor;
            dragged.style.backgroundColor = e.target.style.backgroundColor;
            e.target.style.backgroundColor = tempColor;

            // Salvando mudanças no campo de input para form
            const playerDragged = document.getElementById('input_' + dragged.id);
            const playerDroped = document.getElementById('input_' + e.target.id);
            playerDragged.value = dragged.style.backgroundColor;
            playerDroped.value = e.target.style.backgroundColor;
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