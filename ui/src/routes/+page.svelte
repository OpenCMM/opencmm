<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import Setup from './Setup.svelte';
	import DownloadGCode from './DownloadGCode.svelte';
	import CaptureStart from './CaptureStart.svelte';
	import Result from './Result.svelte';
	import 'carbon-components-svelte/css/g80.css';

	let uploaded: boolean = false;
	let settingDone: boolean = false;
	let captureDone: boolean = false;
</script>

<main>
	<h1>OpenCMM</h1>

	{#if !uploaded}
		<Upload3dModel bind:uploaded />
	{/if}

	{#if uploaded && !settingDone}
		<Setup bind:settingDone />
	{/if}

	{#if settingDone && !captureDone}
		<DownloadGCode />
		<CaptureStart bind:captureDone />
	{/if}

	{#if captureDone}
		<Result />
	{/if}
</main>

<style>
	main {
		padding: 1rem;
	}

	h1 {
		font-size: 2rem;
		font-weight: 700;
		margin-bottom: 1rem;
	}
</style>