<script lang="ts">
	import { ProgressBar } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import Chart from './Chart.svelte';

	let loaded = false;
	interface Edge {
		x: number;
		y: number;
	}

	let edges: Edge[] = [];
	let measuredEdges: Edge[] = [];
	const modelId = $page.url.searchParams.get('id');
	const processId = $page.url.searchParams.get('process');
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
		loaded = true;
	};
	onMount(() => {
		load_edge_data();
	});
</script>

{#if !loaded}
	<ProgressBar helperText="Loading..." />
{:else}
	<Chart {edges} {measuredEdges} />
{/if}