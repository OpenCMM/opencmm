<!-- upload a 3D model file -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { FileUploader } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';

	let error: string | null = null;
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

			if (res.status === 200 && res.data['status'] === 'ok') {
				const modelId = res.data['model_id'];
				window.location.href = `/setup?id=${modelId}`;
			} else {
				error = res.data['message'];
			}
		} catch (err) {
			console.error(err);
		}
	};
</script>

{#if error}
	<p class="error">{error}</p>
{/if}

<div id="file-uploader">
	<FileUploader
		labelTitle={$_('home.upload3dmodel.title')}
		buttonLabel={$_('home.upload3dmodel.buttonLabel')}
		labelDescription={$_('home.upload3dmodel.labelDescription')}
		accept={['.stl', '.STL']}
		status="complete"
		on:change={handleFileChange}
	/>
</div>

<style>
	.error {
		color: red;
	}

	#file-uploader {
		margin: 1rem;
	}
</style>
