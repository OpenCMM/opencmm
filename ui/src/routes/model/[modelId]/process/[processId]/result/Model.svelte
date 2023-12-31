<script lang="ts">
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import CaretRight from 'carbon-icons-svelte/lib/CaretRight.svelte';
	import CaretLeft from 'carbon-icons-svelte/lib/CaretLeft.svelte';
	import { OverflowMenu, OverflowMenuItem } from 'carbon-components-svelte';
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
	import Arc from './Arc.svelte';
	import Line from './Line.svelte';
	import Step from './Step.svelte';
	import ModelCheck from './ModelCheck.svelte';
	import { redirectToFilePage } from '$lib/access/path';
	import { _ } from 'svelte-i18n';
	import axios from 'axios';
	import moment from 'moment';
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
				const [, , , offsetX, offsetY] = res.data;
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

	let duration = 0;
	let start = '';
	const loadProcessInfo = async () => {
		axios.get(`${BACKEND_URL}/get_process_info/${processId}`).then((res) => {
			if (res.status === 200) {
				const _duration = res.data['duration'];
				if (_duration !== null) {
					duration = _duration;
				}
				const _start = res.data['start'];
				start = moment(_start).fromNow();
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
		window.location.href = `/model/${modelId}/process/${nextProcess}/result`;
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
		loadProcessInfo();
		loadProcesses();
	});
</script>

{#if !loaded}
	<Loading />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<h2>
					{modelInfo.name}
				</h2>
			</Column>
			<Column>
				<p>{start}</p>
			</Column>
			<Column>
				{#if duration !== 0}
					<p>
						{$_('home.result.measurementTime')}:
						{duration}
						{$_('common.seconds')}
					</p>
				{/if}
			</Column>
			<Column>
				<Button icon={Calculator} on:click={recomputeStart}>
					{$_('home.recompute.button')}</Button
				>
			</Column>
			<Column>
				<OverflowMenu>
					<OverflowMenuItem
						text={$_('home.file.3dmodel.createGcode')}
						href={`/file/setup?id=${modelId}`}
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
