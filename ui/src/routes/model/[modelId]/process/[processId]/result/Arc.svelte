<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { displayCoordinates, displayLengthDifference, displayRadius } from '$lib/utils/display';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	export let modelId: string;
	export let processId: string;
	let loaded = false;

	interface Arc {
		id: number;
		radius: number;
		center: string;
		rradius: string;
		radiusDiff: string;
		rcenter: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'radius', value: $_('home.result.arc.radius') },
		{ key: 'rradius', value: $_('home.result.arc.rradius') },
		{ key: 'radiusDiff', value: $_('home.result.arc.radiusDiff') },
		{ key: 'center', value: $_('home.result.arc.center') },
		{ key: 'rcenter', value: $_('home.result.arc.rcenter') }
	];
	let row: Arc[] = [];
	const load_table_data = async () => {
		const res = await fetch(
			`${BACKEND_URL}/result/arcs?model_id=${modelId}&process_id=${processId}`
		);
		const data = await res.json();
		console.log(data);
		let idx = 1;
		for (const d of data['arcs']) {
			row.push({
				id: idx,
				radius: d[1],
				rradius: displayRadius(d[5]),
				radiusDiff: displayLengthDifference(d[1], d[5]),
				center: displayCoordinates(d[2], d[3], d[4]),
				rcenter: displayCoordinates(d[6], d[7], d[8])
			});
			idx += 1;
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
	<DataTable size="short" {headers} rows={row}>
		<svelte:fragment slot="cell" let:cell>
			{#if cell.key === 'radiusDiff'}
				{#if Math.abs(parseFloat(cell.value)) < 0.05}
					<span style="color: green;">{cell.value}</span>
				{:else}
					<span style="color: red;">{cell.value}</span>
				{/if}
			{:else}
				{cell.value}
			{/if}
		</svelte:fragment>
	</DataTable>
{/if}
