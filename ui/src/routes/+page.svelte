<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import { Link, Grid, Row, Column } from 'carbon-components-svelte';
	import Files from './Files.svelte';

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
				<Link href="/line">Line</Link>
			</Column>
			<Column>
				<Link href="/arc">Arc</Link>
			</Column>
		</Row>
		<Row>
			<Column>
				<Files />
			</Column>
		</Row>
	</Grid>
</section>
