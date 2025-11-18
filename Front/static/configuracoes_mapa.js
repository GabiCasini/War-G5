const MAPEAMENTO_REGIOES = {
	"Regiao_1": "Metropolitana",
	"Regiao_2": "Serrana",
	"Regiao_3": "Norte Fluminense",
	"Regiao_4": "Costa Verde",
	"Regiao_5": "Médio Paraíba",
	"Regiao_6": "Baixada Litorânea"
}



document.addEventListener('DOMContentLoaded', function () {
	// Configuração para aparecer o tooltip com o nome do município ao passar o mouse sobre ele
	const tooltip = document.getElementById('map-tooltip');
	const svg = document.getElementById('mapa');

	// Zoom no mapa!!
	let scale = 1;
	const minScale = 1;
	const maxScale = 4;
	const baseViewBox = svg.getAttribute('viewBox').split(' ').map(Number); // [x, y, w, h]
	let viewBoxX = baseViewBox[0];
	let viewBoxY = baseViewBox[1];
	let viewBoxW = baseViewBox[2];
	let viewBoxH = baseViewBox[3];

	// --- Pan ---
	let isPanning = false;
	let startMouse = { x: 0, y: 0 };
	let startViewBox = { x: 0, y: 0 };

	svg.addEventListener('mousedown', function (e) {
		isPanning = true;
		startMouse.x = e.clientX;
		startMouse.y = e.clientY;
		startViewBox.x = viewBoxX;
		startViewBox.y = viewBoxY;
		svg.style.cursor = 'grabbing';
	});

	document.addEventListener('mousemove', function (e) {
		if (!isPanning) return;
		const rect = svg.getBoundingClientRect();
		const dx = (e.clientX - startMouse.x) * (viewBoxW / rect.width);
		const dy = (e.clientY - startMouse.y) * (viewBoxH / rect.height);

		let newX = startViewBox.x - dx;
		let newY = startViewBox.y - dy;

		// Limites: não deixar sair do mapa
		newX = Math.max(baseViewBox[0], Math.min(newX, baseViewBox[0] + baseViewBox[2] - viewBoxW));
		newY = Math.max(baseViewBox[1], Math.min(newY, baseViewBox[1] + baseViewBox[3] - viewBoxH));

		viewBoxX = newX;
		viewBoxY = newY;
		setViewBox();
	});

	document.addEventListener('mouseup', function () {
		isPanning = false;
		svg.style.cursor = 'grab';
	});

	function setViewBox() {
		svg.setAttribute('viewBox', `${viewBoxX} ${viewBoxY} ${viewBoxW} ${viewBoxH}`);
	}

	svg.addEventListener('wheel', function (e) {
		e.preventDefault();
		const rect = svg.getBoundingClientRect();
		const mouseX = e.clientX - rect.left;
		const mouseY = e.clientY - rect.top;

		const svgX = viewBoxX + (mouseX / rect.width) * viewBoxW;
		const svgY = viewBoxY + (mouseY / rect.height) * viewBoxH;


		if (e.deltaY < 0) {
			scale = Math.min(maxScale, scale * 1.15);
		} else {
			scale = Math.max(minScale, scale / 1.15);
		}

		const newW = baseViewBox[2] / scale;
		const newH = baseViewBox[3] / scale;

		// Centraliza o zoom no ponteiro
		viewBoxX = svgX - (mouseX / rect.width) * newW;
		viewBoxY = svgY - (mouseY / rect.height) * newH;
		viewBoxW = newW;
		viewBoxH = newH;

		// Limite para não sair do mapa ao voltar ao tamanho original
		if (scale === minScale) {
			viewBoxX = baseViewBox[0];
			viewBoxY = baseViewBox[1];
			viewBoxW = baseViewBox[2];
			viewBoxH = baseViewBox[3];
		}

		setViewBox();
	}, { passive: false });

	const regiaoGroups = svg.querySelectorAll('g[id^="Regiao_"]');
	regiaoGroups.forEach(group => {
		group.querySelectorAll('path').forEach(path => {
			path.addEventListener('mouseenter', function (e) {
				const name = path.getAttribute('name');
				if (name) {
					tooltip.textContent = name;
					tooltip.style.display = 'block';
				}
			});
			path.addEventListener('mousemove', function (e) {
				tooltip.style.left = e.clientX + 10 + 'px';
				tooltip.style.top = e.clientY + 10 + 'px';
			});
			path.addEventListener('mouseleave', function () {
				tooltip.style.display = 'none';
			});
		});
	});
});


function desenharFronteiraMunicipios(nome1, nome2) {
  const svg = document.getElementById("mapa");
  const path1 = svg.querySelector(`path[name="${nome1}"]`);
  const path2 = svg.querySelector(`path[name="${nome2}"]`);

  const getCentro = (path) => {
    const box = path.getBBox();
    return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  };

  const c1 = getCentro(path1);
  const c2 = getCentro(path2);
 
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", c1.x);
  line.setAttribute("y1", c1.y);
  line.setAttribute("x2", c2.x);
  line.setAttribute("y2", c2.y);

  // Aplica estilos (com valores padrão)
  line.setAttribute("stroke", "gray");
  line.setAttribute("stroke-width", "1");
  line.setAttribute("stroke-dasharray", "3,2");
  line.setAttribute("pointer-events", "none");
  line.setAttribute("opacity", "0.7");
  // Adiciona ao SVG
  svg.insertBefore(line, svg.firstChild);

  return line;
}




desenharFronteiraMunicipios("Rio de Janeiro", "Niterói");
desenharFronteiraMunicipios("Paraíba do Sul", "Comendador Levy Gasparian");
desenharFronteiraMunicipios("Nova Friburgo", "Cordeiro");
desenharFronteiraMunicipios("Bom Jardim", "Trajano de Moraes");
desenharFronteiraMunicipios("Teresópolis", "Nova Friburgo");


function desenharNomeRegioes() {
	const svg = document.getElementById('mapa');
	if (!svg) return;

	let rotulosGroup = svg.querySelector('#rotulos_regioes');
	if (rotulosGroup) rotulosGroup.remove();
	rotulosGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
	rotulosGroup.setAttribute('id', 'rotulos_regioes');

	const regioes = svg.querySelectorAll('g[id^="Regiao_"]');
	regioes.forEach(group => {
		const box = group.getBBox();
		const cx = box.x + box.width / 2;
		const cy = box.y + box.height / 2;

		const offset = Math.max(70, box.width * 0.45);
		const xStart = cx;
		const xEnd = cx - offset;

		const id = group.id || '';
		let label = id; // vou mudar depois para o nome certinho de cada regiao
		if (MAPEAMENTO_REGIOES[id]) {
			label = MAPEAMENTO_REGIOES[id];
		}

		const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
		line.setAttribute('x1', xStart);
		line.setAttribute('y1', cy);
		line.setAttribute('x2', xEnd);
		line.setAttribute('y2', cy);
		line.setAttribute('stroke', 'black');
		line.setAttribute('stroke-width', '1');
		line.setAttribute('opacity', '0.8');
		// line.setAttribute('pointer-events', 'none');

		const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
		text.textContent = label;
		text.setAttribute('x', xEnd - 6);
		text.setAttribute('y', cy);
		text.setAttribute('fill', '#000');
		text.setAttribute('font-size', '10');
		text.setAttribute('font-family', 'sans-serif');
		text.setAttribute('text-anchor', 'end');
		text.setAttribute('alignment-baseline', 'middle');
		text.setAttribute('z-index', '10');

		text.style.paintOrder = 'stroke';
		text.style.stroke = 'white';
		text.style.strokeWidth = '0.9';

		text.classList.add('rotulo-regiao');

		text.id = id;

		text.addEventListener("mouseenter", function() {
			console.log('Hover em:', text.id);
			destacarRegiao(text.id);
		});

		console.log('Adicionando rótulo para:', text);


		rotulosGroup.appendChild(line);
		rotulosGroup.appendChild(text);
	});

	svg.insertBefore(rotulosGroup, svg.firstChild);
}



const _destaqueAnimState = new WeakMap();

function destacarRegiao(idRotulo) {
	const svg = document.getElementById('mapa');
	const regiao = svg.querySelector(`g[id="${idRotulo.replace('rotulo-regiao-', 'Regiao_')}"]`);
	if (!regiao) return;

	const paths = regiao.querySelectorAll('path');
	paths.forEach(path => {
		// Se já houver animação ativa, limpa antes de reiniciar (evita empilhar)
		const existing = _destaqueAnimState.get(path);
		if (existing) {
			if (existing.interval) clearInterval(existing.interval);
			if (existing.timeout) clearTimeout(existing.timeout);
			// restaura estilos originais antes de reiniciar
			if (existing.prevStroke !== undefined) {
				if (existing.prevStroke !== '') path.setAttribute('stroke', existing.prevStroke);
				else path.removeAttribute('stroke');
			}
			if (existing.prevStrokeWidth !== undefined) {
				if (existing.prevStrokeWidth !== '') path.setAttribute('stroke-width', existing.prevStrokeWidth);
				else path.removeAttribute('stroke-width');
			}
		}

		// armazena os valores originais (captura atual)
		const prevStroke = path.getAttribute('stroke') || '';
		const prevStrokeWidth = path.getAttribute('stroke-width') || '';

		const state = { prevStroke, prevStrokeWidth, interval: null, timeout: null };
		_destaqueAnimState.set(path, state);

		// inicia animação (toggle) e garante que não será duplicada
		let toggle = false;
		path.setAttribute('stroke', 'black');
		state.interval = setInterval(() => {
			path.setAttribute('stroke-width', toggle ? '0.287244' : '1.5');
			toggle = !toggle;
		}, 300);

		// após 2s para a animação e restaura estilos originais
		state.timeout = setTimeout(() => {
			if (state.interval) clearInterval(state.interval);

			if (state.prevStroke !== '') path.setAttribute('stroke', state.prevStroke);
			else path.removeAttribute('stroke');

			if (state.prevStrokeWidth !== '') path.setAttribute('stroke-width', state.prevStrokeWidth);
			else path.removeAttribute('stroke-width');

			_destaqueAnimState.delete(path);
		}, 2000);
	});
}


desenharNomeRegioes();


