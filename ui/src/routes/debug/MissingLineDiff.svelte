<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { _ } from 'svelte-i18n';
	import { DataTable, InlineLoading, Pagination } from 'carbon-components-svelte';
	import { onMount } from 'svelte';

	export let modelId: string;
	export let processId: string;
	let loaded = false;

	let pageSize = 10;
	let page = 1;
	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'line', value: 'line' },
		{ key: 'diff', value: 'diff' }
	];
	interface Diff {
		id: number;
		line: number;
		diff: number;
	}
	let avgDiff: number;
	let diffs: Diff[] = [];

	const loadMissingLineDiff = async () => {
		axios
			.get(
				`${BACKEND_URL}/result/mtconnect/missing/lines/travel/time/diff?model_id=${modelId}&process_id=${processId}`
			)
			.then((res) => {
				if (res.status === 200) {
					avgDiff = res.data['avg'];
					let idx = 1;
					for (const d of res.data['diff']) {
						diffs.push({
							id: idx,
							line: d[0],
							diff: d[1]
						});
						idx += 1;
					}
					loaded = true;
				}
			});
	};

	onMount(() => {
		loadMissingLineDiff();
	});
</script>

{#if !loaded}
	<InlineLoading />
{:else if diffs.length === 0}
	No data available
{:else}
	<DataTable
		title="Missing Line Diff"
		description="Average missing line differences: {avgDiff}"
		size="short"
		{headers}
		rows={diffs}
		{pageSize}
		{page}
	/>
	<Pagination
		bind:pageSize
		bind:page
		totalItems={diffs.length}
		pageSizeInputDisabled
		forwardText={$_('page.forwardText')}
		backwardText={$_('page.backwardText')}
		itemRangeText={(min, max, total) => `${min}–${max} (${total})`}
		pageRangeText={(_, total) => `${total}`}
	/>
{/if}
