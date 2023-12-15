import { BACKEND_URL } from '$lib/constants/backend';

export interface ModelLine {
	id: number;
	x1: number;
	y1: number;
	x2: number;
	y2: number;
}

export interface Arc {
	id: number;
	radius: number;
	cx: number;
	cy: number;
}

export const loadModelShapeData = async (modelId: string) => {
	const lines: ModelLine[] = [];
	const res = await fetch(`${BACKEND_URL}/model/shapes/${modelId}`);
	const data = await res.json();

	for (const d of data['lines']) {
		lines.push({
			id: d[0],
			x1: d[1],
			y1: d[2],
			x2: d[3],
			y2: d[4]
		});
	}
	// for (const d of data['arcs']) {
	// 	arcs.push({
	// 		id: d[0],
	// 		radius: d[1],
	// 		cx: d[2],
	// 		cy: d[3]
	// 	});
	// }
	return lines;
};
