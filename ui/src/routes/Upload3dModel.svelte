<!-- upload a 3D model file -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { FileUploader } from 'carbon-components-svelte';

	let error: string | null = null;
	export let uploaded: boolean = false;
	const handleFileChange = async (event: CustomEvent) => {
		console.log(event);
		const fileInput = event.detail;
		if (fileInput === null) return;
		const file = fileInput[0];

		if (!file) return;

		const formData = new FormData();
		formData.append('file', file);

		try {
			const res = await axios.post(`${BACKEND_URL_LOCAL}/upload/3dmodel`, formData, {
				headers: {
					'Content-Type': 'multipart/form-data'
				}
			});
			console.log(res);
			uploaded = true;
		} catch (err) {
			console.error(err);
		}
	};
</script>

{#if error}
	<p class="error">{error}</p>
{/if}

{#if !uploaded}
	<FileUploader
		labelTitle="3Dモデルをアップロードしてください"
		buttonLabel="ファイルを選択"
		labelDescription="STLファイルのみ対応しています"
		accept={['.stl', '.STL']}
		status="complete"
		on:change={handleFileChange}
	/>
{/if}

<style>
	.error {
		color: red;
	}
</style>
