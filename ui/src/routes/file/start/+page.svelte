<script lang="ts">
	import StartSensor from './StartSensor.svelte';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { ProgressIndicator, ProgressStep } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import 'carbon-components-svelte/css/all.css';
	import { page } from '$app/stores';
	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';

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
		<ProgressIndicator spaceEqually currentIndex={2}>
			<ProgressStep complete label={$_('home.file.progress.step1')} on:click={() => goto('/')} />
			<ProgressStep
				complete={modelInfo.status > 0}
				label={$_('home.file.progress.step2')}
				on:click={() => goto(`/file/setup?id=${modelId}`)}
			/>
			<ProgressStep complete={modelInfo.status > 1} label={$_('home.file.progress.step3')} />
		</ProgressIndicator>
	</div>
	<StartSensor />
{/if}

<style>
	#progress-indicator {
		margin-top: 2rem;
	}
</style>
