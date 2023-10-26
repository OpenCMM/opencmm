<!-- Start capturing images -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, InlineLoading } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';

	let error: string | null = null;
	let mtInterval = 500;
	let interval = 1000;
	let threshold = 100;
	let processing = false;

	const startCapturing = async (e: Event) => {
		e.preventDefault();

		try {
			processing = true;
			const data = {
				mtconnect_interval: Number(mtInterval),
				interval: Number(interval),
				threshold: Number(threshold)
			};
			const res = await axios.post(`${BACKEND_URL_LOCAL}/start/measurement`, data);
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
			<TextInput
				labelText="MTConnect data fetch interval"
				id="mtInterval"
				bind:value={mtInterval}
			/>
		</FormGroup>
		<FormGroup>
			<TextInput labelText="Sensor data fetch interval" id="interval" bind:value={interval} />
			<TextInput
				labelText="Sensor data difference threshold"
				id="threshold"
				bind:value={threshold}
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
