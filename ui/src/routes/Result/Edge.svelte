<!-- show the result image -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayCoordinates } from './utils';

	let loaded = false;

	interface Edge {
		id: number;
		coordinate: string;
		rcoordinate: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'coordinate', value: $_('home.result.edge.coordinate') },
		{ key: 'rcoordinate', value: $_('home.result.edge.rcoordinate') }
	];
	let row: Edge[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/edges`);
		const data = await res.json();
		for (const d of data['edges']) {
			row.push({
				id: d[0],
				coordinate: displayCoordinates(d[2], d[3], d[4]),
				rcoordinate: displayCoordinates(d[5], d[6], d[7])
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
		<DataTable size="short" title={$_('home.result.edge.title')} {headers} rows={row} />
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
