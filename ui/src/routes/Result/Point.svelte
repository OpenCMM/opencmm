<!-- show the result image -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayCoordinates } from './utils';

	let loaded = false;

	interface Point {
		id: number;
		coordinate: string;
		rcoordinate: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'coordinate', value: $_('home.result.point.coordinate') },
		{ key: 'rcoordinate', value: $_('home.result.point.rcoordinate') }
	];
	let row: Point[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/points`);
		const data = await res.json();
		for (const d of data['points']) {
			row.push({
				id: d[0],
				coordinate: displayCoordinates(d[1], d[2], d[3]),
				rcoordinate: displayCoordinates(d[4], d[5], d[6])
			});
		}
		loaded = true;
	};

	onMount(() => {
		load_table_data();
	});
</script>

<img id="result" src={`${BACKEND_URL_LOCAL}/load/image`} alt="result" />
<div id="data-table">
	{#if !loaded}
		<p>loading...</p>
	{:else}
		<DataTable size="short" title={$_('home.result.point.title')} {headers} rows={row} />
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
