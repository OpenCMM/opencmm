<script lang="ts">
	import Setup from './Setup.svelte';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { Loading } from 'carbon-components-svelte';

	import { ProgressIndicator, ProgressStep } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import 'carbon-components-svelte/css/all.css';
	import { page } from '$app/stores';
	import { _ } from 'svelte-i18n';

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
	<Loading />
{:else}
	<h1>
		{modelInfo.name}
	</h1>

	<div id="progress-indicator">
		<ProgressIndicator spaceEqually preventChangeOnClick currentIndex={1}>
			<ProgressStep complete label={$_('home.file.progress.step1')} />
			<ProgressStep complete={modelInfo.status > 0} label={$_('home.file.progress.step2')} />
			<ProgressStep complete={modelInfo.status > 1} label={$_('home.file.progress.step3')} />
		</ProgressIndicator>
	</div>
	<Setup />
{/if}

<style>
	#progress-indicator {
		margin-top: 2rem;
	}
</style>
