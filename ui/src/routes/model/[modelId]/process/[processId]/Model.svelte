<script lang="ts">
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import { Button, ContentSwitcher, Loading, Switch } from 'carbon-components-svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import ChartStepper from 'carbon-icons-svelte/lib/ChartStepper.svelte';
	import Table from 'carbon-icons-svelte/lib/Table.svelte';
	import Arc from './Arc.svelte';
	import Line from './Line.svelte';
	import ModelCheck from './ModelCheck.svelte';
	import { redirectToFilePage } from '$lib/access/path';
	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';
	import axios from 'axios';

	export let modelId: string;
	export let processId: string;

	let loaded = false;

	let selectedIndex = 0;
	interface ModelInfo {
		id: number;
		name: string;
		gcodeReady: boolean;
		status: number;
	}

	let offset = [0.0, 0.0, 0.0];
	let offsetLoaded = false;

	let modelInfo = {} as ModelInfo;
	const loadModelInfo = async () => {
		const res = await fetch(`${BACKEND_URL}/get/3dmodel/info/${modelId}`);
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

	const loadModelTableData = async () => {
		axios.get(`${BACKEND_URL}/get/model/table/data/${modelId}`).then((res) => {
			if (res.status === 200) {
				const [, _filename, , offsetX, offsetY] = res.data;
				offset = [offsetX, offsetY, 0.0];
				offsetLoaded = true;
			}
		});
	};

	onMount(() => {
		loadModelInfo();
		loadModelTableData();
	});
</script>

{#if !loaded}
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
					<Button
						icon={ChartStepper}
						on:click={() => goto(`/gcode?id=${modelId}&process=${processId}`)}
					>
						{$_('common.gcode')}</Button
					>
				</Column>
				<Column>
					<Button icon={Table} on:click={() => goto(`/model/${modelId}`)}>
						{$_('home.process.title')}</Button
					>
				</Column>
			</Row>
			<Row>
				<Column>
					{#if !offsetLoaded}
						<Loading />
					{:else}
						<ModelCheck {modelId} {processId} {offset} />
					{/if}
				</Column>
				<Column>
					<ContentSwitcher bind:selectedIndex>
						<Switch>{$_('common.arc')}</Switch>
						<Switch>{$_('common.line')}</Switch>
					</ContentSwitcher>

					<div id="data-tale">
						{#if selectedIndex === 0}
							<Arc {modelId} {processId} />
						{:else if selectedIndex === 1}
							<Line {modelId} {processId} />
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
