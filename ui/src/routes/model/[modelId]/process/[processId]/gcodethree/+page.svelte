<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Grid, Row, Column, ProgressBar } from 'carbon-components-svelte';
	import Edge from '../result/Edge.svelte';
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
	let offset = [0.0, 0.0, 0.0];
	let offsetLoaded = false;
	let filename = '';
	onMount(() => {
		axios.get(`${BACKEND_URL}/get/model/table/data/${modelId}`).then((res) => {
			if (res.status === 200) {
				const [, _filename, , offsetX, offsetY] = res.data;
				offset = [offsetX, offsetY, 0.0];
				filename = _filename;
				offsetLoaded = true;
			}
		});
	});
</script>

{#if !modelId || !processId || !offsetLoaded}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<h1>
					{filename}
				</h1>
			</Column>
		</Row>
		<Row>
			<Column>
				<Gcode {modelId} {processId} {offset} />
			</Column>
			<Column>
				<Edge {modelId} {processId} />
			</Column>
		</Row>
	</Grid>
{/if}
