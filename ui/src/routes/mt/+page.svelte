<script lang="ts">
	import {
		Grid,
		Column,
		ProgressBar,
		Row,
		Button,
		Form,
		FormGroup,
		TextInput
	} from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import Chart from './Chart.svelte';
	import { _ } from 'svelte-i18n';

	let shapeLoaded = false;
	let gcodeLoaded = false;
	let sensorLoaded = false;
	let mtctLatency = 1000;
	let mtLoaded = false;
	interface Sensor {
		x: number;
		y: number;
		timestamp: string;
		output: number;
	}

	interface Mtct {
		x: number;
		y: number;
	}

	interface Line {
		id: number;
		x1: number;
		y1: number;
		x2: number;
		y2: number;
	}

	// interface Arc {
	// 	id: number;
	// 	radius: number;
	// 	cx: number;
	// 	cy: number;
	// }

	interface GcodeLine {
		id: number; // line number
		x1: number;
		y1: number;
		x2: number;
		y2: number;
		feedrate: number;
	}

	let lines: Line[] = [];
	let gcodeLines: GcodeLine[] = [];
	// let arcs: Arc[] = [];
	let sensor: Sensor[] = [];
	let mtct: Mtct[] = [];
	const modelId = $page.url.searchParams.get('id');
	const processId = $page.url.searchParams.get('process');
	const load_model_shape_data = async () => {
		const res = await fetch(`${BACKEND_URL}/model/shapes/${modelId}`);
		const data = await res.json();

		for (const d of data['lines']) {
			lines.push({
				id: d[0],
				x1: d[1],
				y1: d[2],
				x2: d[3],
				y2: d[4]
			});
		}
		// for (const d of data['arcs']) {
		// 	arcs.push({
		// 		id: d[0],
		// 		radius: d[1],
		// 		cx: d[2],
		// 		cy: d[3]
		// 	});
		// }
		shapeLoaded = true;
	};

	const load_gcode_line_data = async () => {
		const res = await fetch(`${BACKEND_URL}/gcode/lines/${modelId}`);
		const data = await res.json();

		for (const d of data['lines']) {
			gcodeLines.push({
				id: d[0],
				x1: d[1],
				y1: d[2],
				x2: d[3],
				y2: d[4],
				feedrate: d[5]
			});
		}
		gcodeLoaded = true;
	};

	const updateConfig = async () => {
		// update mtct latency
		sensorLoaded = false;
		loadSensorData();
	};

	const loadSensorData = async () => {
		const res = await fetch(
			`${BACKEND_URL}/sensor/positions/${modelId}/${processId}?mtct_latency=${mtctLatency}`
		);
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
	onMount(() => {
		loadSensorData();
		loadMtctData();
		load_gcode_line_data();
		load_model_shape_data();
	});
</script>

{#if !shapeLoaded || !gcodeLoaded || !sensorLoaded || !mtLoaded || !modelId || !processId}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<Chart {lines} {gcodeLines} {sensor} {mtct} />
			</Column>
			<Column>
				<Form>
					<FormGroup>
						<TextInput
							bind:value={mtctLatency}
							id="latency"
							type="number"
							labelText={$_('settings.mtconnect.latency')}
						/>
					</FormGroup>
					<Button on:click={updateConfig}>{$_('common.save')}</Button>
				</Form>
			</Column>
		</Row>
	</Grid>
{/if}
