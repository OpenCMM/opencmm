import { BACKEND_URL } from '$lib/constants/backend';

export interface Edge {
	id: number;
	x: number;
	y: number;
}

export const loadEdgeData = async (modelId: string, processId: string) => {
	const edges: Edge[] = [];
	const measuredEdges: Edge[] = [];
	const res = await fetch(`${BACKEND_URL}/result/edges/result/combined/${modelId}/${processId}`);
	const data = await res.json();
	for (const d of data['edges']) {
		edges.push({
			id: d[0],
			x: d[1],
			y: d[2]
		});
		if (d[4] !== null) {
			measuredEdges.push({
				id: d[0],
				x: d[4],
				y: d[5]
			});
		}
	}
	return { edges, measuredEdges };
};
