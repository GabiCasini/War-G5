//  lista onde cada elemento é uma lista que possui informações de cada territorio do jogo -> [nome, regiao, lista de fronteiras]
const territoriosFronteiras = [
  ["Rio de Janeiro", "Regiao_1", ["Nova Iguaçu", "Mesquita", "São João de Meriti", "Niterói"]],
  ["Nova Iguaçu", "Regiao_1", ["Rio de Janeiro", "Mesquita", "Seropédica"]],
  ["Mesquita", "Regiao_1", ["Rio de Janeiro", "Nova Iguaçu", "São João de Meriti"]],
  ["São João de Meriti", "Regiao_1", ["Rio de Janeiro", "Mesquita"]], 
  ["Seropédica", "Regiao_2", ["Nova Iguaçu", "Queimados", "Japeri", "Paracambi"]],
  ["Queimados", "Regiao_2", ["Japeri", "Seropédica"]],
  ["Japeri", "Regiao_2", ["Miguel Pereira", "Queimados", "Seropédica", "Paracambi"]],
  ["Paracambi", "Regiao_2", ["Miguel Pereira", "Eng Paulo de Frontin", "Seropédica", "Japeri"]],
  ["Miguel Pereira", "Regiao_2", ["Paty do Alferes", "Vassouras", "Eng Paulo de Frontin", "Japeri", "Paracambi"]],
  ["Eng Paulo de Frontin", "Regiao_2", ["Vassouras", "Miguel Pereira", "Paracambi"]],
  ["Vassouras", "Regiao_2", ["Paty do Alferes", "Miguel Pereira", "Eng Paulo de Frontin", "Paraíba do Sul"]],
  ["Paty do Alferes", "Regiao_2", ["Vassouras", "Miguel Pereira", "Paraíba do Sul"]],
  ["Paraíba do Sul", "Regiao_2", ["Paty do Alferes", "Vassouras", "Comendador Levy Gasparian"]],
  ["Comendador Levy Gasparian", "Regiao_3", ["Três Rios", "Paraíba do Sul"]],
  ["Três Rios", "Regiao_3", ["Comendador Levy Gasparian", "Sapucaia", "Areal"]],
  ["Areal", "Regiao_3", ["Petrópolis", "Três Rios"]],
  ["Sapucaia", "Regiao_3", ["Três Rios", "Teresópolis", "São José do Vale do Rio Preto"]],
  ["Petrópolis", "Regiao_3", ["Areal", "Teresópolis", "Magé", "Guapimirim"]],
  ["Teresópolis", "Regiao_3", ["Sapucaia", "Petrópolis", "Cachoeiras de Macacu", "Guapimirim", "Nova Friburgo"]],
  ["Cachoeiras de Macacu", "Regiao_3", ["Teresópolis", "Guapimirim", "Itaboraí"]],
  ["São José do Vale do Rio Preto", "Regiao_4", ["Sapucaia", "Sumidouro"]],
  ["Sumidouro", "Regiao_4", ["São José do Vale do Rio Preto", "Carmo", "Duas Barras", "Nova Friburgo"]],
  ["Nova Friburgo", "Regiao_4", ["Teresópolis", "Sumidouro", "Duas Barras", "Bom Jardim", "Cordeiro", "Trajano de Moraes"]],
  ["Bom Jardim", "Regiao_4", ["Duas Barras", "Nova Friburgo", "Macuco"]],
  ["Duas Barras", "Regiao_4", ["Cantagalo", "Carmo", "Sumidouro", "Nova Friburgo", "Bom Jardim"]],
  ["Carmo", "Regiao_4", ["Cantagalo", "Duas Barras", "Sumidouro"]],
  ["Cantagalo", "Regiao_4", ["Duas Barras", "Carmo", "Macuco", "São Sebastião do Alto", "Itaocara", "Santo Antônio de Pádua"]],
  ["Macuco", "Regiao_4", ["Cantagalo", "São Sebastião do Alto", "Bom Jardim"]],
  ["São Sebastião do Alto", "Regiao_4", ["Cantagalo", "Macuco", "Itaocara"]],
  ["Itaocara", "Regiao_4", ["Cantagalo", "São Sebastião do Alto", "Santo Antônio de Pádua", "Cambuci"]],
  ["Santo Antônio de Pádua", "Regiao_4", ["Cantagalo", "Itaocara", "Cambuci"]],
  ["Cambuci", "Regiao_4", ["Santo Antônio de Pádua", "Itaocara"]],
  ["Magé", "Regiao_5", ["Petrópolis", "Guapimirim"]],
  ["Guapimirim", "Regiao_5", ["Petrópolis", "Magé", "Teresópolis", "Cachoeiras de Macacu", "Itaboraí"]],
  ["Itaboraí", "Regiao_5", ["Guapimirim", "Cachoeiras de Macacu", "São Gonçalo", "Maricá"]],
  ["São Gonçalo", "Regiao_5", ["Itaboraí", "Maricá", "Niterói"]],
  ["Maricá", "Regiao_5", ["Itaboraí", "São Gonçalo", "Niterói"]],
  ["Niterói", "Regiao_5", ["São Gonçalo", "Maricá", "Rio de Janeiro"]],
  ["Cordeiro", "Regiao_6", ["Nova Friburgo", "Trajano de Moraes"]],
  ["Trajano de Moraes", "Regiao_6", ["Nova Friburgo", "Cordeiro", "Macaé"]],
  ["Macaé", "Regiao_6", ["Trajano de Moraes", "Casimiro de Abreu"]],
  ["Casimiro de Abreu", "Regiao_6", ["Macaé"]]
]


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