<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, Loading } from 'carbon-components-svelte';
	import { ToastNotification } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	let arcNumber = 4;
	let lineNumber = 2;
	let loaded = false;
	let saveFailed = false;
	let success = false;

	onMount(() => {
		// Load the settings here
		axios.get(`${BACKEND_URL}/get/edge_detection_config`).then((response) => {
			if (response.status === 200) {
				const data = response.data;
				arcNumber = data['arc_number'];
				lineNumber = data['line_number'];
				loaded = true;
			}
		});
	});

	const saveSettings = async (e: Event) => {
		e.preventDefault();
		try {
			const data = {
				arc_number: arcNumber,
				line_number: lineNumber
			};
			const res = await axios.post(`${BACKEND_URL}/update/edge_detection_config`, data, {
				headers: {
					'Content-Type': 'application/json'
				}
			});
			console.log(res);
			if (res.status === 200 && res.data['status'] === 'ok') {
				success = true;
			}
		} catch (err) {
			console.error(err);
			saveFailed = true;
		}
	};
</script>

{#if !loaded}
	<Loading />
{:else}
	<Form>
		<FormGroup>
			<TextInput
				bind:value={arcNumber}
				id="arcNumber"
				type="number"
				labelText={$_('settings.edge.arcNumber')}
			/>
			<TextInput
				bind:value={lineNumber}
				id="lineNumber"
				type="number"
				labelText={$_('settings.edge.lineNumber')}
			/>
		</FormGroup>
		<Button on:click={saveSettings}>{$_('common.save')}</Button>
	</Form>
{/if}

{#if success}
	<ToastNotification
		kind="success"
		title={$_('common.saveSuccess')}
		timeout={3000}
		on:close={() => (success = false)}
	/>
{/if}

{#if saveFailed}
	<ToastNotification
		kind="error"
		title={$_('common.saveFailed')}
		timeout={5000}
		on:close={() => (saveFailed = false)}
	/>
{/if}
