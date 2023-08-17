<script lang="ts">
	import { Select, SelectItem } from 'carbon-components-svelte';
	import { _, locale } from 'svelte-i18n';

	const changeLanguage = (e: Event) => {
		const select = e.target as HTMLSelectElement;
		const lang = select.value;
		locale.set(lang);
	};
</script>

<Select labelText={$_('settings.language.label')} id="language" on:change={changeLanguage}>
	<SelectItem value="en" text="English" />
	<SelectItem value="ja" text="日本語" />
</Select>
