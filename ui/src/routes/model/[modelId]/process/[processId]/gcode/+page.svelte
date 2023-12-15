<script lang="ts">
	import { Grid, Column, ProgressBar, Row } from 'carbon-components-svelte';
	import GcodeD3 from '../../../../../components/GcodeD3.svelte';
	import Edge from '../result/Edge.svelte';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
</script>

{#if !modelId || !processId}
	<ProgressBar helperText="Loading..." />
{:else}
	<Grid padding>
		<Row>
			<Column>
				<GcodeD3 {modelId} {processId} />
			</Column>
			<Column>
				<Edge {modelId} {processId} />
			</Column>
		</Row>
	</Grid>
{/if}
