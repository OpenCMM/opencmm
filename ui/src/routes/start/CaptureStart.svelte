<!-- Start capturing images -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, InlineLoading } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';

	let error: string | null = null;
	let focalLength = 25;

	let sensorWidth = 6.287;

	let distance = 50.0;
	let processing = false;

	const startCapturing = async (e: Event) => {
		e.preventDefault();

		const data = {
			focal_length: Number(focalLength),
			sensor_width: Number(sensorWidth),
			distance: Number(distance),
			is_full: false,
			save_as_file: true
		};
		try {
			processing = true;
			const res = await axios.post(`${BACKEND_URL_LOCAL}/process/start`, data, {
				headers: {
					'Content-Type': 'application/json'
				}
			});
			console.log(res);
		} catch (err) {
			console.error(err);
			error = $_('home.start.error');
			processing = false;
		}
	};
</script>

<div class="bx--form-item">
	<p id="form-title">{$_('home.start.title')}</p>

	<Form on:submit={startCapturing}>
		<FormGroup>
			<TextInput labelText="focal length" id="focalLength" bind:value={focalLength} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="sensor width" id="sensorWidth" bind:value={sensorWidth} />
		</FormGroup>
		<FormGroup>
			<TextInput
				labelText={$_('home.start.distance.label')}
				id="distance"
				bind:value={distance}
				helperText={$_('home.start.distance.helperText')}
			/>
		</FormGroup>
		{#if processing && !error}
			<InlineLoading status="active" description={$_('home.start.status.active')} />
		{:else if error}
			<InlineLoading status="error" description={error} />
		{:else}
			<Button type="submit">{$_('home.start.start')}</Button>
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
