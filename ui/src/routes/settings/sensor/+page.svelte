<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, Button, Loading, NumberInput } from 'carbon-components-svelte';
	import { ToastNotification } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	let interval = 700;
	let threshold = 3.0;
	let beamDiameter = 120.0;
	let middleOutput = 9400.0;
	let responseTime = 10.0;
	let tolerance = 0.3;
	let loaded = false;
	let saveFailed = false;
	let success = false;

	onMount(() => {
		// Load the settings here
		axios.get(`${BACKEND_URL}/get/sensor_config`).then((response) => {
			if (response.status === 200) {
				const data = response.data;
				interval = data['interval'];
				threshold = data['threshold'];
				beamDiameter = data['beam_diameter'];
				middleOutput = data['middle_output'];
				responseTime = data['response_time'];
				tolerance = data['tolerance'];
				loaded = true;
			}
		});
	});

	const saveSettings = async (e: Event) => {
		e.preventDefault();
		try {
			const data = {
				interval,
				threshold,
				beam_diameter: beamDiameter,
				middle_output: middleOutput,
				response_time: responseTime,
				tolerance
			};
			const res = await axios.post(`${BACKEND_URL}/update/sensor_config`, data, {
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
			<NumberInput value={interval} id="interval" min={0} label={$_('settings.sensor.interval')} />
			<NumberInput
				bind:value={threshold}
				id="threshold"
				min={0}
				step={0.01}
				label={$_('settings.sensor.threshold')}
			/>
			<NumberInput
				value={beamDiameter}
				id="beamDiameter"
				min={0}
				label={$_('settings.sensor.beamDiameter')}
			/>
			<NumberInput
				bind:value={middleOutput}
				id="middleOutput"
				label={$_('settings.sensor.middleOutput')}
			/>
			<NumberInput
				value={responseTime}
				id="responseTime"
				min={0}
				label={$_('settings.sensor.responseTime')}
			/>
			<NumberInput
				value={tolerance}
				id="tolerance"
				step={0.01}
				min={0}
				label={$_('settings.sensor.tolerance')}
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
