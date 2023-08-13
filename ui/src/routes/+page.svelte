<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import Setup from './Setup.svelte';
	import DownloadGCode from './DownloadGCode.svelte';
	import CaptureStart from './CaptureStart.svelte';
	import Result from './Result.svelte';

	let uploaded: boolean = false;
	let settingDone: boolean = false;
	let captureDone: boolean = false;
</script>

<h1>OpenCMM</h1>

<Upload3dModel bind:uploaded={uploaded} />

{#if uploaded && !settingDone}
	<Setup bind:settingDone={settingDone} />
{/if}

{#if settingDone}
	<DownloadGCode />
	<CaptureStart bind:captureDone={captureDone} />
{/if}

{#if captureDone}
	<Result />
{/if}