<script lang="ts">
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import CaretRight from 'carbon-icons-svelte/lib/CaretRight.svelte';
	import CaretLeft from 'carbon-icons-svelte/lib/CaretLeft.svelte';
	import { OverflowMenu, OverflowMenuItem } from 'carbon-components-svelte';
	import Add from 'carbon-icons-svelte/lib/Add.svelte';
	import {
		Button,
		ButtonSet,
		ContentSwitcher,
		Loading,
		Switch,
		ToastNotification
	} from 'carbon-components-svelte';
	import Calculator from 'carbon-icons-svelte/lib/Calculator.svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import ChartStepper from 'carbon-icons-svelte/lib/ChartStepper.svelte';
	import Arc from './Arc.svelte';
	import Line from './Line.svelte';
	import Step from './Step.svelte';
	import ModelCheck from './ModelCheck.svelte';
	import { redirectToFilePage } from '$lib/access/path';
	import { _ } from 'svelte-i18n';
	import axios from 'axios';
	import Slope from './Slope.svelte';

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

	const deleteModel = async () => {
		axios.delete(`${BACKEND_URL}/delete/model/?model_id=${modelId}`).then((res) => {
			if (res.status === 200) {
				window.location.href = '/';
			}
		});
	};

	let nextProcess: string;
	let previousProcess: string;
	const loadProcesses = async () => {
		axios.get(`${BACKEND_URL}/get/prev/next/processes/${modelId}/${processId}`).then((res) => {
			if (res.status === 200) {
				previousProcess = res.data['prev'];
				nextProcess = res.data['next'];
			}
		});
	};
	const goToDifferentPage = (nextProcess: string) => {
		processId = nextProcess;
		window.location.href = `/model/${modelId}/process/${nextProcess}`;
	};

	let recomputeSuccess = false;
	const recomputeStart = async () => {
		try {
			axios.post(`${BACKEND_URL}/recompute/process/${processId}`).then((res) => {
				if (res.status === 200) {
					recomputeSuccess = true;
				}
			});
		} catch (e) {
			console.log(e);
		}
	};

	onMount(() => {
		loadModelInfo();
		loadModelTableData();
		loadProcesses();
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
					<Button icon={ChartStepper} href={`/gcode?id=${modelId}&process=${processId}`}>
						{$_('common.gcode')}</Button
					>
				</Column>
				<Column>
					<Button href={`/d3?id=${modelId}&process=${processId}`}>2D</Button>
				</Column>
				<Column>
					<Button icon={Add} href={`/file/setup?id=${modelId}`}>
						{$_('home.file.3dmodel.createGcode')}</Button
					>
				</Column>
				<Column>
					<Button icon={Calculator} on:click={recomputeStart}>
						{$_('home.recompute.button')}</Button
					>
				</Column>
				<Column>
					<OverflowMenu>
						<OverflowMenuItem href={`/debug?id=${modelId}&process=${processId}`} text="MTConnect" />
						<OverflowMenuItem href={`/mt?id=${modelId}&process=${processId}`} text="MTConnect 2D" />
						<OverflowMenuItem
							href={`/model/processes?id=${modelId}`}
							text={$_('home.process.title')}
						/>
						<OverflowMenuItem danger text={$_('common.deleteModel')} on:click={deleteModel} />
					</OverflowMenu>
				</Column>
				<Column>
					<div id="page-button">
						<ButtonSet>
							<Button
								iconDescription={$_('page.backwardText')}
								icon={CaretLeft}
								disabled={previousProcess === null}
								on:click={() => goToDifferentPage(previousProcess)}
							/>
							<Button
								iconDescription={$_('page.forwardText')}
								icon={CaretRight}
								disabled={nextProcess === null}
								on:click={() => goToDifferentPage(nextProcess)}
							/>
						</ButtonSet>
					</div>
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
						<Switch>{$_('common.step')}</Switch>
						<Switch>{$_('common.slope')}</Switch>
					</ContentSwitcher>

					<div id="data-tale">
						{#if selectedIndex === 0}
							<Arc {modelId} {processId} />
						{:else if selectedIndex === 1}
							<Line {modelId} {processId} />
						{:else if selectedIndex === 2}
							<Step {modelId} {processId} />
						{:else if selectedIndex === 3}
							<Slope {modelId} {processId} />
						{/if}
					</div>
				</Column>
			</Row>
		</Grid>
	</div>
{/if}

{#if recomputeSuccess}
	<ToastNotification
		kind="success"
		title={$_('home.recompute.start')}
		timeout={3000}
		on:close={() => (recomputeSuccess = false)}
	/>
{/if}

<style>
	#model-page {
		max-width: 2400px;
	}

	#data-tale {
		margin-top: 2rem;
	}

	#page-button {
		position: absolute;
		top: 4rem;
		right: 4rem;
		width: 3rem;
	}
</style>
