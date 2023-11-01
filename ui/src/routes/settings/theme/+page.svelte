<script lang="ts">
	import { Theme } from 'carbon-components-svelte';
	import type { CarbonTheme } from 'carbon-components-svelte/types/Theme/Theme.svelte';
	let theme: CarbonTheme | undefined = 'g90';
</script>

<Theme render="select" bind:theme persist persistKey="__carbon-theme" />
