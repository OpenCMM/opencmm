<!-- upload a 3D model file -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL
	 } from '$lib/constants/backend';


	let error: string | null = null;
	export let uploaded: boolean = false;
	const handleFileChange = async (event: Event) => {
    const fileInput = event.target;
	if (fileInput === null) return;
    const file = fileInput.files[0];

		if (!file) return;

		const formData = new FormData();
		formData.append('file', file);

		try {
			const res = await axios.post(`${BACKEND_URL_LOCAL}/upload/3dmodel`, formData, {
				headers: {
					'Content-Type': 'multipart/form-data',
				},
			});
			console.log(res);
			uploaded = true;
		} catch (err) {
			console.error(err);
		}
	};
</script>

{#if !uploaded}
	<p>3Dモデルをstlファイルでアップロードしてください</p>
{/if}

{#if error}
	<p class="error">{error}</p>
{/if}


<input type="file" name="file" on:change={handleFileChange} />

<style>
	.error {
		color: red;
	}
</style>