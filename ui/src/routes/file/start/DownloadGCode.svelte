<!-- Download the GCode -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Button } from 'carbon-components-svelte';
	import Download from 'carbon-icons-svelte/lib/Download.svelte';
	import { _ } from 'svelte-i18n';

	export let modelId: string;

	const downloadGCode = async () => {
		try {
			const res = await axios.get(`${BACKEND_URL_LOCAL}/download/gcode/${modelId}`);
			console.log(res);
			const textContent = res.data;
			const blob = new Blob([textContent], { type: 'text/plain' });
			const url = URL.createObjectURL(blob);

			const link = document.createElement('a');
			link.href = url;
			link.download = 'opencmm.gcode';
			link.click();

			URL.revokeObjectURL(url);
		} catch (err) {
			console.error(err);
		}
	};
</script>

<div class="bx--form-item">
	<h3>{$_('home.gcode.download.label')}</h3>
	<p class="download-description">{$_('home.gcode.download.description')}</p>
	<Button icon={Download} on:click={downloadGCode}>{$_('home.gcode.download.helperText')}</Button>
</div>

<style>
	.bx--form-item {
		margin-top: 1rem;
	}

	.download-description {
		margin-top: 1rem;
		margin-bottom: 1rem;
	}
</style>
