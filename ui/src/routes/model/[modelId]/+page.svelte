<script lang="ts">
	import 'carbon-components-svelte/css/all.css';
	import { BACKEND_URL } from '$lib/constants/backend';
	import { redirectToFilePage } from '$lib/access/path';
	import { onMount } from 'svelte';
	import { Loading } from 'carbon-components-svelte';
	import axios from 'axios';
	import { goto } from '$app/navigation';

	export let data;
	const modelId = data.modelId;

	const redirectToModelPage = async () => {
		axios.get(`${BACKEND_URL}/list/processes/${modelId}`).then((res) => {
			if (res.status === 200) {
				console.log(res.data);
				const processes = res.data['processes'];
				const latestProcess = processes[processes.length - 1];
				goto(`/model/${modelId}/process/${latestProcess[0]}/result`);
			}
		});
	};

	const loadModelInfo = async () => {
		const res = await fetch(`${BACKEND_URL}/get/3dmodel/info/${modelId}`);
		const data = await res.json();
		// access control
		redirectToFilePage(data['id'], data['model_status']);
		redirectToModelPage();
	};

	onMount(() => {
		loadModelInfo();
	});
</script>

<Loading />
