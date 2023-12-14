<script lang="ts">
	import DataTable from 'carbon-icons-svelte/lib/DataTable.svelte';
	import Add from 'carbon-icons-svelte/lib/Add.svelte';
	import ChartLineData from 'carbon-icons-svelte/lib/ChartLineData.svelte';
	import {
		SideNav,
		SideNavItems,
		SideNavMenu,
		SideNavMenuItem,
		SideNavLink,
		Content
	} from 'carbon-components-svelte';
	import Result from 'carbon-icons-svelte/lib/Result.svelte';

	import ChartStepper from 'carbon-icons-svelte/lib/ChartStepper.svelte';
	import { _ } from 'svelte-i18n';

	export let data;
	const modelId = data.modelId;
	const processId = data.processId;
	const baseUri = `/model/${modelId}/process/${processId}`;
</script>

<SideNav isOpen={true}>
	<SideNavItems>
		<SideNavLink href={`${baseUri}/result`} text={$_('home.result.title')} icon={Result} />
		<SideNavLink href={`${baseUri}/gcode`} text={$_('common.gcode')} icon={ChartStepper} />
		<SideNavLink text={$_('common.gcode') + '2D'} href={`${baseUri}/d3`} icon={ChartStepper} />
		<SideNavLink
			text={$_('home.file.3dmodel.createGcode')}
			href={`/file/setup?id=${modelId}`}
			icon={Add}
		/>
		<SideNavLink text="MTConnect" href={`${baseUri}/debug`} icon={ChartLineData} />
		<SideNavLink text="MTConnect 2D" href={`${baseUri}/mt`} icon={ChartLineData} />
		<SideNavLink
			href={`/model/processes?id=${modelId}`}
			text={$_('home.process.title')}
			icon={DataTable}
		/>
		<SideNavMenu text={$_('common.advanced')}>
			<SideNavMenuItem href={`${baseUri}/delays`} text="MTConnect Delays" />
		</SideNavMenu>
	</SideNavItems>
</SideNav>

<Content>
	<slot />
</Content>
