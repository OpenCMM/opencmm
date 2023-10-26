<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { DataTable, Button } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import Add from 'carbon-icons-svelte/lib/Add.svelte';
	import Download from 'carbon-icons-svelte/lib/Download.svelte';
	import TrashCan from 'carbon-icons-svelte/lib/TrashCan.svelte';

	import { _ } from 'svelte-i18n';

	let loaded = false;

	interface File {
		id: number;
		name: string;
		size: number;
		modifiedTime: string;
		gcodeReady: boolean;
		createGcode: number;
		downloadGcode: number;
	}

	const headers = [
		{ key: 'id', value: 'ID' },
		{ key: 'name', value: $_('home.file.3dmodel.name') },
		{ key: 'size', value: $_('home.file.3dmodel.size') },
		{ key: 'modifiedTime', value: $_('home.file.3dmodel.lastModified') },
		{ key: 'gcodeReady', value: $_('home.file.3dmodel.gcodeReady') },
		{ key: 'createGcode', empty: true },
		{ key: 'downloadGcode', empty: true },
		{ key: 'delete', empty: true }
	];
	let row: File[] = [];
	const load_table_data = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/list/3dmodels`);
		const data = await res.json();
		for (const d of data['models']) {
			row.push({
				id: d['id'],
				name: d['name'],
				size: d['size'],
				modifiedTime: new Date(d['modified_time']).toLocaleString(),
				gcodeReady: d['gcode_ready'],
				createGcode: d['id'],
				downloadGcode: d['id']
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
		<DataTable size="short" title={$_('home.file.3dmodel.title')} {headers} rows={row}>
			<svelte:fragment slot="cell" let:cell>
				{#if cell.key === 'createGcode'}
					<Button
						kind="primary"
						size="small"
						href={`/setup?id=${cell.value}`}
						iconDescription={$_('home.file.3dmodel.createGcode')}
						icon={Add}
					/>
				{:else if cell.key === 'downloadGcode'}
					<Button
						kind="primary"
						size="small"
						href={`/setup?id=${cell.value}`}
						iconDescription={$_('home.file.3dmodel.downloadGcode')}
						icon={Download}
					/>
				{:else if cell.key === 'delete'}
					<Button
						kind="secondary"
						size="small"
						href={`/setup?id=${cell.value}`}
						iconDescription={$_('home.file.3dmodel.delete')}
						icon={TrashCan}
					/>
				{:else}
					{cell.value}{/if}
			</svelte:fragment>
		</DataTable>
	{/if}
</div>

<style>
	#data-table {
		margin-top: 40px;
	}
</style>
