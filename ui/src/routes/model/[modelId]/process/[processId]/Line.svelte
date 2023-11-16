<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayLengthDifference } from '$lib/utils/display';

	let loaded = false;

	export let modelId: string;
	export let processId: string;
	interface Line {
		id: number;
		length: number;
		rlength: number;
		lengthDiff: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'length', value: $_('home.result.line.length') },
		{ key: 'rlength', value: $_('home.result.line.rlength') },
		{ key: 'lengthDiff', value: $_('home.result.line.lengthDiff') }
	];
	let row: Line[] = [];
	const load_table_data = async () => {
		const res = await fetch(
			`${BACKEND_URL}/result/lines?model_id=${modelId}&process_id=${processId}`
		);
		const data = await res.json();
		for (const d of data['lines']) {
			row.push({
				id: d[0],
				length: d[1],
				rlength: d[2],
				lengthDiff: displayLengthDifference(d[1], d[2])
			});
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
			{#if cell.key === 'lengthDiff'}
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
