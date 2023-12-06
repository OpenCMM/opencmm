<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	// visualize two list of xy coordinates with d3

	export let lines = [];
	// export let arcs = [];
	export let edges = [];
	export let measuredEdges = [];

	let svg;
	let margin = { top: 20, right: 20, bottom: 30, left: 40 };
	let width = 840 - margin.left - margin.right;
	let height = 800 - margin.top - margin.bottom;
	const edgeRadius = 4;

	onMount(() => {
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
		const yAxisGridLine = g.append('g')
			.attr('class', 'grid')
			.attr('opacity', 0.2)
			.call(
				d3.axisLeft(y)
					.tickSize(-height)
					.tickFormat('')
			);

		const xAxisGridLine = g.append('g')
			.attr('class', 'grid')
			.attr('opacity', 0.2)
			.call(
				d3.axisBottom(x)
					.tickSize(height)
					.tickFormat('')
			);

		// Set up zoom behavior
		const zoom = d3.zoom().scaleExtent([0.5, 10]).on('zoom', handleZoom);

		svg.call(zoom);

		function handleZoom(event) {
			const transform = event.transform;
			const zx = transform.rescaleX(x);
			const zy = transform.rescaleY(y);
			g.select('.axis--x').call(xAxis.scale(zx));
			g.select('.axis--y').call(yAxis.scale(zy));
			dot.attr('transform', transform);
			measuredDot.attr('transform', transform);
			line.attr('transform', transform);
			yAxisGridLine.attr('transform', transform);
			xAxisGridLine.attr('transform', transform);
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
			.style('stroke-width', 2);

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
			.style('fill', 'red');

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
			.style('fill', 'green');

		dot.on('mouseover', function (event, d) {
			d3.select(this).style('fill', 'blue');
			tooltip.transition().duration(200).style('opacity', 0.9);
			tooltip
				.html(`Edge: (${d['x']}, ${d['y']})`)
				.style('left', event.pageX + 'px')
				.style('top', event.pageY - 28 + 'px');
		});

		dot.on('mouseout', function (event, d) {
			d3.select(this).style('fill', 'red');
			tooltip.transition().duration(500).style('opacity', 0);
		});

		measuredDot.on('mouseover', function (event, d) {
			d3.select(this).style('fill', 'blue');
			tooltip.transition().duration(200).style('opacity', 0.9);
			tooltip
				.html(`Measured Edge: (${d['x']}, ${d['y']})`)
				.style('left', event.pageX + 'px')
				.style('top', event.pageY - 28 + 'px');
		});

		measuredDot.on('mouseout', function (event, d) {
			d3.select(this).style('fill', 'green');
			tooltip.transition().duration(500).style('opacity', 0);
		});
	});
</script>

<div id="chart-container" />
