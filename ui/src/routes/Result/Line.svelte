<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';

	let loaded = false;

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'a', value: '始点' },
		{ key: 'b', value: '終点' },
		{ key: 'length', value: '長さ' },
		{ key: 'rlength', value: '実際の長さ' }
	];
	let row: { id: any; a: any; b: any; length: any; rlength: any }[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/lines`);
		const data = await res.json();
		for (const d of data['lines']) {
			row.push({
				id: d[0],
				a: d[1],
				b: d[2],
				length: d[3],
				rlength: d[4]
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
		<DataTable size="short" title="線" {headers} rows={row} />
	{/if}
</div>

<style>
	#data-table {
		margin-top: 40px;
	}
</style>
