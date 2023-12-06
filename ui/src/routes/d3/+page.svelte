<script lang="ts">
	import { ProgressBar } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import Chart from './Chart.svelte';

	let shapeLoaded = false;
	let edgeLoaded = false;
	interface Edge {
		x: number;
		y: number;
	}

	interface Line {
		x1: number;
		y1: number;
		x2: number;
		y2: number;
	}

	interface Arc {
		radius: number;
		cx: number;
		cy: number;
	}

	let lines: Line[] = [];
	let arcs: Arc[] = [];
	let edges: Edge[] = [];
	let measuredEdges: Edge[] = [];
	const modelId = $page.url.searchParams.get('id');
	const processId = $page.url.searchParams.get('process');
	const load_model_shape_data = async () => {
		const res = await fetch(`${BACKEND_URL}/model/shapes/${modelId}`);
		const data = await res.json();
		console.log(data);

		for (const d of data['lines']) {
			lines.push({
				x1: d[0],
				y1: d[1],
				x2: d[2],
				y2: d[3]
			});
		}
		for (const d of data['arcs']) {
			arcs.push({
				radius: d[0],
				cx: d[1],
				cy: d[2]
			});
		}
		shapeLoaded = true;
	};
	const load_edge_data = async () => {
		const res = await fetch(`${BACKEND_URL}/result/edges/result/combined/${modelId}/${processId}`);
		const data = await res.json();
		console.log(data);
		for (const d of data['edges']) {
			edges.push({
				x: d[1],
				y: d[2]
			});
			if (d[4] !== null) {
				measuredEdges.push({
					x: d[4],
					y: d[5]
				});
			}
		}
		edgeLoaded = true;
	};
	onMount(() => {
		load_edge_data();
		load_model_shape_data();
	});
</script>

{#if !shapeLoaded || !edgeLoaded}
	<ProgressBar helperText="Loading..." />
{:else}
	<Chart {lines} {arcs} {edges} {measuredEdges} />
{/if}
