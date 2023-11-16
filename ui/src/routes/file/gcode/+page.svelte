<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Grid, Row, Column, ProgressBar } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';

	const modelId = $page.url.searchParams.get('id');
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

{#if !modelId || !offsetLoaded}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<Gcode {modelId} {offset} />
			</Column>
		</Row>
	</Grid>
{/if}
