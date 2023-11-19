<script lang="ts">
	import { page } from '$app/stores';
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { DataTable, Link, Loading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	const modelId = $page.url.searchParams.get('id');
	let loaded = false;

	interface Process {
		id: number;
		datetime: string;
		status: number;
	}
	const headers = [
		{ key: 'id', value: 'id' },
		{ key: 'datetime', value: $_('home.process.datetime') },
		{ key: 'status', value: $_('home.process.status') }
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
						status: p[2]
					});
				}
				loaded = true;
			}
		});
	});
</script>

{#if !loaded}
	<Loading />
{:else}
	<div id="process-list">
		<DataTable title={$_('home.process.title')} rows={processes} {headers}>
			<svelte:fragment slot="cell" let:cell>
				{#if cell.key === 'id'}
					<Link href={`/model/${modelId}/process/${cell.value}`}>
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

<style>
	#process-list {
		margin: 1rem;
		max-width: 1000px;
	}
</style>
