<script lang="ts">
	import { onMount } from 'svelte';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { page } from '$app/stores';
	import { _ } from 'svelte-i18n';
	import { ClickableTile } from 'carbon-components-svelte';
	import { ProgressIndicator, ProgressStep } from 'carbon-components-svelte';

	const modelId = $page.url.searchParams.get('id');

	let loaded = false;

	interface ModelInfo {
		id: number;
		name: string;
		gcodeReady: boolean;
		status: number;
	}
	let modelInfo = {} as ModelInfo;
	const load_model_info = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/get/3dmodel/info/${modelId}`);
		const data = await res.json();
		modelInfo = {
			id: data['id'],
			name: data['name'],
			gcodeReady: data['gcode_ready'],
			status: data['model_status']
		};
		loaded = true;
	};

	onMount(() => {
		load_model_info();
	});
</script>

{#if !loaded}
	<p>Loading...</p>
{:else}
	<h1>
		{modelInfo.name}
	</h1>

	<div id="progress-indicator">
		<ProgressIndicator spaceEqually preventChangeOnClick currentIndex={8}>
			<ProgressStep complete label={$_('home.file.progress.step1')} />
			<ProgressStep complete={modelInfo.gcodeReady} label={$_('home.file.progress.step2')} />
			<ProgressStep label={$_('home.file.progress.step3')} />
		</ProgressIndicator>
	</div>
	<ClickableTile href={`/file/setup?id=${modelInfo.id}`}>
		{$_('home.file.3dmodel.createGcode')}
	</ClickableTile>

	{#if modelInfo.gcodeReady}
		<ClickableTile href={`/gcode?id=${modelInfo.id}`}>
			{$_('home.file.3dmodel.downloadGcode')}
		</ClickableTile>
	{/if}
{/if}

<style>
	#progress-indicator {
		margin-top: 2rem;
		margin-bottom: 2rem;
	}
</style>
