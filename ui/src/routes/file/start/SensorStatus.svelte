<script lang="ts">
	import { BACKEND_WS_URL } from '$lib/constants/backend';
	import { _ } from 'svelte-i18n';
	import { onDestroy } from 'svelte';
	import { InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';

	export let modelId: string;
	export let sensorStatus: string;
	let ws: WebSocket;

	onDestroy(() => {
		if (ws.readyState === WebSocket.OPEN) {
			ws.close();
		}
	});

	onMount(() => {
		ws = new WebSocket(`${BACKEND_WS_URL}/ws/${modelId}`);
		ws.addEventListener('open', function (_event) {
			console.log('WebSocket is open now.');
		});

		ws.onmessage = function (event) {
			const data = JSON.parse(event.data);
			sensorStatus = data['status'];
		};
	});
</script>

<div>
	<h3>{$_('home.start.status.title')}</h3>
	{#if sensorStatus === 'running' || sensorStatus === 'done'}
		<InlineLoading description={$_('home.start.status.running')} status="finished" />
	{:else if sensorStatus === 'process not found'}
		<InlineLoading description={$_('home.start.status.notRunning')} status="inactive" />
	{:else if sensorStatus === 'sensor not found or turned off'}
		<InlineLoading description={$_('home.start.status.cannotPing')} status="error" />
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
