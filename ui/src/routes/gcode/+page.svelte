<script lang="ts">
	import Gcode from './Gcode.svelte';
	import { Tabs, Tab, TabContent } from 'carbon-components-svelte';
	import { Grid, Row, Column } from 'carbon-components-svelte';
	import Arc from '../arc/Arc.svelte';
	import Edge from '../edge/Edge.svelte';
	import Line from '../line/Line.svelte';
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
				<Tab label="Arc" />
				<svelte:fragment slot="content">
					<TabContent>
						<Edge />
					</TabContent>
					<TabContent>
						<Line />
					</TabContent>
					<TabContent>
						<Arc />
					</TabContent>
				</svelte:fragment>
			</Tabs>
		</Column>
	</Row>
</Grid>
