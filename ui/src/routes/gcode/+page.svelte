<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import Edge from '../model/Edge.svelte';

	const modelId = $page.url.searchParams.get('id');
</script>

{#if !modelId}
	<p>Loading...</p>
{:else}
	<Grid>
		<Row>
			<Column>
				<Gcode {modelId} />
			</Column>
			<Column>
				<Edge {modelId} />
			</Column>
		</Row>
	</Grid>
{/if}
