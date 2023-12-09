<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	export let modelId: string;
	export let processId: string;
	let loaded = false;

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'line', value: 'line' },
		{ key: 'start', value: 'start' },
		{ key: 'end', value: 'end' },
	];
	interface MtcnLine {
		id: number;
		line: number;
		start: string;
		end:  string;
	}
	let lines: MtcnLine[] = [];

	const loadMtcnLines = async () => {
		axios
			.get(`${BACKEND_URL}/result/mtconnect/lines?model_id=${modelId}&process_id=${processId}`)
			.then((res) => {
				if (res.status === 200) {
					const data = res.data;
					let idx = 1;
					for (const d of data['lines']) {
						lines.push({
							id: idx,
							line: d[0],
							start: d[1],
							end: d[2]
						});
						idx += 1;
					}
					loaded = true;
				}
			});
	};

	onMount(() => {
		loadMtcnLines();
	});
</script>

{#if !loaded}
	<InlineLoading />
{:else if lines.length === 0}
	No line data
{:else}
	<DataTable size="short" {headers} rows={lines} />
{/if}
