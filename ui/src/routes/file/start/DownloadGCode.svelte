<!-- Download the GCode -->

<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import { Button } from 'carbon-components-svelte';
	import Download from 'carbon-icons-svelte/lib/Download.svelte';

	import { _ } from 'svelte-i18n';

	export let modelId: string;
</script>

<div class="bx--form-item">
	<Button icon={Download} href={`${BACKEND_URL}/download/gcode/${modelId}`}
		>{$_('home.gcode.download.helperText')}</Button
	>
</div>

<style>
	.bx--form-item {
		margin-top: 1rem;
	}
</style>
