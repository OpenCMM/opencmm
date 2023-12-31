<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import { loadGcodeLineData } from '$lib/db/loadGcode';
	import { loadModelShapeData } from '$lib/db/loadModel';
	import { loadEdgeData } from '$lib/db/loadEdges';

	// visualize two list of xy coordinates with d3

	let lines = [];
	let gcodeLines = [];
	/**
	 * @type {string}
	 */
	export let modelId;
	/**
	 * @type {string}
	 */
	export let processId;

	let svg;
	let margin = { top: 20, right: 20, bottom: 30, left: 40 };
	let width = 740 - margin.left - margin.right;
	let height = 700 - margin.top - margin.bottom;
	const edgeRadius = 4;
	const edgeColor = '#ffd000';
	const measuredEdgeColor = '#2bbda4';
	const lineWidth = 2;
	const gridWidth = 1;

	onMount(async () => {
		gcodeLines = await loadGcodeLineData(modelId);
		lines = await loadModelShapeData(modelId);
		const { edges, measuredEdges } = await loadEdgeData(modelId, processId);

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
			measuredDot.attr('transform', transform).attr('r', edgeRadius / transform.k);
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
			.data(edges)
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
			.style('fill', edgeColor)
			.style('opacity', 0.8);

		const measuredDot = g
			.selectAll('.measuredDot')
			.data(measuredEdges)
			.enter()
			.append('circle')
			.attr('class', 'measuredDot')
			.attr('r', edgeRadius)
			.attr('cx', function (d) {
				return x(d.x);
			})
			.attr('cy', function (d) {
				return y(d.y);
			})
			.style('fill', measuredEdgeColor);

		dot.on('mouseover', function (event, d) {
			tooltip.transition().duration(200).style('opacity', 0.9);
			tooltip
				.html(`(${d['x']}, ${d['y']}, ${d['z']})`)
				.style('left', event.pageX + 'px')
				.style('top', event.pageY - 28 + 'px');
		});

		dot.on('mouseout', function () {
			tooltip.transition().duration(200).style('opacity', 0);
		});

		measuredDot.on('mouseover', function (event, d) {
			tooltip.transition().duration(200).style('opacity', 0.9);
			tooltip
				.html(`(${d['x']}, ${d['y']}, ${d['z']})`)
				.style('left', event.pageX + 'px')
				.style('top', event.pageY - 28 + 'px');
		});

		measuredDot.on('mouseout', function () {
			tooltip.transition().duration(200).style('opacity', 0);
		});
	});
</script>

<div id="chart-container" />
