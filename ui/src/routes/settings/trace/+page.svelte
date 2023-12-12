<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, TextInput, Button, Loading } from 'carbon-components-svelte';
	import { ToastNotification } from 'carbon-components-svelte';
	import { onMount } from 'svelte';
	import { _ } from 'svelte-i18n';
	let minMeasureCount = 5;
	let maxFeedrate = 2500;
	let interval = 200;
	let margin = 2.5;
	let slopeNumber = 3;
	let loaded = false;
	let saveFailed = false;
	let success = false;

	onMount(() => {
		// Load the settings here
		axios.get(`${BACKEND_URL}/get/trace_config`).then((response) => {
			if (response.status === 200) {
				const data = response.data;
				minMeasureCount = data['min_measure_count'];
				maxFeedrate = data['max_feedrate'];
				interval = data['interval'];
				margin = data['margin'];
				slopeNumber = data['slope_number'];
				loaded = true;
			}
		});
	});

	const saveSettings = async (e: Event) => {
		e.preventDefault();
		try {
			const data = {
				min_measure_count: minMeasureCount,
				max_feedrate: maxFeedrate,
				interval,
				margin,
				slope_number: slopeNumber
			};
			const res = await axios.post(`${BACKEND_URL}/update/trace_config`, data, {
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
				bind:value={minMeasureCount}
				id="minMeasureCount"
				type="number"
				labelText={$_('settings.trace.minMeasureCount')}
			/>
			<TextInput
				bind:value={maxFeedrate}
				id="maxFeedrate"
				type="number"
				labelText={$_('settings.trace.maxFeedrate')}
			/>
			<TextInput
				bind:value={interval}
				id="interval"
				type="number"
				labelText={$_('settings.trace.interval')}
			/>
			<TextInput
				bind:value={margin}
				id="margin"
				type="number"
				step="0.01"
				labelText={$_('settings.trace.margin')}
			/>
			<TextInput
				bind:value={slopeNumber}
				id="slopeNumber"
				type="number"
				labelText={$_('settings.trace.slopeNumber')}
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
