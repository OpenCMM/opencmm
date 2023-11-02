<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Grid, Row, Column, ProgressBar, Button } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';
	import { page } from '$app/stores';
	import DataTable from 'carbon-icons-svelte/lib/DataTable.svelte';
	import Edge from '../model/Edge.svelte';
	import { goto } from '$app/navigation';

	const modelId = $page.url.searchParams.get('id');
</script>

{#if !modelId}
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
				<Gcode {modelId} />
			</Column>
			<Column>
				<Edge {modelId} />
			</Column>
		</Row>
	</Grid>
{/if}
