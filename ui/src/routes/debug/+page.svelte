<script lang="ts">
	import Debug from './Debug.svelte';
	import { Grid, Row, Column, ProgressBar } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';
	import MissingData from './MissingData.svelte';
	import MtctLines from './MtctLines.svelte';
	import DelayBetweenLines from './DelayBetweenLines.svelte';
	import MissingLineDiff from './MissingLineDiff.svelte';

	const modelId = $page.url.searchParams.get('id');
	const processId = $page.url.searchParams.get('process');
	let offset = [0.0, 0.0, 0.0];
	let loaded = false;

	onMount(() => {
		axios.get(`${BACKEND_URL}/get/model/table/data/${modelId}`).then((res) => {
			if (res.status === 200) {
				const [, , , offsetX, offsetY] = res.data;
				offset = [offsetX, offsetY, 0.0];
				loaded = true;
			}
		});
	});
</script>

{#if modelId && processId && loaded}
	<Grid padding>
		<Row>
			<Column>
				<Debug {modelId} {processId} {offset} />
			</Column>
			<Column>
				<MissingData {modelId} {processId} />
				<MtctLines {modelId} {processId} />
				<DelayBetweenLines {modelId} {processId} />
				<MissingLineDiff {modelId} {processId} />
			</Column>
		</Row>
	</Grid>
{:else}
	<ProgressBar helperText="Loading..." />
{/if}
