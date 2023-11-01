<!-- Download the GCode -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { Button, ButtonSet } from 'carbon-components-svelte';
	import Download from 'carbon-icons-svelte/lib/Download.svelte';
	import ChartStepper from 'carbon-icons-svelte/lib/ChartStepper.svelte';

	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';

	export let modelId: string;
</script>

<div class="bx--form-item">
	<h3>{$_('home.gcode.download.label')}</h3>
	<p class="download-description">{$_('home.gcode.download.description')}</p>
	<ButtonSet>
		<Button icon={Download} href={`${BACKEND_URL_LOCAL}/download/gcode/${modelId}`}
			>{$_('home.gcode.download.helperText')}</Button
		>
		<Button icon={ChartStepper} on:click={() => goto(`/gcode?id=${modelId}`)} kind="secondary"
			>{$_('home.gcode.download.check')}</Button
		>
	</ButtonSet>
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
