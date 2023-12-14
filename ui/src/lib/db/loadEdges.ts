import { BACKEND_URL } from '$lib/constants/backend';

export interface Edge {
	id: number;
	x: number;
	y: number;
	z: number;
}

export const loadEdgeData = async (modelId: string, processId: string) => {
	const edges: Edge[] = [];
	const measuredEdges: Edge[] = [];
	if (processId === '') {
		const url = `${BACKEND_URL}/result/edges/${modelId}?with_offset=true`;
		const res = await fetch(url);
		const data = await res.json();
		for (const d of data['edges']) {
			edges.push({
				id: d[0],
				x: d[2],
				y: d[3],
				z: d[4]
			});
		}
		return { edges, measuredEdges };
	} else {
		const url = `${BACKEND_URL}/result/edges/result/combined/${modelId}/${processId}`;
		const res = await fetch(url);
		const data = await res.json();
		for (const d of data['edges']) {
			edges.push({
				id: d[0],
				x: d[1],
				y: d[2],
				z: d[3]
			});
			if (d[4] !== null) {
				measuredEdges.push({
					id: d[0],
					x: d[4],
					y: d[5],
					z: d[6]
				});
			}
		}
		return { edges, measuredEdges };
	}
};
