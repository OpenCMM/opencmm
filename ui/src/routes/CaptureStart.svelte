<!-- Start capturing images -->

<script lang="ts">
	import { BACKEND_URL_LOCAL
	 } from '$lib/constants/backend';
	import axios from 'axios';
	export let captureDone: boolean = false;
	let focalLength: number = 0;

	let sensorWidth: number = 0;

	let distance: number = 0;

	 const startCapturing = async (e: Event) => {
		e.preventDefault();

		const data = {
			focal_length: Number(focalLength),
			sensor_width: Number(sensorWidth),
			distance: Number(distance),
			is_full: false,
		};
		 try {
			 const res = await axios.post(`${BACKEND_URL_LOCAL}/process/start`, data, {
				 headers: {
					 'Content-Type': 'application/json',
				 },
			 });
			console.log(res);
			captureDone = true;
		 } catch (err) {
			 console.error(err);
		 }
	 };
</script>


<p>測定を開始します</p>

  <form on:submit={startCapturing}>
    <div>
      <label for="focalLength">focal length:</label>
      <input type="text" id="focalLength" bind:value={focalLength} />
    </div>
    <div>
      <label for="sensorWidth">sensor width:</label>
      <input type="text" id="sensorWidth" bind:value={sensorWidth} />
    </div>
    <div>
      <label for="distance">カメラとの距離:</label>
      <input type="text" id="distance" bind:value={distance} />
    </div>
    <button type="submit">測定開始</button>
  </form>
