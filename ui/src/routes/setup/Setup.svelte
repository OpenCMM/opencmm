<!-- set up the job config -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { Form, FormGroup, TextInput, Button } from 'carbon-components-svelte';
	import { _ } from 'svelte-i18n';

	let xOffset = 0;
	let yOffset = 0;
	let zOffset = 0;
	let cameraHeight = 300.0;
	let feedRate = 3000.0;
	let error: string | null = null;
	let settingDone: boolean = false;
	const handleSubmit = async (e: Event) => {
		e.preventDefault();

		const data = {
			camera_height: Number(cameraHeight),
			feed_rate: Number(feedRate),
			x_offset: Number(xOffset),
			y_offset: Number(yOffset),
			z_offset: Number(zOffset)
		};

		try {
			const res = await axios.post(`${BACKEND_URL_LOCAL}/setup/data`, data, {
				headers: {
					'Content-Type': 'application/json'
				}
			});
			console.log(res);
			if (res.status === 200 && res.data["status"] === 'ok') {
				settingDone = true;
				window.location.href = '/start';
			} else {
				error = res.data["message"];
			}
		} catch (err) {
			console.error(err);
		}
	};
</script>

{#if error}
	<p class="error">{error}</p>
{/if}

<div class="bx--form-item">
	<p id="form-title">{$_('home.setup.title')}</p>
	<Form on:submit={handleSubmit}>
		<FormGroup>
			<TextInput
				labelText={$_('home.setup.cameraHeight.label')}
				id="cameraHeight"
				bind:value={cameraHeight}
				helperText=""
			/>
		</FormGroup>
		<FormGroup>
			<TextInput labelText={$_('home.setup.feedRate.label')} id="feedRate" bind:value={feedRate} />
		</FormGroup>
		<p>{$_('home.setup.offset')}</p>
		<FormGroup>
			<TextInput labelText="x" id="xOffset" bind:value={xOffset} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="y" id="yOffset" bind:value={yOffset} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="z" id="zOffset" bind:value={zOffset} />
		</FormGroup>
		<Button type="submit">{$_('home.setup.submit')}</Button>
	</Form>
</div>

{#if settingDone}
	<p>{$_('home.setup.done')}</p>
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
