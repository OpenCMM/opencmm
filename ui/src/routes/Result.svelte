<!-- show the result image -->

<script lang="ts">
	import { BACKEND_URL_LOCAL } from '$lib/constants/backend';
</script>

<p>結果</p>
<img id="result" src={`${BACKEND_URL_LOCAL}/load/image`} alt="result" />

<style>
	#result {
		max-width: 1000px;
	}
</style>
