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
		{ key: 'start', value: 'start' },
		{ key: 'end', value: 'end' },
		{ key: 'delay', value: 'delay' }
	];
	interface Delay {
		id: number;
		start: number;
		end: number;
		delay: number;
	}
	let avgDelay: number;
	let delays: Delay[] = [];

	const loadDelayBetweenLines = async () => {
		axios
			.get(`${BACKEND_URL}/result/mtconnect/avg/delay?model_id=${modelId}&process_id=${processId}`)
			.then((res) => {
				if (res.status === 200) {
					avgDelay = res.data['avg'];
					let idx = 1;
					for (const d of res.data['delay']) {
						delays.push({
							id: idx,
							start: d[0],
							end: d[1],
							delay: d[2]
						});
						idx += 1;
					}
					loaded = true;
				}
			});
	};

	onMount(() => {
		loadDelayBetweenLines();
	});
</script>

{#if !loaded}
	<InlineLoading />
{:else if delays.length === 0}
	No data available
{:else}
	<DataTable
		title="Delay between lines"
		description="Average delay between lines: {avgDelay}"
		size="short"
		{headers}
		rows={delays}
		{pageSize}
		{page}
	/>
	<Pagination
		bind:pageSize
		bind:page
		totalItems={delays.length}
		pageSizeInputDisabled
		forwardText={$_('page.forwardText')}
		backwardText={$_('page.backwardText')}
		itemRangeText={(min, max, total) => `${min}–${max} (${total})`}
		pageRangeText={(_, total) => `${total}`}
	/>
{/if}
