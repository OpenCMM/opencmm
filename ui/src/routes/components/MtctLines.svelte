<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { DataTable, InlineLoading, Pagination } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';
	import { onMount } from 'svelte';

	export let modelId: string;
	export let processId: string;
	let loaded = false;

	let pageSize = 10;
	let page = 1;
	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'line', value: 'line' },
		{ key: 'start', value: 'start' },
		{ key: 'end', value: 'end' }
	];
	interface MtcnLine {
		id: number;
		line: number;
		start: string;
		end: string;
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
	<DataTable title="MTConnect Time" size="short" {headers} rows={lines} {pageSize} {page} />
	<Pagination
		bind:pageSize
		bind:page
		totalItems={lines.length}
		pageSizeInputDisabled
		forwardText={$_('page.forwardText')}
		backwardText={$_('page.backwardText')}
		itemRangeText={(min, max, total) => `${min}–${max} (${total})`}
		pageRangeText={(_, total) => `${total}`}
	/>
{/if}
