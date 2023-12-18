<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import { loadGcodeLineData } from '$lib/db/loadGcode';
	import { loadModelShapeData } from '$lib/db/loadModel';

	// visualize two list of xy coordinates with d3

	/**
	 * @type {string}
	 */
	export let modelId;
	let lines = [];
	let gcodeLines = [];
	// export let arcs = [];
	export let sensor = [];
	export let mtct = [];

	let svg;
	let margin = { top: 20, right: 20, bottom: 30, left: 40 };
	let width = 840 - margin.left - margin.right;
	let height = 800 - margin.top - margin.bottom;
	const edgeRadius = 4;
	const edgeColor = '#134715';
	const mtColor = '#0381ff';
	const baseHeightColor = '#03ff5f';
	const offRangeColor = '#e31e00';
	const lineWidth = 2;
	const gridWidth = 1;

	onMount(async () => {
		gcodeLines = await loadGcodeLineData(modelId);
		lines = await loadModelShapeData(modelId);

		svg = d3
			.select('#chart-container')
			.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom);

		// Add tooltips
		const tooltip = d3
			.select('#chart-container')
			.append('div')
			.attr('class', 'tooltip')
			.style('position', 'absolute')
			.style('opacity', 1);

		const g = svg
			.append('g')
			.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

		const x = d3
			.scaleLinear()
			.domain(
				// d3.extent(edges, function (d) {
				// 	return d.x;
				// })
				[-50, 150]
			)
			.range([0, height]);
		// .range([0, width]);

		const y = d3
			.scaleLinear()
			.domain(
				// d3.extent(edges, function (d) {
				// 	return d.y;
				// })
				[-150, 50]
			)
			.range([height, 0]);

		const xAxis = d3.axisBottom(x);
		const yAxis = d3.axisLeft(y);

		// Add grid lines
		const yAxisGridLine = g
			.append('g')
			.attr('class', 'grid')
			.attr('opacity', 0.2)
			.style('stroke-width', gridWidth)
			.call(d3.axisLeft(y).tickSize(-height));

		const xAxisGridLine = g
			.append('g')
			.attr('class', 'grid')
			.attr('opacity', 0.2)
			.style('stroke-width', gridWidth)
			.call(d3.axisBottom(x).tickSize(height));

		// Set up zoom behavior
		const zoom = d3.zoom().scaleExtent([0.5, 20]).on('zoom', handleZoom);

		svg.call(zoom);

		function handleZoom(event) {
			const transform = event.transform;
			const zx = transform.rescaleX(x);
			const zy = transform.rescaleY(y);
			g.select('.axis--x').call(xAxis.scale(zx));
			g.select('.axis--y').call(yAxis.scale(zy));
			dot.attr('transform', transform).attr('r', edgeRadius / transform.k);
			mtDot.attr('transform', transform).attr('r', edgeRadius / transform.k);
			line.attr('transform', transform).style('stroke-width', lineWidth / transform.k);
			yAxisGridLine.attr('transform', transform).style('stroke-width', gridWidth / transform.k);
			xAxisGridLine.attr('transform', transform).style('stroke-width', gridWidth / transform.k);
			gcodeLine.attr('transform', transform).style('stroke-width', lineWidth / transform.k);
		}

		g.append('g')
			.attr('class', 'axis axis--x')
			.attr('transform', 'translate(0,' + height + ')')
			.call(xAxis);

		g.append('g').attr('class', 'axis axis--y').call(yAxis);

		const line = g
			.selectAll('.line')
			.data(lines)
			.enter()
			.append('line')
			.attr('class', 'line')
			.attr('x1', function (d) {
				return x(d.x1);
			})
			.attr('y1', function (d) {
				return y(d.y1);
			})
			.attr('x2', function (d) {
				return x(d.x2);
			})
			.attr('y2', function (d) {
				return y(d.y2);
			})
			.style('stroke', 'black')
			.style('stroke-width', lineWidth);

		const gcodeLine = g
			.selectAll('.gcodeLine')
			.data(gcodeLines)
			.enter()
			.append('line')
			.attr('class', 'gcodeLine')
			.attr('x1', function (d) {
				return x(d.x1);
			})
			.attr('y1', function (d) {
				return y(d.y1);
			})
			.attr('x2', function (d) {
				return x(d.x2);
			})
			.attr('y2', function (d) {
				return y(d.y2);
			})
			.style('stroke', function (d) {
				if (d.feedrate < 500) {
					return '#cf1fbd';
				} else {
					return '#5b8ac7';
				}
			})
			.style('stroke-width', function (d) {
				if (d.feedrate < 500) {
					return 6;
				} else {
					return 4;
				}
			})
			.style('opacity', function (d) {
				if (d.feedrate < 500) {
					return 0.5;
				} else {
					return 0.7;
				}
			});

		const dot = g
			.selectAll('.dot')
			.data(sensor)
			.enter()
			.append('circle')
			.attr('class', 'dot')
			.attr('r', edgeRadius)
			.attr('cx', function (d) {
				return x(d.x);
			})
			.attr('cy', function (d) {
				return y(d.y);
			})
			.style('fill', function (d) {
				if (!d.output) {
					return offRangeColor;
				} else if (d.output < 1.3 && d.output > -1.3) {
					return baseHeightColor;
				} else {
					return edgeColor;
				}
			})
			.style('opacity', 0.8);

		const mtDot = g
			.selectAll('.mtDot')
			.data(mtct)
			.enter()
			.append('circle')
			.attr('class', 'mtDot')
			.attr('r', edgeRadius)
			.attr('cx', function (d) {
				return x(d.x);
			})
			.attr('cy', function (d) {
				return y(d.y);
			})
			.style('fill', mtColor);

		dot.on('mouseover', function (event, d) {
			tooltip.transition().duration(200).style('opacity', 0.9);
			tooltip
				.html(`(${d['x']}, ${d['y']}, ${d['output']}) ${d['timestamp']}`)
				.style('left', event.pageX + 'px')
				.style('top', event.pageY - 28 + 'px');
		});

		dot.on('mouseout', function () {
			tooltip.transition().duration(500).style('opacity', 0);
		});

		mtDot.on('mouseover', function (event, d) {
			tooltip.transition().duration(200).style('opacity', 0.9);
			tooltip
				.html(`(${d['x']}, ${d['y']})`)
				.style('left', event.pageX + 'px')
				.style('top', event.pageY - 28 + 'px');
		});

		mtDot.on('mouseout', function () {
			tooltip.transition().duration(500).style('opacity', 0);
		});
	});
</script>

<div id="chart-container" />
