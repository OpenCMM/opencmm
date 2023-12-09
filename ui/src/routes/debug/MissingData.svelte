<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { DataTable, InlineLoading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';

	export let modelId: string;
	export let processId: string;
	let loaded = false;

	const headers = [
		{ key: 'id', value: 'Line' },
		{ key: 'start', value: 'start' },
		{ key: 'end', value: 'end' },
		{ key: 'feedrate', value: 'feedrate' }
	];
	interface MissingData {
		id: number; // line number
		start: number[];
		end: number[];
		feedrate: number;
	}
	let missingData: MissingData[];

	const loadMissingMTConnectData = async () => {
		axios
			.get(`${BACKEND_URL}/result/check/mtconnect/points/${modelId}/${processId}`)
			.then((res) => {
				if (res.status === 200) {
					missingData = res.data['lines'];
					loaded = true;
				}
			});
	};

	onMount(() => {
		loadMissingMTConnectData();
	});
</script>

{#if !loaded}
	<InlineLoading />
{:else if missingData.length === 0}
	No missing data
{:else}
	<DataTable size="short" {headers} rows={missingData} />
{/if}
