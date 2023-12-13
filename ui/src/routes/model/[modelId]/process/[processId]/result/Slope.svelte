<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayLength, displayLengthDifference } from '$lib/utils/display';

	let loaded = false;

	export let modelId: string;
	export let processId: string;
	interface Slope {
		id: number;
		angle: number;
		rangle: string;
		angleDiff: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'angle', value: $_('home.result.slope.angle') },
		{ key: 'rangle', value: $_('home.result.slope.rangle') },
		{ key: 'angleDiff', value: $_('home.result.slope.angleDiff') }
	];
	let row: Slope[] = [];
	const load_table_data = async () => {
		const res = await fetch(
			`${BACKEND_URL}/result/slopes?model_id=${modelId}&process_id=${processId}`
		);
		const data = await res.json();
		let idx = 1;
		for (const d of data['slopes']) {
			row.push({
				id: idx,
				angle: d[1],
				rangle: displayLength(d[2]),
				angleDiff: displayLengthDifference(d[1], d[2])
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
			{#if cell.key === 'angleDiff'}
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
