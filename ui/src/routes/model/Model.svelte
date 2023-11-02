<script lang="ts">
	import { onMount } from 'svelte';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { page } from '$app/stores';
	import { Button, ContentSwitcher, Loading, Switch } from 'carbon-components-svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import ChartStepper from 'carbon-icons-svelte/lib/ChartStepper.svelte';
	import Arc from './Arc.svelte';
	import Line from './Line.svelte';
	import ModelCheck from './ModelCheck.svelte';
	import { redirectToFilePage } from '$lib/access/path';
	import { goto } from '$app/navigation';

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
		// access control
		redirectToFilePage(data['id'], data['model_status']);
		loaded = true;
	};

	onMount(() => {
		load_model_info();
	});
</script>

{#if !loaded || !modelId}
	<Loading />
{:else}
	<div id="model-page">
		<Grid padding>
			<Row>
				<Column>
					<h1>
						{modelInfo.name}
					</h1>
				</Column>
				<Column>
					<Button icon={ChartStepper} on:click={() => goto(`/gcode?id=${modelId}`)}>GCode</Button>
				</Column>
			</Row>
			<Row>
				<Column>
					<ModelCheck {modelId} />
				</Column>
				<Column>
					<ContentSwitcher bind:selectedIndex>
						<Switch>Arc</Switch>
						<Switch>Line</Switch>
					</ContentSwitcher>

					<div id="data-tale">
						{#if selectedIndex === 0}
							<Arc {modelId} />
						{:else if selectedIndex === 1}
							<Line {modelId} />
						{/if}
					</div>
				</Column>
			</Row>
		</Grid>
	</div>
{/if}

<style>
	#model-page {
		max-width: 2400px;
	}

	#data-tale {
		margin-top: 2rem;
	}
</style>
