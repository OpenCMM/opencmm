<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Tabs, Tab, TabContent } from 'carbon-components-svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import Edge from '../edge/Edge.svelte';
</script>

<Grid fullWidth>
	<Row>
		<Column>
			<Gcode />
		</Column>
		<Column>
			<Tabs autoWidth>
				<Tab label="Edge" />
				<Tab label="Line" />
				<svelte:fragment slot="content">
					<TabContent>
						<Edge />
					</TabContent>
				</svelte:fragment>
			</Tabs>
		</Column>
	</Row>
</Grid>
