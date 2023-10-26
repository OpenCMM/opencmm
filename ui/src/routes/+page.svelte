<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import Files from './Files.svelte';
</script>

<svelte:head>
	<title>OpenCMM</title>
	<meta name="description" content="OpenCMM" />
</svelte:head>

<section>
	<Upload3dModel />
	<Grid>
		<Row>
			<Column>
				<Files />
			</Column>
		</Row>
	</Grid>
</section>
