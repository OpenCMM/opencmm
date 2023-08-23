<script>
	import {
		Content,
		Header,
		SkipToContent,
		HeaderUtilities,
		HeaderAction,
		HeaderPanelLinks,
		HeaderPanelLink,
		HeaderActionLink
	} from 'carbon-components-svelte';
	import Debug from 'carbon-icons-svelte/lib/Debug.svelte';
	import 'carbon-components-svelte/css/all.css';
	import { _ } from 'svelte-i18n';
	let isOpen = false;
</script>

<div class="app">
	<Header company="OpenCMM" href="/">
		<svelte:fragment slot="skip-to-content">
			<SkipToContent />
		</svelte:fragment>
		<HeaderUtilities>
			<HeaderActionLink href="/debug" aria-label="Debug" icon={Debug}>Debug</HeaderActionLink>
			<HeaderAction bind:isOpen>
				<HeaderPanelLinks>
					<HeaderPanelLink href="/settings/language">{$_('menu.settings')}</HeaderPanelLink>
				</HeaderPanelLinks>
			</HeaderAction>
		</HeaderUtilities>
	</Header>
	<main>
		<Content>
			<slot />
		</Content>
	</main>
</div>

<style>
	.app {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	main {
		flex: 1;
		display: flex;
		flex-direction: column;
		padding: 1rem;
		width: 100%;
		max-width: 64rem;
		margin: 0 auto;
		box-sizing: border-box;
	}
</style>
