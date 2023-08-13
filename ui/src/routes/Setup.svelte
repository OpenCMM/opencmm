<!-- set up the job config -->

<script lang="ts">
	import axios from 'axios';
	import { BACKEND_URL_LOCAL
	 } from '$lib/constants/backend';

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

<p>設定</p>

{#if error}
	<p class="error">{error}</p>
{/if}

  <form on:submit={handleSubmit}>
    <div>
      <label for="z">z:</label>
      <input type="text" id="z" bind:value={z} />
    </div>
    <div>
      <label for="cameraHeight">カメラの高さ:</label>
      <input type="text" id="cameraHeight" bind:value={cameraHeight} />
    </div>
    <div>
      <label for="feedRate">送り速度:</label>
      <input type="text" id="feedRate" bind:value={feedRate} />
    </div>
    <button type="submit">設定</button>
  </form>

{#if settingDone}
	<p>設定が完了しました</p>
{/if}

<style>
	.error {
		color: red;
	}
</style>