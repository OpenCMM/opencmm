<script lang="ts">
	import { page } from '$app/stores';
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Content, DataTable, Link, Loading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	const modelId = $page.url.searchParams.get('id');
	let loaded = false;

	interface Process {
		id: number;
		datetime: string;
		status: number;
		measurementRange?: number;
		measureFeedrate?: number;
		moveFeedrate?: number;
		mtctLatency?: number;
	}
	const headers = [
		{ key: 'id', value: 'id' },
		{ key: 'datetime', value: $_('home.process.datetime') },
		{ key: 'status', value: $_('home.process.status') },
		{ key: 'measurementRange', value: $_('home.setup.measurementRange.label') },
		{ key: 'measureFeedrate', value: $_('home.setup.measureFeedRate.label') },
		{ key: 'moveFeedrate', value: $_('home.setup.moveFeedRate.label') },
		{ key: 'mtctLatency', value: $_('settings.mtconnect.latency') }
	];
	let processes: Process[] = [];
	onMount(() => {
		axios.get(`${BACKEND_URL}/list/processes/${modelId}`).then((res) => {
			if (res.status === 200) {
				console.log(res.data);
				for (const p of res.data['processes']) {
					processes.push({
						id: p[0],
						datetime: p[7],
						status: p[2],
						measurementRange: p[9],
						measureFeedrate: p[10],
						moveFeedrate: p[11],
						mtctLatency: p[12] || ''
					});
				}
				loaded = true;
			}
		});
	});
</script>

<Content>
	{#if !loaded}
		<Loading />
	{:else}
		<div id="process-list">
			<DataTable title={$_('home.process.title')} rows={processes} {headers}>
				<svelte:fragment slot="cell" let:cell>
					{#if cell.key === 'id'}
						<Link href={`/model/${modelId}/process/${cell.value}/result`}>
							{cell.value}
						</Link>
					{:else if cell.key === 'datetime'}
						{new Date(cell.value).toLocaleString()}
					{:else}
						{cell.value}
					{/if}
				</svelte:fragment>
			</DataTable>
		</div>
	{/if}
</Content>

<style>
	#process-list {
		margin: 1rem;
		max-width: 1000px;
	}
</style>
