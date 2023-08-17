<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';

	let loaded = false;

	interface Arc {
		id: number;
		radius: number;
		cx: number;
		cy: number;
		cz: number;
		rradius: number;
		rcx: number;
		rcy: number;
		rcz: number;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'radius', value: '半径' },
		{ key: 'cx', value: '中心のx' },
		{ key: 'cy', value: '中心のy' },
		{ key: 'cz', value: '中心のz' },
		{ key: 'rradius', value: '実際の半径' },
		{ key: 'rcx', value: '実際の中心のx' },
		{ key: 'rcy', value: '実際の中心のy' },
		{ key: 'rcz', value: '実際の中心のz' }
	];
	let row: Arc[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/arcs`);
		const data = await res.json();
		console.log(data);
		for (const d of data['arcs']) {
			row.push({
				id: d[0],
				radius: d[1],
				cx: d[2],
				cy: d[3],
				cz: d[4],
				rradius: d[5],
				rcx: d[6],
				rcy: d[7],
				rcz: d[8]
			});
		}
		loaded = true;
	};

	onMount(() => {
		load_table_data();
	});
</script>

<div id="data-table">
	{#if !loaded}
		<p>loading...</p>
	{:else}
		<DataTable size="short" title="孤" {headers} rows={row} />
	{/if}
</div>

<style>
	#data-table {
		margin-top: 40px;
	}
</style>
