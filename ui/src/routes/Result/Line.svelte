<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	import { displayLengthDifference } from './utils';

	let loaded = false;

	interface Line {
		id: number;
		a: number;
		b: number;
		length: number;
		rlength: number;
		lengthDiff: string;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'a', value: $_('home.result.line.start') },
		{ key: 'b', value: $_('home.result.line.end') },
		{ key: 'length', value: $_('home.result.line.length') },
		{ key: 'rlength', value: $_('home.result.line.rlength') },
		{ key: 'lengthDiff', value: $_('home.result.line.lengthDiff') }
	];
	let row: Line[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/result/lines`);
		const data = await res.json();
		console.log(data);
		for (const d of data['lines']) {
			row.push({
				id: d[0],
				a: d[1],
				b: d[2],
				length: d[3],
				rlength: d[4],
				lengthDiff: displayLengthDifference(d[3], d[4])
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
		<DataTable size="short" title={$_('home.result.line.title')} {headers} rows={row} />
	{/if}
</div>

<style>
	#data-table {
		margin-top: 40px;
	}
</style>
