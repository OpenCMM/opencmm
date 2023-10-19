<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import Point from './Result/Edge.svelte';
	import Line from './Result/Line.svelte';
	import Arc from './Result/Arc.svelte';
	import { Link, Grid, Row, Column } from 'carbon-components-svelte';

	let uploaded = false;
</script>

<svelte:head>
	<title>OpenCMM</title>
	<meta name="description" content="OpenCMM" />
</svelte:head>

<section>
	{#if !uploaded}
		<Upload3dModel />
	{/if}
	<Grid>
		<Row>
			<Column>
				<Link href="/gcode">Gcode</Link>
			</Column>
			<Column>Column</Column>
			<Column>Column</Column>
			<Column>Column</Column>
		</Row>
	</Grid>
	<Point />
	<Line />
	<Arc />
</section>
