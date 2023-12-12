<!-- set up the job config -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL } from '$lib/constants/backend';
	import { page } from '$app/stores';
	import { InlineLoading } from 'carbon-components-svelte';
	import { Form, FormGroup, NumberInput, Button, Checkbox } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';

	const modelId = $page.url.searchParams.get('id');
	let xOffset = 0;
	let yOffset = 0;
	let zOffset = 0;
	let measurementRange = 2.5;
	let measureFeedRate = 100.0;
	let moveFeedRate = 1000.0;
	let error: string | null = null;
	let settingDone = false;
	let loading = false;
	let sendFile = true;
	const handleSubmit = async (e: Event) => {
		loading = true;
		e.preventDefault();

		const data = {
			three_d_model_id: Number(modelId),
			measurement_range: Number(measurementRange),
			measure_feedrate: Number(measureFeedRate),
			move_feedrate: Number(moveFeedRate),
			x_offset: Number(xOffset),
			y_offset: Number(yOffset),
			z_offset: Number(zOffset),
			send_gcode: sendFile
		};

		try {
			const res = await axios.post(`${BACKEND_URL}/setup/data`, data, {
				headers: {
					'Content-Type': 'application/json'
				}
			});
			console.log(res);
			if (res.status === 200 && res.data['status'] === 'ok') {
				window.location.href = '/file/start?id=' + modelId;
				settingDone = true;
			} else {
				error = res.data['message'];
			}
		} catch (err) {
			console.error(err);
		}
		loading = false;
	};
</script>

{#if error}
	<p class="error">{error}</p>
{/if}

{#if settingDone}
	<p>{$_('home.setup.done')}</p>
{:else}
	<div class="bx--form-item">
		<p id="form-title">{$_('home.setup.title')}</p>
		<Form on:submit={handleSubmit}>
			<FormGroup>
				<NumberInput
					label={$_('home.setup.measurementRange.label')}
					id="measurementRange"
					min={0}
					step={0.01}
					bind:value={measurementRange}
				/>
				<NumberInput
					label={$_('home.setup.measureFeedRate.label')}
					id="measureFeedRate"
					min={0}
					bind:value={measureFeedRate}
				/>
				<NumberInput
					label={$_('home.setup.moveFeedRate.label')}
					id="moveFeedRate"
					min={0}
					bind:value={moveFeedRate}
				/>
			</FormGroup>
			<p>{$_('home.setup.offset')}</p>
			<FormGroup>
				<NumberInput label="x" id="xOffset" bind:value={xOffset} step={0.01} />
			</FormGroup>
			<FormGroup>
				<NumberInput label="y" id="yOffset" bind:value={yOffset} step={0.01} />
			</FormGroup>
			<FormGroup>
				<NumberInput label="z" id="zOffset" bind:value={zOffset} step={0.01} />
			</FormGroup>
			<FormGroup>
				<Checkbox bind:checked={sendFile} labelText={$_('home.setup.sendFile')} />
			</FormGroup>
			{#if loading}
				<InlineLoading description={$_('home.setup.loading')} />
			{:else}
				<Button type="submit">{$_('home.setup.submit')}</Button>
			{/if}
		</Form>
	</div>
{/if}

<style>
	.error {
		color: red;
	}

	#form-title {
		font-size: 1.2rem;
		font-weight: bold;
		margin: 1rem;
	}

	.bx--form-item {
		margin: 1rem;
	}
</style>
