<script lang="ts">
	import { Grid, Row, Column, ClickableTile } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';
</script>

<div id="settings">
	<Grid>
		<Row>
			<Column>
				<ClickableTile
					on:click={() => goto('/settings/language')}
					light={$page.url.pathname === '/settings/language'}
				>
					{$_('settings.language.label')}
				</ClickableTile>
				<ClickableTile
					on:click={() => goto('/settings/theme')}
					light={$page.url.pathname === '/settings/theme'}
				>
					{$_('settings.theme.label')}
				</ClickableTile>
				<ClickableTile
					on:click={() => goto('/settings/cnc')}
					light={$page.url.pathname === '/settings/cnc'}
				>
					{$_('settings.cnc.label')}
				</ClickableTile>
				<ClickableTile
					on:click={() => goto('/settings/mtconnect')}
					light={$page.url.pathname === '/settings/mtconnect'}
				>
					{$_('settings.mtconnect.label')}
				</ClickableTile>
				<ClickableTile
					on:click={() => goto('/settings/sensor')}
					light={$page.url.pathname === '/settings/sensor'}
				>
					{$_('settings.sensor.label')}
				</ClickableTile>
			</Column>
			<Column>
				<slot />
			</Column>
		</Row>
	</Grid>
</div>

<style>
	#settings {
		margin: 0 auto;
		width: 100%;
		max-width: 960px;
		margin-top: 2rem;
	}
</style>
