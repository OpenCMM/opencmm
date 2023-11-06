<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, Loading } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	let cncIpAddress = '';
	let username = '';
	let password = '';
	let sharedFolder = '';
	let loaded = false;

	onMount(() => {
		// Load the settings here
		axios.get(`${BACKEND_URL}/get_first_machine`).then((response) => {
			console.log({ response });
			cncIpAddress = response.data[1];
			username = response.data[2];
			password = response.data[3];
			sharedFolder = response.data[4];
			loaded = true;
		});
	});

	function saveSettings() {
		// Save the settings here
	}
</script>

{#if !loaded}
	<Loading />
{:else}
	<Form>
		<FormGroup>
			<TextInput bind:value={cncIpAddress} id="cnc-ip-address" labelText={$_('settings.cnc.ip')} />
			<TextInput bind:value={username} id="username" labelText={$_('settings.cnc.username')} />
			<TextInput
				bind:value={password}
				id="password"
				labelText={$_('settings.cnc.password')}
				type="password"
			/>
			<TextInput
				bind:value={sharedFolder}
				id="sharedFolder"
				labelText={$_('settings.cnc.sharedFolder')}
			/>
		</FormGroup>
		<Button on:click={saveSettings}>{$_('common.save')}</Button>
	</Form>
{/if}
