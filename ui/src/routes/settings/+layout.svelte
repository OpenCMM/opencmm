<script lang="ts">
	import { Grid, Row, Column, ClickableTile, Content } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { _ } from 'svelte-i18n';
	import { goto } from '$app/navigation';
</script>

<Content>
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
					<ClickableTile
						on:click={() => goto('/settings/edge')}
						light={$page.url.pathname === '/settings/edge'}
					>
						{$_('settings.edge.label')}
					</ClickableTile>
					<ClickableTile
						on:click={() => goto('/settings/trace')}
						light={$page.url.pathname === '/settings/trace'}
					>
						{$_('settings.trace.label')}
					</ClickableTile>
				</Column>
				<Column>
					<slot />
				</Column>
			</Row>
		</Grid>
	</div>
</Content>

<style>
	#settings {
		margin: 0 auto;
		width: 100%;
		max-width: 960px;
		margin-top: 2rem;
	}
</style>
