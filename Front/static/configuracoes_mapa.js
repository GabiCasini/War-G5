
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




// melhoria para o futuro...
// mapa = document.getElementById("mapa");
// const regioes = mapa.querySelectorAll('g[id^="Regiao"]');

// regioes.forEach((regiao) => {

// regiao.addEventListener("mouseenter", () => {
	
// 	regiao.querySelectorAll("path").forEach((p) => {
// 	p.setAttribute("stroke", "#0088ff");
// 	p.setAttribute("stroke-width", "1.2");
// 	p.setAttribute("opacity", "1");
// 	});

// 	// Escurece as outras regiões
// 	regioes.forEach((outra) => {
// 	if (outra !== regiao) {
// 		outra.querySelectorAll("path").forEach((p) => {
// 		p.setAttribute("opacity", "0.4");
// 		});
// 	}
// 	});
// });

// regiao.addEventListener("mouseleave", () => {
// 	regioes.forEach((r) => {
// 	r.querySelectorAll("path").forEach((p) => {
// 		p.setAttribute("stroke", "#1F1A17");
// 		p.setAttribute("stroke-width", "0.3");
// 		p.setAttribute("opacity", "1");
// 	});
// 	});
// });
// });


