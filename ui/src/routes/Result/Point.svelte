<!-- show the result image -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';

	let loaded = false;

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'x', value: 'x' },
		{ key: 'y', value: 'y' },
		{ key: 'z', value: 'z' },
		{ key: 'rx', value: '実際のx' },
		{ key: 'ry', value: '実際のy' },
		{ key: 'rz', value: '実際のz' }
	];
	let row: { id: any; x: any; y: any; z: any; rx: any; ry: any; rz: any }[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/points`);
		const data = await res.json();
		for (const d of data['points']) {
			row.push({
				id: d[0],
				x: d[1],
				y: d[2],
				z: d[3],
				rx: d[4],
				ry: d[5],
				rz: d[6]
			});
		}
		loaded = true;
	};

	onMount(() => {
		load_table_data();
	});
</script>

<p>結果</p>
<img id="result" src={`${BACKEND_URL_LOCAL}/load/image`} alt="result" />
<div id="data-table">
	{#if !loaded}
		<p>loading...</p>
	{:else}
		<DataTable size="short" title="各頂点の座標" {headers} rows={row} />
	{/if}
</div>

<style>
	#result {
		max-width: 1000px;
	}

	#data-table {
		margin-top: 40px;
	}
</style>
