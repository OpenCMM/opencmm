<script lang="ts">
	import { Grid, Row, Column, ClickableTile } from 'carbon-components-svelte';
	import { page } from '$app/stores';
	import { _ } from 'svelte-i18n';
</script>

<div id="settings">
	<Grid>
		<Row>
			<Column>
				<ClickableTile
					href="/settings/language"
					light={$page.url.pathname === '/settings/language'}
				>
					{$_('settings.language.label')}
				</ClickableTile>
				<ClickableTile href="/settings/theme" light={$page.url.pathname === '/settings/theme'}>
					{$_('settings.theme.label')}
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
