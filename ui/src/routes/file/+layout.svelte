<script>
	import { Content } from 'carbon-components-svelte';
</script>

<div id="file-page">
	<Content>
		<slot />
	</Content>
</div>

<style>
	#file-page {
		max-width: 64rem;
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		margin: 0 auto;
		box-sizing: border-box;
	}
</style>
