<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import Line from './Result/Line.svelte';
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
			<Column>
				<Link href="/edge">Edge</Link>
			</Column>
			<Column>
				<Link href="/arc">Arc</Link>
			</Column>
			<Column>Column</Column>
		</Row>
	</Grid>
	<Line />
</section>
