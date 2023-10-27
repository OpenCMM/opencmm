<script lang="ts">
	import { BACKEND_WS_URL_LOCAL } from '$lib/constants/backend';
	import { _ } from 'svelte-i18n';
	import { InlineLoading } from 'carbon-components-svelte';

	export let modelId: string;
	export let sensorStatus: string;

	const ws = new WebSocket(`${BACKEND_WS_URL_LOCAL}/ws/${modelId}`);
	ws.addEventListener('open', function (event) {
		console.log('WebSocket is open now.');
	});

	ws.onmessage = function (event) {
		const data = JSON.parse(event.data);
		sensorStatus = data['status'];
	};
</script>

<div>
	<h3>{$_('home.start.status.title')}</h3>
	{#if sensorStatus === 'running' || sensorStatus === 'done'}
		<InlineLoading description={$_('home.start.status.running')} status="finished" />
	{:else if sensorStatus === 'process not found'}
		<InlineLoading description={$_('home.start.status.notRunning')} status="inactive" />
	{:else}
		<InlineLoading description={$_('home.start.status.running')} status="active" />
	{/if}
</div>

<style>
	h3 {
		margin-top: 1rem;
		margin-bottom: 1rem;
	}
</style>
