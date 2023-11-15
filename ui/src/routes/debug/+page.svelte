<script lang="ts">
	import Debug from './Debug.svelte';
	import { Grid, Row, Column, ProgressBar } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';

	const modelId = $page.url.searchParams.get('id');
	const processId = $page.url.searchParams.get('process');
	let offset = [0.0, 0.0, 0.0];
	let offsetLoaded = false;
	onMount(() => {
		axios.get(`${BACKEND_URL}/get/model/table/data/${modelId}`).then((res) => {
			if (res.status === 200) {
				const [, , , offsetX, offsetY] = res.data;
				offset = [offsetX, offsetY, 0.0];
				offsetLoaded = true;
			}
		});
	});
</script>

{#if modelId && processId && offsetLoaded}
	<Grid padding>
		<Row>
			<Column>
				<Debug {modelId} {processId} {offset} />
			</Column>
		</Row>
	</Grid>
{:else}
	<ProgressBar helperText="Loading..." />
{/if}
