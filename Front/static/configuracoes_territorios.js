let territorios = [];
let territorioSelecionado = null;
let possiveisAlvosAtaque = [];
let possiveisAlvosReposicionamento = [];

function colorirTerritoriosNoMapa() {
  const svg = document.getElementById("mapa");
  if (!svg) return;
  territorios.forEach((territorio) => {
    const path = Array.from(svg.querySelectorAll("path")).find(
      (p) => p.getAttribute("name") === territorio.nome
    );
    if (path) {
      // console.log("Território encontrado no mapa:", territorio.nome);
      let cor = players.find((p) => p.cor === territorio.cor_jogador)?.corHex;
      // console.log("Cor do território", territorio.nome, ":", cor);
      if (!cor) cor = "#ccc"; // Cor padrão se não houver dono
      path.setAttribute("fill", cor);
    }
  });
}

function desenharExercitosNoMapa() {
  const svg = document.getElementById("mapa");
  if (!svg) return;

  Array.from(svg.querySelectorAll(".exercito-marker")).forEach((e) =>
    e.remove()
  );

  territorios.forEach((territorio) => {
    const path = Array.from(svg.querySelectorAll("path")).find(
      (p) => p.getAttribute("name") === territorio.nome
    );
    if (!path) return;

    const bbox = path.getBBox();
    const cx = bbox.x + bbox.width / 2;
    const cy = bbox.y + bbox.height / 2;

    const circle = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "circle"
    );
    circle.setAttribute("cx", cx);
    circle.setAttribute("cy", cy);
    circle.setAttribute("r", 5);
    circle.setAttribute("fill", "#fff");
    circle.setAttribute("stroke", "#222");
    circle.setAttribute("stroke-width", "1");
    circle.setAttribute("class", "exercito-marker");

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", cx);
    text.setAttribute("y", cy);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("dominant-baseline", "middle");
    text.setAttribute("font-size", "7");
    text.setAttribute("font-family", "Arial, sans-serif");
    text.setAttribute("fill", "#222");
    text.setAttribute("class", "exercito-marker");
    text.textContent = territorio.exercitos;

    svg.appendChild(circle);
    svg.appendChild(text);
  });
}

function ativarCliquePosicionamento() {
  const svg = document.getElementById("mapa");
  if (!svg) return;
  const paths = svg.querySelectorAll("path[name]");

  paths.forEach((path) => {
    path.style.cursor = "pointer";

    path.addEventListener("click", function handler(e) {
      e.stopPropagation();

      const nomeTerritorio = path.getAttribute("name");

      if (faseAtual === "posicionamento") {
        if (!verificaDonoTerritorio(nomeTerritorio, jogadorAtual)) return;

        posicionarExercitos(nomeTerritorio);
      } else if (faseAtual === "ataque") {
        if (territorioSelecionado !== nomeTerritorio) {
          if (possiveisAlvosAtaque.includes(nomeTerritorio)) {
            ataqueTerritorio(territorioSelecionado, nomeTerritorio);
            territorioSelecionado = null;
            possiveisAlvosAtaque = [];
            removerTodosDestaqueTerritorio();

            return;
          }
        }

        if (!verificaDonoTerritorio(nomeTerritorio, jogadorAtual)) return;

        possiveisAlvosAtaque = [];
        selecionarTerritorio(nomeTerritorio);

        removerTodosDestaqueTerritorio();
        let listaPossiveisAtaques = obterTerritoriosParaAtaque(
          jogadorAtual,
          nomeTerritorio
        );

        listaPossiveisAtaques.forEach((ataque) => {
          if (ataque.de === nomeTerritorio) {
            possiveisAlvosAtaque.push(ataque.para);
            destacarTerritorio(ataque.para);
          }
        });
      } else if (faseAtual === "reposicionamento") {
        e.stopPropagation();

        if (territorioSelecionado !== nomeTerritorio) {
          if (possiveisAlvosReposicionamento.includes(nomeTerritorio)) {
            reposicionarTerritorio(territorioSelecionado, nomeTerritorio);
            territorioSelecionado = null;
            possiveisAlvosReposicionamento = [];
            removerTodosDestaqueTerritorio();
          }
        }

        if (!verificaDonoTerritorio(nomeTerritorio, jogadorAtual)) return;

        possiveisAlvosReposicionamento = [];
        selecionarTerritorio(nomeTerritorio);
        removerTodosDestaqueTerritorio();

        let listaPossiveisReposicionamentos = obterTerritoriosReposicionamento(
          jogadorAtual,
          nomeTerritorio
        );

        listaPossiveisReposicionamentos.forEach((reposicionamento) => {
          if (reposicionamento.de === nomeTerritorio) {
            possiveisAlvosReposicionamento.push(reposicionamento.para);
            destacarTerritorio(reposicionamento.para);
          }
        });
      }
    });
  });
}

// Ativa ao carregar a página
window.addEventListener("DOMContentLoaded", ativarCliquePosicionamento);

function adicionarExercitos(nome, quantidade) {
  const territorio = territorios.find((t) => t.nome === nome);
  if (territorio) {
    territorio.exercitos += quantidade;
    desenharExercitosNoMapa();
  }
}

function verificaDonoTerritorio(territorioNome, jogadorCor) {
  const territorio = territorios.find((t) => t.nome === territorioNome);
  return territorio && territorio.cor_jogador === jogadorCor;
}

function obterTerritoriosParaAtaque(jogador, territorioNome) {
  const territoriosAtacantes = territorios.filter(t => t.jogador_id === jogador && t.nome === territorioNome && t.exercitos >= 2);
  const ataquesPossiveis = [];

  territoriosAtacantes.forEach((territorio) => {
    const vizinhos = obterTerritoriosVizinhos(territorio.nome);
    vizinhos.forEach((vizinho) => {
      if (vizinho.jogador_id !== jogador) {
        ataquesPossiveis.push({ de: territorio.nome, para: vizinho.nome });
      }
    });
  });

  return ataquesPossiveis;
}

function obterTerritoriosReposicionamento(jogador, territorioNome) {
  const territoriosReposicionamento = territorios.filter(
    (t) =>
      t.jogador_id === jogador && t.nome === territorioNome && t.exercitos > 1
  );
  const reposicionamentosPossiveis = [];
  territoriosReposicionamento.forEach((territorio) => {
    const vizinhos = obterTerritoriosVizinhos(territorio.nome);
    vizinhos.forEach((vizinho) => {
      if (vizinho.jogador_id === jogador) {
        reposicionamentosPossiveis.push({
          de: territorio.nome,
          para: vizinho.nome,
        });
      }
    });
  });

  return reposicionamentosPossiveis;
}

function obterTerritoriosVizinhos(territorioNome) {
  console.log(territorios);
  const territorioInfo = territorios.find((t) => t.nome === territorioNome);
  if (!territorioInfo) return [];
  const fronteiras = territorioInfo.fronteiras;

  // console.log(fronteiras, territorioNome);
  return territorios.filter((t) => fronteiras.includes(t.nome));
}

function destacarTerritorio(nomeTerritorio) {
  const svg = document.getElementById("mapa");
  if (!svg) return;
  // console.log("Destacando território:", nomeTerritorio);
  const path = Array.from(svg.querySelectorAll("path")).find(
    (p) => p.getAttribute("name") === nomeTerritorio
  );
  if (path) {
    // path.setAttribute('stroke', '#FFD700');
    // path.setAttribute('stroke-width', '3');
    // path.classList.remove('blinking_territorio');
    path.classList.add("blinking_territorio");
  }
}

function removerDestaqueTerritorio(nomeTerritorio) {
  const svg = document.getElementById("mapa");
  if (!svg) return;
  const path = Array.from(svg.querySelectorAll("path")).find(
    (p) => p.getAttribute("name") === nomeTerritorio
  );
  if (path) {
    // path.setAttribute('stroke', '#1F1A17');
    // path.setAttribute('stroke-width', '0.3');
    path.classList.remove("blinking_territorio");
  }
}

function removerTodosDestaqueTerritorio() {
  for (const territorio of territorios) {
    removerDestaqueTerritorio(territorio.nome);
    // deselecionarTerritorio(territorio.nome);
  }
}

function selecionarTerritorio(nomeTerritorio) {
  territorioSelecionado = nomeTerritorio;
  const svg = document.getElementById("mapa");
  if (!svg) return;
  const path = Array.from(svg.querySelectorAll("path"));
  for (const p of path) {
    p.classList.remove("selecionado_territorio");

    if (p.getAttribute("name") === nomeTerritorio) {
      p.classList.add("selecionado_territorio");
    }
  }
}

function refreshTerritorios() {
  removerTodosDestaqueTerritorio();
  territorioSelecionado = null;
  possiveisAlvosAtaque = [];
  possiveisAlvosReposicionamento = [];
}

function posicionarExercitos(nomeTerritorio) {

  let maximoExercitos = players.find(p => p.cor === jogadorAtual).exercitosDisponiveisPosicionamento;

  if (maximoExercitos <= 0) {
    alert("Você não tem exércitos disponíveis para posicionar.");
    return;
  }

  const dialog = document.getElementById('posicionamentoDialog');
  const form = document.getElementById('posicionamentoForm');
  const titulo = document.getElementById('posicionamentoTitulo');
  const label = document.getElementById('posicionamentoLabel');
  const input = document.getElementById('posicionamentoQtd');
  const btnCancel = dialog.querySelector('.btn-cancelar');
  const btnDecrement = dialog.querySelector('.btn-decrement');
  const btnIncrement = dialog.querySelector('.btn-increment');

  titulo.textContent = `Posicionar em ${nomeTerritorio}`;
  label.textContent = `Quantos exércitos deseja posicionar em ${nomeTerritorio}?`;
  input.value = 1;
  input.min = 1;

  btnDecrement.onclick = () => {
    let val = parseInt(input.value, 10);
    if (val > 1) {
      input.value = val - 1;
    }
  };

  btnIncrement.onclick = () => {
    if (parseInt(input.value, 10) >= maximoExercitos) return;
    input.value = parseInt(input.value, 10) + 1;
  };
  
  dialog.showModal();

  const cleanup = () => {
    dialog.close();
    form.onsubmit = null;
    btnCancel.onclick = null;
    btnDecrement.onclick = null;
    btnIncrement.onclick = null;
  };

  form.onsubmit = (e) => {
    e.preventDefault();
    const qtd = parseInt(input.value, 10);
    if (!isNaN(qtd) && qtd > 0) {
      console.log(`Posicionando ${qtd} exércitos em "${nomeTerritorio}"`);
      postPosicionarExercitos(jogadorAtual, nomeTerritorio, qtd);
    }
    cleanup();
  };

  btnCancel.onclick = cleanup;
}

function ataqueTerritorio(territorioDe, territorioPara) {
  
  const dialog = document.getElementById('ataqueDialog');
  const form = document.getElementById('ataqueForm');
  const titulo = document.getElementById('ataqueTitulo');
  const label = document.getElementById('ataqueLabel');
  const btnCancel = dialog.querySelector('.btn-cancelar');

  const territorioDeObj = territorios.find(t => t.nome === territorioDe);
  const territorioParaObj = territorios.find(t => t.nome === territorioPara);
  
  if (!territorioDeObj || !territorioParaObj) return;

  const exercitosAtacantes = territorioDeObj.exercitos >= 4 ? 3 : (territorioDeObj.exercitos - 1);
  
  titulo.textContent = `Confirmar Ataque`;
  label.innerHTML = `Atacar <strong>${territorioPara}</strong> 
                       usando <strong>${territorioDeObj.exercitos}</strong> exército(s) de <strong>${territorioDe}</strong> ? <br> 
                       (Ataque: ${territorioDeObj.exercitos}) (Defesa: ${territorioParaObj.exercitos})`;

  dialog.showModal();

  const cleanup = () => {
    dialog.close();
    form.onsubmit = null;
    btnCancel.onclick = null;
  };

  form.onsubmit = (e) => {
    e.preventDefault();
    console.log(`Ataque de "${territorioDe}" para "${territorioPara}" confirmado.`);
    postAtaque(jogadorAtual, territorioDe, territorioPara);
    cleanup();
  };

  btnCancel.onclick = cleanup;
}

function reposicionarTerritorio(territorioDe, territorioPara) {
  const dialog = document.getElementById('reposicionamentoDialog');
  const form = document.getElementById('reposicionamentoForm');
  const titulo = document.getElementById('reposicionamentoTitulo');
  const label = document.getElementById('reposicionamentoLabel');
  const input = document.getElementById('reposicionamentoQtd');
  const btnCancel = dialog.querySelector('.btn-cancelar');
  const btnDecrement = dialog.querySelector('.btn-decrement');
  const btnIncrement = dialog.querySelector('.btn-increment');

  const territorioDeObj = territorios.find(t => t.nome === territorioDe);
  const maxQtd = territorioDeObj ? (territorioDeObj.exercitos - 1) : 1;

  titulo.textContent = 'Reposicionar Exércitos';
  label.textContent = `Mover quantos exércitos de ${territorioDe} para ${territorioPara}?`;
  input.value = 1;
  input.min = 1;

  btnDecrement.onclick = () => {
    let val = parseInt(input.value, 10);
    if (val > 1) {
      input.value = val - 1;
    }
  };

  btnIncrement.onclick = () => {
    if (parseInt(input.value, 10) >= maxQtd) return;
    input.value = parseInt(input.value, 10) + 1;
  };

  dialog.showModal();

  const cleanup = () => {
    dialog.close();
    form.onsubmit = null;
    btnCancel.onclick = null;
    btnDecrement.onclick = null;
    btnIncrement.onclick = null;
  };

  form.onsubmit = (e) => {
    e.preventDefault();
    const exercitosReposicionar = parseInt(input.value, 10);
    if (isNaN(exercitosReposicionar) || exercitosReposicionar <= 0) {
      alert("sem exercitos...");
      return;
    }
    
    console.log(`Reposicionamento de "${territorioDe}" para "${territorioPara}" com ${exercitosReposicionar}`);
    postReposicionamento(jogadorAtual, territorioDe, territorioPara, exercitosReposicionar);
    cleanup();
  };

  btnCancel.onclick = cleanup;
}