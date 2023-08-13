<!-- set up the job config -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL
	 } from '$lib/constants/backend';
  import {
    Form,
    FormGroup,
    TextInput,
	Button,
  } from "carbon-components-svelte";

	 let z = 0;
	 let cameraHeight = 0;
	 let feedRate = 0;
	let error: string | null = null;
	export let settingDone: boolean = false;
	const handleSubmit = async (e: Event) => {
		e.preventDefault();

		const data = {
			z: Number(z),
			camera_height: Number(cameraHeight),
			feed_rate: Number(feedRate),
		};

		try {
			const res = await axios.post(`${BACKEND_URL_LOCAL}/setup/data`, data, {
				headers: {
					'Content-Type': 'application/json',
				},
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
	<p>設定</p>
  <Form on:submit={handleSubmit}>
	<FormGroup>
      <TextInput 
	  labelText="z"
	  id="z" bind:value={z} />
	</FormGroup>
	<FormGroup>
      <TextInput 
	  labelText="カメラの高さ"
	  id="cameraHeight" bind:value={cameraHeight} />
	</FormGroup>
	<FormGroup>
      <TextInput
	  labelText="送り速度"
	   id="feedRate" bind:value={feedRate} />
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

	.bx--form-item {
		margin: 1rem;
	}
</style>