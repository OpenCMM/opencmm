<script lang="ts">
	import {
		Grid,
		Column,
		ProgressBar,
		Row,
		Button,
		Form,
		FormGroup,
		NumberInput,
		ToastNotification
	} from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import Chart from './Chart.svelte';
	import { _ } from 'svelte-i18n';
	import axios from 'axios';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
	let sensorLoaded = false;
	let mtctLatency = 0;
	let mtLoaded = false;
	let updateSuccess = false;
	interface Sensor {
		x: number;
		y: number;
		timestamp: string;
		output: number | undefined;
	}

	interface Mtct {
		x: number;
		y: number;
	}
	let sensor: Sensor[] = [];
	let mtct: Mtct[] = [];
	const applyConfig = async () => {
		// apply mtct latency
		sensorLoaded = false;
		loadSensorData();
	};

	const updateConfig = async () => {
		// update mtct latency
		axios
			.post(`${BACKEND_URL}/update/mtconnect/latency/${processId}?mtct_latency=${mtctLatency}`)
			.then((res) => {
				if (res.status === 200 && res.data['status'] === 'ok') {
					updateSuccess = true;
				}
			});
	};

	const loadSensorData = async () => {
		let url = `${BACKEND_URL}/sensor/positions/${modelId}/${processId}`;
		if (mtLoaded) {
			url += `?mtct_latency=${mtctLatency}`;
		}
		const res = await fetch(url);
		const data = await res.json();
		sensor = [];
		for (const d of data['sensor']) {
			sensor.push({
				x: d[1],
				y: d[2],
				timestamp: d[3],
				output: d[4]
			});
		}
		if (mtctLatency != data['latency']) {
			mtctLatency = data['latency'];
		}
		sensorLoaded = true;
	};
	const loadMtctData = async () => {
		const res = await fetch(`${BACKEND_URL}/result/debug/mtconnect/points/${processId}`);
		const data = await res.json();
		for (const d of data['points']) {
			mtct.push({
				x: d[1],
				y: d[2]
			});
		}
		mtLoaded = true;
	};
	onMount(async () => {
		loadSensorData();
		loadMtctData();
	});
</script>

{#if !sensorLoaded || !mtLoaded || !modelId || !processId}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<Chart {modelId} {sensor} {mtct} />
			</Column>
			<Column>
				<Form>
					<FormGroup>
						<NumberInput
							bind:value={mtctLatency}
							id="latency"
							label={$_('settings.mtconnect.latency')}
							min={0}
							step={0.01}
						/>
					</FormGroup>
					<Button kind="secondary" on:click={applyConfig}>{$_('common.apply')}</Button>
					<Button on:click={updateConfig}>{$_('common.save')}</Button>
				</Form>
			</Column>
		</Row>
	</Grid>
{/if}

{#if updateSuccess}
	<ToastNotification
		kind="success"
		title={$_('common.saveSuccess')}
		timeout={3000}
		on:close={() => (updateSuccess = false)}
	/>
{/if}
