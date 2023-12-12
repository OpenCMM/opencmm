<script lang="ts">
	import { BACKEND_URL } from '$lib/constants/backend';
	import axios from 'axios';
	import { Form, FormGroup, NumberInput, Button, Loading } from 'carbon-components-svelte';
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
			<NumberInput
				value={minMeasureCount}
				id="minMeasureCount"
				min={1}
				label={$_('settings.trace.minMeasureCount')}
			/>
			<NumberInput
				value={maxFeedrate}
				id="maxFeedrate"
				min={0}
				label={$_('settings.trace.maxFeedrate')}
			/>
			<NumberInput value={interval} id="interval" min={0} label={$_('settings.trace.interval')} />
			<NumberInput value={margin} id="margin" step={0.01} label={$_('settings.trace.margin')} />
			<NumberInput
				value={slopeNumber}
				id="slopeNumber"
				min={2}
				label={$_('settings.trace.slopeNumber')}
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
