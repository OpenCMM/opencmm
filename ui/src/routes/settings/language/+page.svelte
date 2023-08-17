<script lang="ts">
	import { Select, SelectItem } from 'carbon-components-svelte';
	import { _, locale, locales } from 'svelte-i18n';

	let selected = $locale ? $locale : 'en';
	const changeLanguage = (e: Event) => {
		const select = e.target as HTMLSelectElement;
		const lang = select.value;
		locale.set(lang);
	};

	const languages: { [lang: string]: string } = {
		en: 'English',
		ja: '日本語'
	};
</script>

<Select
	labelText={$_('settings.language.label')}
	id="language"
	{selected}
	on:change={changeLanguage}
>
	{#each $locales as locale}
		<SelectItem value={locale} text={languages[locale]} />
	{/each}
</Select>
