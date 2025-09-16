document.addEventListener('DOMContentLoaded', function () {
	const tooltip = document.getElementById('map-tooltip');
	const svg = document.getElementById('mapa');
	if (!svg || !tooltip) return;

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
