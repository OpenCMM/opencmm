<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';
	import { Content, FileUploader, ToastNotification } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';

	let updateSuccess = false;
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
			const res = await axios.post(`${BACKEND_URL}/send/file`, formData, {
				headers: {
					'Content-Type': 'multipart/form-data'
				}
			});
			console.log(res);

			if (res.status === 200 && res.data['status'] === 'ok') {
				updateSuccess = true;
			} else {
				error = res.data['message'];
			}
		} catch (err) {
			console.error(err);
		}
	};
</script>

<Content>
	<div id="file-uploader">
		<FileUploader
			labelTitle={$_('menu.sendFile')}
			buttonLabel={$_('home.upload3dmodel.buttonLabel')}
			status="complete"
			on:change={handleFileChange}
		/>
	</div>

	{#if updateSuccess}
		<ToastNotification
			kind="success"
			title={$_('common.sendSuccess')}
			timeout={3000}
			on:close={() => (updateSuccess = false)}
		/>
	{/if}

	{#if error}
		<ToastNotification
			kind="error"
			title={$_('common.sendFailed')}
			subtitle={error}
			timeout={3000}
			on:close={() => (error = null)}
		/>
	{/if}
</Content>

<style>
	#file-uploader {
		margin: 1rem;
	}
</style>
