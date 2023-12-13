<script lang="ts">
	import { Grid, Column, ProgressBar, Row } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { BACKEND_URL } from '$lib/constants/backend';
	import Chart from './Chart.svelte';
	import Edge from '../result/Edge.svelte';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
	let shapeLoaded = false;
	let gcodeLoaded = false;
	let edgeLoaded = false;
	interface Edge {
		id: number;
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
	let edges: Edge[] = [];
	let measuredEdges: Edge[] = [];
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

	const load_edge_data = async () => {
		const res = await fetch(`${BACKEND_URL}/result/edges/result/combined/${modelId}/${processId}`);
		const data = await res.json();
		for (const d of data['edges']) {
			edges.push({
				id: d[0],
				x: d[1],
				y: d[2]
			});
			if (d[4] !== null) {
				measuredEdges.push({
					id: d[0],
					x: d[4],
					y: d[5]
				});
			}
		}
		edgeLoaded = true;
	};
	onMount(() => {
		load_edge_data();
		load_gcode_line_data();
		load_model_shape_data();
	});
</script>

{#if !shapeLoaded || !gcodeLoaded || !edgeLoaded || !modelId || !processId}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<Chart {lines} {gcodeLines} {edges} {measuredEdges} />
			</Column>
			<Column>
				<Edge {modelId} {processId} />
			</Column>
		</Row>
	</Grid>
{/if}
