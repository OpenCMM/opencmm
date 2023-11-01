<script lang="ts">
	import { Modal, Grid, Row, Tile, Column, Button } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import DocumentAdd from 'carbon-icons-svelte/lib/DocumentAdd.svelte';
	import Document from 'carbon-icons-svelte/lib/Document.svelte';
	import { InlineLoading } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';
	import Upload3dModel from './Upload3dModel.svelte';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import FileTiles from './FileTiles.svelte';
	import { goto } from '$app/navigation';

	let newFileOpen = false;
	let openFileOpen = false;
	let loaded = false;
	interface RecentFile {
		modelId: number;
		name: string;
		status: number;
	}
	let recentFiles: RecentFile[] = [];
	const load_recent_files = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/list/recent/3dmodels?limit=3`);
		const data = await res.json();
		for (const d of data['models']) {
			recentFiles.push({
				modelId: d['model_id'],
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

<div id="start-menu">
	<Tile class="welcome-tile">
		<h1>{$_('home.welcome.title')}</h1>
		<p>{$_('home.welcome.description')}</p>
		<Grid>
			<Row>
				<Column>
					<Button class="menu-button" icon={DocumentAdd} on:click={() => (newFileOpen = true)}
						>{$_('home.welcome.newFile')}</Button
					>
				</Column>
			</Row>
			<Row>
				<Column>
					<Button
						class="menu-button"
						icon={Document}
						kind="secondary"
						on:click={() => (openFileOpen = true)}>{$_('home.welcome.openFile')}</Button
					>
				</Column>
			</Row>
			<Row>
				<Column>
					<h2>{$_('home.welcome.recentFiles')}</h2>
					{#if !loaded}
						<InlineLoading />
					{:else}
						{#each recentFiles as file}
							<Button
								class="menu-button"
								kind="secondary"
								on:click={() => goto(`/model?id=${file.modelId}`)}>{file.name}</Button
							>
						{/each}
					{/if}
				</Column>
			</Row>
		</Grid>
	</Tile>
</div>
<Modal
	bind:open={newFileOpen}
	modalHeading={$_('home.welcome.newFile')}
	passiveModal
	on:click:button--secondary={() => (newFileOpen = false)}
	on:open
	on:close
>
	<Upload3dModel />
</Modal>

<Modal
	bind:open={openFileOpen}
	hasScrollingContent
	modalHeading={$_('home.welcome.openFile')}
	passiveModal
	on:click:button--secondary={() => (openFileOpen = false)}
	on:open
	on:close
>
	<FileTiles />
</Modal>

<style>
	#start-menu {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	div :global(.welcome-tile) {
		max-width: 1000px;
		padding: 2rem;
	}

	#start-menu h1 {
		font-size: 2.5rem;
		margin-bottom: 1rem;
	}

	#start-menu p {
		font-size: 1.25rem;
		margin-bottom: 2rem;
	}

	#start-menu :global(.menu-button) {
		margin-right: 1rem;
		margin-bottom: 1rem;
	}
	#start-menu .bx--col h2 {
		font-size: 1.25rem;
		margin-right: 1rem;
		margin-top: 1rem;
		margin-bottom: 1rem;
	}
</style>
