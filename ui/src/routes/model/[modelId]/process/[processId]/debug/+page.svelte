<script lang="ts">
	import Debug from './Debug.svelte';
	import { Grid, Row, Column, ProgressBar, Content } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';
	import MissingData from '../../../../../components/MissingData.svelte';
	import MtctLines from '../../../../../components/MtctLines.svelte';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
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

<Content>
	{#if modelId && processId && loaded}
		<Grid padding>
			<Row>
				<Column>
					<Debug {modelId} {processId} {offset} />
				</Column>
				<Column>
					<MissingData {modelId} {processId} />
					<MtctLines {modelId} {processId} />
				</Column>
			</Row>
		</Grid>
	{:else}
		<ProgressBar helperText="Loading..." />
	{/if}
</Content>
