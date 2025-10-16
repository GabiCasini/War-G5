const territorios = [
  { nome: "Nova Iguaçu", jogador: "", exercitos: 1 },
  { nome: "Mesquita", jogador: "", exercitos: 1 },
  { nome: "São João de Meriti", jogador: "", exercitos: 1 },
  { nome: "Rio de Janeiro", jogador: "", exercitos: 1 },
  { nome: "Guapimirim", jogador: "", exercitos: 1 },
  { nome: "Itaboraí", jogador: "", exercitos: 1 },
  { nome: "Magé", jogador: "", exercitos: 1 },
  { nome: "Maricá", jogador: "", exercitos: 1 },
  { nome: "Niterói", jogador: "", exercitos: 1 },
  { nome: "São Gonçalo", jogador: "", exercitos: 1 },
  { nome: "Paracambi", jogador: "", exercitos: 1 },
  { nome: "Seropédica", jogador: "", exercitos: 1 },
  { nome: "Eng Paulo de Frontin", jogador: "", exercitos: 1 },
  { nome: "Japeri", jogador: "", exercitos: 1 },
  { nome: "Miguel Pereira", jogador: "", exercitos: 1 },
  { nome: "Queimados", jogador: "", exercitos: 1 },
  { nome: "Vassouras", jogador: "", exercitos: 1 },
  { nome: "Paty do Alferes", jogador: "", exercitos: 1 },
  { nome: "Paraíba do Sul", jogador: "", exercitos: 1 },
  { nome: "Petrópolis", jogador: "", exercitos: 1 },
  { nome: "Areal", jogador: "", exercitos: 1 },
  { nome: "Comendador Levy Gasparian", jogador: "", exercitos: 1 },
  { nome: "Três Rios", jogador: "", exercitos: 1 },
  { nome: "Sapucaia", jogador: "", exercitos: 1 },
  { nome: "Teresópolis", jogador: "", exercitos: 1 },
  { nome: "Cachoeiras de Macacu", jogador: "", exercitos: 1 },
  { nome: "Sumidouro", jogador: "", exercitos: 1 },
  { nome: "Carmo", jogador: "", exercitos: 1 },
  { nome: "São José do Vale do Rio Preto", jogador: "", exercitos: 1 },
  { nome: "Nova Friburgo", jogador: "", exercitos: 1 },
  { nome: "Santo Antônio de Pádua", jogador: "", exercitos: 1 },
  { nome: "Bom Jardim", jogador: "", exercitos: 1 },
  { nome: "Cantagalo", jogador: "", exercitos: 1 },
  { nome: "Duas Barras", jogador: "", exercitos: 1 },
  { nome: "Itaocara", jogador: "", exercitos: 1 },
  { nome: "Macuco", jogador: "", exercitos: 1 },
  { nome: "São Sebastião do Alto", jogador: "", exercitos: 1 },
  { nome: "Cambuci", jogador: "", exercitos: 1 },
  { nome: "Cordeiro", jogador: "", exercitos: 1 },
  { nome: "Trajano de Moraes", jogador: "", exercitos: 1 },
  { nome: "Casimiro de Abreu", jogador: "", exercitos: 1 },
  { nome: "Macaé", jogador: "", exercitos: 1 }
];

function desenharExercitosNoMapa() {
  const svg = document.getElementById('mapa');
  if (!svg) return;

  Array.from(svg.querySelectorAll('.exercito-marker')).forEach(e => e.remove());

  territorios.forEach(territorio => {
    const path = Array.from(svg.querySelectorAll('path')).find(p => p.getAttribute('name') === territorio.nome);
    if (!path) return;

    const bbox = path.getBBox();
    const cx = bbox.x + bbox.width / 2;
    const cy = bbox.y + bbox.height / 2;

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx);
    circle.setAttribute('cy', cy);
    circle.setAttribute('r', 6);
    circle.setAttribute('fill', '#fff');
    circle.setAttribute('stroke', '#222');
    circle.setAttribute('stroke-width', '1');
    circle.setAttribute('class', 'exercito-marker');

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', cx);
    text.setAttribute('y', cy + 5);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-size', '8');
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('fill', '#222');
    text.setAttribute('class', 'exercito-marker');
    text.textContent = territorio.exercitos;

    svg.appendChild(circle);
    svg.appendChild(text);
  });
}

desenharExercitosNoMapa()

// Adiciona evento de clique nos territórios do mapa para adicionar exércitos
function ativarCliqueAdicionarExercitos() {
  const svg = document.getElementById('mapa');
  if (!svg) return;
  const paths = svg.querySelectorAll('path[name]');
  paths.forEach(path => {
    path.style.cursor = 'pointer';
    path.addEventListener('click', function handler(e) {
      e.stopPropagation();
      const nome = path.getAttribute('name');
      const valor = prompt(`Adicionar quantos exércitos para "${nome}"?`, "1");
      const qtd = parseInt(valor, 10);
      if (!isNaN(qtd) && qtd !== 0) {
        adicionarExercitos(nome, qtd);
      }
    });
  });
}

// Ativa ao carregar a página
window.addEventListener('DOMContentLoaded', ativarCliqueAdicionarExercitos);


function adicionarExercitos(nome, quantidade) {
  const territorio = territorios.find(t => t.nome === nome);
  if (territorio) {
    territorio.exercitos += quantidade;
    desenharExercitosNoMapa();
  }
}