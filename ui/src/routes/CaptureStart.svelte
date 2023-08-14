<!-- Start capturing images -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, InlineLoading } from 'carbon-components-svelte';

	export let captureDone: boolean = false;
	let error: string | null = null;
	let focalLength: number = 25;

	let sensorWidth: number = 6.287;

	let distance: number = 0;
	let processing: boolean = false;

	const startCapturing = async (e: Event) => {
		e.preventDefault();

		const data = {
			focal_length: Number(focalLength),
			sensor_width: Number(sensorWidth),
			distance: Number(distance),
			is_full: false
		};
		try {
			processing = true;
			const res = await axios.post(`${BACKEND_URL_LOCAL}/process/start`, data, {
				headers: {
					'Content-Type': 'application/json'
				}
			});
			console.log(res);
			captureDone = true;
		} catch (err) {
			console.error(err);
			error = '測定に失敗しました';
			processing = false;
		}
	};
</script>

<div class="bx--form-item">
	<p id="form-title">測定を開始します</p>

	<Form on:submit={startCapturing}>
		<FormGroup>
			<TextInput labelText="focal length" id="focalLength" bind:value={focalLength} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="sensor width" id="sensorWidth" bind:value={sensorWidth} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="カメラとの距離" id="distance" bind:value={distance} />
		</FormGroup>
		{#if processing && !error}
			<InlineLoading status="active" description="測定中" />
		{:else if error}
			<InlineLoading status="error" description={error} />
		{:else}
			<Button type="submit">測定開始</Button>
		{/if}
	</Form>
</div>

<style>
	.bx--form-item {
		margin: 1rem;
	}

	#form-title {
		font-size: 1.2rem;
		font-weight: bold;
		margin: 1rem;
	}

</style>
