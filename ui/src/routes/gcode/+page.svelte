<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Grid, Row, Column, ProgressBar, Button } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';
	import { page } from '$app/stores';
	import DataTable from 'carbon-icons-svelte/lib/DataTable.svelte';
	import Edge from '../model/Edge.svelte';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';

	const modelId = $page.url.searchParams.get('id');
	const processId = $page.url.searchParams.get('processId');
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

{#if !modelId || !processId || !offsetLoaded}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<Button icon={DataTable} on:click={() => goto(`/model?id=${modelId}`)}>
					{$_('home.result.title')}
				</Button>
			</Column>
		</Row>
		<Row>
			<Column>
				<Gcode {modelId} {processId} {offset} />
			</Column>
			<Column>
				<Edge {modelId} />
			</Column>
		</Row>
	</Grid>
{/if}
