<!-- Download the GCode -->

<script lang="ts">
	import { BACKEND_URL_LOCAL
	 } from '$lib/constants/backend';
	import axios from 'axios';
  import {
	Button,
  } from "carbon-components-svelte";

	 const downloadGCode = async () => {
		 try {
			 const res = await axios.get(`${BACKEND_URL_LOCAL}/download/gcode`);
			 console.log(res);
			 const textContent = res.data;
    const blob = new Blob([textContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement("a");
    link.href = url;
    link.download = "opencmm.gcode";
    link.click();
    
    URL.revokeObjectURL(url);

		 } catch (err) {
			 console.error(err);
		 }
	 };
</script>


<div class="bx--form-item">
<p>GCodeをダウンロードしてください</p>
<Button on:click={downloadGCode} >ダウンロード</Button>
</div>

<style>
	.bx--form-item {
		margin: 1rem;
	}
</style>