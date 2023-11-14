<script lang="ts">
	import 'carbon-components-svelte/css/all.css';
	import ProcessList from './ProcessList.svelte';

	export let data;
	const modelId = data.modelId;
</script>

<ProcessList {modelId} />
