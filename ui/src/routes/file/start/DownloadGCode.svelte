<!-- Download the GCode -->

<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { Button, ButtonSet } from 'carbon-components-svelte';
	import Download from 'carbon-icons-svelte/lib/Download.svelte';
	import ChartStepper from 'carbon-icons-svelte/lib/ChartStepper.svelte';

	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';

	export let modelId: string;
</script>

<div class="bx--form-item">
	<ButtonSet>
		<Button icon={Download} href={`${BACKEND_URL}/download/gcode/${modelId}`}
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
</style>
