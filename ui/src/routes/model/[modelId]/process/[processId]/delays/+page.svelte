<script lang="ts">
	import { Grid, Row, Column, ProgressBar, Content } from 'carbon-components-svelte';
	import DelayBetweenLines from '../../../../../components/DelayBetweenLines.svelte';
	import MissingLineDiff from '../../../../../components/MissingLineDiff.svelte';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
</script>

<Content>
	{#if modelId && processId}
		<Grid padding>
			<Row>
				<Column>
					<DelayBetweenLines {modelId} {processId} />
				</Column>
				<Column>
					<MissingLineDiff {modelId} {processId} />
				</Column>
			</Row>
		</Grid>
	{:else}
		<ProgressBar helperText="Loading..." />
	{/if}
</Content>
