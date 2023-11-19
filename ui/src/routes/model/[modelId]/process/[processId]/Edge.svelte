<!-- show the result image -->

<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayCoordinates } from '$lib/utils/display';

	export let modelId: string;
	export let processId: string;
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
		const res = await fetch(`${BACKEND_URL}/result/edges/result/combined/${modelId}/${processId}`);
		const data = await res.json();
		for (const d of data['edges']) {
			if (d[4] === null) {
				row.push({
					id: d[0],
					coordinate: displayCoordinates(d[1], d[2], d[3]),
					rcoordinate: ''
				});
			} else {
				row.push({
					id: d[0],
					coordinate: displayCoordinates(d[1], d[2], d[3]),
					rcoordinate: displayCoordinates(d[4], d[5], d[6])
				});
			}
		}
		loaded = true;
	};

	onMount(() => {
		load_table_data();
	});
</script>

{#if !loaded}
	<InlineLoading />
{:else}
	<DataTable size="short" title={$_('home.result.edge.title')} {headers} rows={row} />
{/if}
