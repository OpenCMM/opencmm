<script lang="ts">
	import 'carbon-components-svelte/css/all.css';
	import { _ } from 'svelte-i18n';
	import Model from './Model.svelte';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
</script>

<Model {modelId} {processId} />
