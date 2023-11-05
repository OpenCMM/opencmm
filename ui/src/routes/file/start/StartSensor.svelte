<script lang="ts">
	import { _ } from 'svelte-i18n';
	import { page } from '$app/stores';
	import DownloadGCode from './DownloadGCode.svelte';
	import { InlineNotification } from 'carbon-components-svelte';
	import SensorStatus from './SensorStatus.svelte';

	const modelId = $page.url.searchParams.get('id');
	let error: string | null = null;
	let sensorStatus = 'process not found';
</script>

<div class="steps-to-measure">
	<h2>{$_('home.start.howto.title')}</h2>
	<p>{$_('home.start.howto.step1')}</p>
	<p>{$_('home.start.howto.step2')}</p>
	<p>{$_('home.start.howto.step3')}</p>
</div>

{#if modelId}
	<DownloadGCode {modelId} />
{/if}

{#if modelId}
	<SensorStatus {modelId} {sensorStatus} />
{/if}

{#if error}
	<InlineNotification title="Error:" subtitle={$_('home.start.error')} />
{/if}

<style>
	h2 {
		margin-bottom: 1rem;
	}
	.steps-to-measure {
		margin-top: 2rem;
		margin-bottom: 2rem;
	}
</style>
