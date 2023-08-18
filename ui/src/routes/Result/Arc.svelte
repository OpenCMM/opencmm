<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayCoordinates } from './utils';

	let loaded = false;

	interface Arc {
		id: number;
		radius: number;
		center: string;
		rradius: number;
		rcenter: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'radius', value: $_('home.result.arc.radius') },
		{ key: 'center', value: $_('home.result.arc.center') },
		{ key: 'rradius', value: $_('home.result.arc.rradius') },
		{ key: 'rcenter', value: $_('home.result.arc.rcenter') }
	];
	let row: Arc[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/arcs`);
		const data = await res.json();
		for (const d of data['arcs']) {
			row.push({
				id: d[0],
				radius: d[1],
				center: displayCoordinates(d[2], d[3], d[4]),
				rradius: d[5],
				rcenter: displayCoordinates(d[6], d[7], d[8])
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
		<DataTable size="short" title={$_('home.result.arc.title')} {headers} rows={row} />
	{/if}
</div>

<style>
	#data-table {
		margin-top: 40px;
	}
</style>
