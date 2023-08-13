<!-- show the result image -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
	import axios from 'axios';

	let resultImage: string = '';

	const getResultImage = async () => {
		try {
			const res = await axios.get(`${BACKEND_URL_LOCAL}/load/image`);
			console.log(res);
			resultImage = res.data;
		} catch (err) {
			console.error(err);
		}
	};
</script>

<p>結果</p>
<img id="result" src={`${BACKEND_URL_LOCAL}/load/image`} alt="result" />

<style>
	#result {
		width: 100%;
	}
</style>