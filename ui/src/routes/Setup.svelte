<!-- set up the job config -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import { Form, FormGroup, TextInput, Button } from 'carbon-components-svelte';

	let xOffset = 0;
	let yOffset = 0;
	let zOffset = 0;
	let cameraHeight = 300.0;
	let feedRate = 3000.0;
	let error: string | null = null;
	export let settingDone: boolean = false;
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
			settingDone = true;
		} catch (err) {
			console.error(err);
		}
	};
</script>

{#if error}
	<p class="error">{error}</p>
{/if}

<div class="bx--form-item">
	<p id="form-title">設定</p>
	<Form on:submit={handleSubmit}>
		<FormGroup>
			<TextInput
				labelText="カメラの高さ"
				id="cameraHeight"
				bind:value={cameraHeight}
				helperText="測定箇所から機械原点までのz軸の距離（カメラの高さ＋焦点の長さ）"
			/>
		</FormGroup>
		<FormGroup>
			<TextInput labelText="送り速度" id="feedRate" bind:value={feedRate} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="xオフセット" id="xOffset" bind:value={xOffset} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="yオフセット" id="yOffset" bind:value={yOffset} />
		</FormGroup>
		<FormGroup>
			<TextInput labelText="zオフセット" id="zOffset" bind:value={zOffset} />
		</FormGroup>
		<Button type="submit">設定</Button>
	</Form>
</div>

{#if settingDone}
	<p>設定が完了しました</p>
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
