<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayLength, displayLengthDifference } from '$lib/utils/display';

	let loaded = false;

	export let modelId: string;
	export let processId: string;
	interface Step {
		id: number;
		height: number;
		rheight: string;
		heightDiff: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'height', value: $_('home.result.step.height') },
		{ key: 'rheight', value: $_('home.result.step.rheight') },
		{ key: 'heightDiff', value: $_('home.result.step.heightDiff') }
	];
	let row: Step[] = [];
	const load_table_data = async () => {
		const res = await fetch(
			`${BACKEND_URL}/result/steps?model_id=${modelId}&process_id=${processId}`
		);
		const data = await res.json();
		let idx = 1;
		for (const d of data['steps']) {
			row.push({
				id: idx,
				height: d[1],
				rheight: displayLength(d[2]),
				heightDiff: displayLengthDifference(d[1], d[2])
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
			{#if cell.key === 'heightDiff'}
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
