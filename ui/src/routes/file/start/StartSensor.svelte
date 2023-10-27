<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, InlineLoading } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';
	import { page } from '$app/stores';
	import DownloadGCode from './DownloadGCode.svelte';

	const modelId = $page.url.searchParams.get('id');
	const advanced = $page.url.searchParams.get('advanced') === 'true';

	let error: string | null = null;
	let mtInterval = 5;
	let interval = 10;
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

<div class="steps-to-measure">
	<h2>{$_('home.start.howto.title')}</h2>
	<p>{$_('home.start.howto.step1')}</p>
	<p>{$_('home.start.howto.step2')}</p>
	<p>{$_('home.start.howto.step3')}</p>
	<p>{$_('home.start.howto.step4')}</p>
</div>

{#if modelId}
	<DownloadGCode {modelId} />
{/if}
<div class="bx--form-item">
	<h3>{$_('home.start.title')}</h3>
	<p class="start-description">{$_('home.start.description')}</p>

	<Form on:submit={startCapturing}>
		{#if advanced}
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
		{/if}
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
		margin-top: 2rem;
	}

	h2 {
		margin-top: 2rem;
		margin-bottom: 1rem;
	}

	.start-description {
		margin-top: 1rem;
		margin-bottom: 1rem;
	}

	.steps-to-measure {
		margin-top: 2rem;
		margin-bottom: 2rem;
	}
</style>
