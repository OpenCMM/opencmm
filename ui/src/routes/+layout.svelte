<script>
	import {
		Header,
		SkipToContent,
		HeaderUtilities,
		HeaderAction,
		HeaderPanelLinks,
		HeaderPanelLink
	} from 'carbon-components-svelte';
	import 'carbon-components-svelte/css/all.css';
	import { _ } from 'svelte-i18n';
	let isOpen = false;
</script>

<svelte:head>
	<title>OpenCMM</title>
</svelte:head>

<div class="app">
	<Header company="OpenCMM" href="/">
		<svelte:fragment slot="skip-to-content">
			<SkipToContent />
		</svelte:fragment>
		<HeaderUtilities>
			<HeaderAction bind:isOpen>
				<HeaderPanelLinks>
					<HeaderPanelLink href="/settings/language">{$_('menu.settings')}</HeaderPanelLink>
					<HeaderPanelLink href="/sendfile">{$_('menu.sendFile')}</HeaderPanelLink>
				</HeaderPanelLinks>
			</HeaderAction>
		</HeaderUtilities>
	</Header>
	<main>
		<slot />
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
		margin: 0 auto;
		box-sizing: border-box;
	}
</style>
