<script lang="ts">
	import { onMount } from 'svelte';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { page } from '$app/stores';
	import { ContentSwitcher, Switch } from 'carbon-components-svelte';
	import Arc from './Arc.svelte';
	import Line from './Line.svelte';
	import Edge from './Edge.svelte';
	import ModelCheck from './ModelCheck.svelte';

	const modelId = $page.url.searchParams.get('id');

	let loaded = false;

	let selectedIndex = 0;
	interface ModelInfo {
		id: number;
		name: string;
		gcodeReady: boolean;
		status: number;
	}
	let modelInfo = {} as ModelInfo;
	const load_model_info = async () => {
		const res = await fetch(`${BACKEND_URL_LOCAL}/get/3dmodel/info/${modelId}`);
		const data = await res.json();
		modelInfo = {
			id: data['id'],
			name: data['name'],
			gcodeReady: data['gcode_ready'],
			status: data['model_status']
		};
		loaded = true;
	};

	onMount(() => {
		load_model_info();
	});
</script>

{#if !loaded || !modelId}
	<p>Loading...</p>
{:else}
	<h1>
		{modelInfo.name}
	</h1>
	<ModelCheck {modelId} />
	<ContentSwitcher bind:selectedIndex>
		<Switch>Arc</Switch>
		<Switch>Line</Switch>
		<Switch>Edge</Switch>
	</ContentSwitcher>

	{#if selectedIndex === 0}
		<Arc {modelId} />
	{:else if selectedIndex === 1}
		<Line {modelId} />
	{:else if selectedIndex === 2}
		<Edge {modelId} />
	{/if}
{/if}
