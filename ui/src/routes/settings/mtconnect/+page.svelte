<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, Loading } from 'carbon-components-svelte';
	import { ToastNotification } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	let url = '';
	let interval = 100;
	let latency = 30;
	let loaded = false;
	let saveFailed = false;
	let success = false;

	onMount(() => {
		// Load the settings here
		axios.get(`${BACKEND_URL}/get/mtconnect_config`).then((response) => {
			if (response.status === 200) {
				const data = response.data;
				url = data['url'];
				interval = data['interval'];
				latency = data['latency'];
				console.log(data);
				loaded = true;
			}
		});
	});

	const saveSettings = async (e: Event) => {
		e.preventDefault();
		try {
			const data = {
				url,
				interval,
				latency
			};
			const res = await axios.post(`${BACKEND_URL}/update/mtconnect_config`, data, {
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
			<TextInput bind:value={url} id="url" labelText={$_('settings.mtconnect.url')} />
			<TextInput
				bind:value={interval}
				id="interval"
				type="number"
				labelText={$_('settings.mtconnect.interval')}
			/>
			<TextInput
				bind:value={latency}
				id="latency"
				type="number"
				labelText={$_('settings.mtconnect.latency')}
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
