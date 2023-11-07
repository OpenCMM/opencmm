<script lang="ts">
	import { _ } from 'svelte-i18n';
	import DownloadGCode from './DownloadGCode.svelte';
	import { InlineNotification, Loading } from 'carbon-components-svelte';
	import axios from 'axios';
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';

	export let modelId: string | null = null;
	let error: string | null = null;
	let gcodeFilename = '';
	let programNumber = '';
	let loaded = false;

	onMount(() => {
		// Load the settings here
		axios.get(`${BACKEND_URL}/get/gcode/info/${modelId}`).then((response) => {
			console.log({ response });
			gcodeFilename = response.data['filename'];
			programNumber = response.data['program_number'];
			loaded = true;
		});
	});
</script>

{#if !loaded}
	<Loading />
{:else}
	<div id="instruction">
		<h2>
			{$_('home.start.howto.instruction')}
		</h2>
		<h2>{gcodeFilename}</h2>
		<p>{$_('home.start.howto.programNumber')}: {programNumber}</p>
	</div>
{/if}

{#if modelId}
	<DownloadGCode {modelId} />
{/if}

{#if error}
	<InlineNotification title="Error:" subtitle={$_('home.start.error')} />
{/if}

<style>
	h2 {
		margin-bottom: 1rem;
	}
	#instruction {
		margin-top: 2rem;
		margin-bottom: 2rem;
	}
</style>
