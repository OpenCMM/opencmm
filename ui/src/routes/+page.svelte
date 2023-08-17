<script lang="ts">
	import Upload3dModel from './Upload3dModel.svelte';
	import Point from './Result/Point.svelte';
	import Line from './Result/Line.svelte';
	import Arc from './Result/Arc.svelte';

	let uploaded: boolean = false;
</script>

<svelte:head>
	<title>OpenCMM</title>
	<meta name="description" content="OpenCMM" />
</svelte:head>

<section>
	{#if !uploaded}
		<Upload3dModel />
	{/if}

	<Point />
	<Line />
	<Arc />
</section>