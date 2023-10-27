<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { onMount } from 'svelte';
	import { ClickableTile } from 'carbon-components-svelte';
	import { goToFilePage } from './utils/path';

	let loaded = false;

	interface File {
		id: number;
		name: string;
		status: number;
	}

	let files: File[] = [];
	const load_recent_files = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/list/3dmodels`);
		const data = await res.json();
		for (const d of data['models']) {
			files.push({
				id: d['id'],
				name: d['name'],
				status: d['model_status']
			});
		}
		loaded = true;
	};

	onMount(() => {
		document.body.classList.add('start-menu-open');
		load_recent_files();
	});
</script>

<div id="data-table">
	{#if !loaded}
		<p>Loading...</p>
	{:else}
		{#each files as file}
			<ClickableTile on:click={() => goToFilePage(file.id, file.status)}>
				{file.name}
			</ClickableTile>
		{/each}
	{/if}
</div>

<style>
	#data-table {
		margin-top: 40px;
	}
</style>
