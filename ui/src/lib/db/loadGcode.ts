import { BACKEND_URL } from '$lib/constants/backend';

export interface GcodeLine {
	id: number; // line number
	x1: number;
	y1: number;
	x2: number;
	y2: number;
	feedrate: number;
}
export const loadGcodeLineData = async (modelId: string) => {
	const gcodeLines: GcodeLine[] = [];
	const res = await fetch(`${BACKEND_URL}/gcode/lines/${modelId}`);
	const data = await res.json();

	for (const d of data['lines']) {
		gcodeLines.push({
			id: d[0],
			x1: d[1],
			y1: d[2],
			x2: d[3],
			y2: d[4],
			feedrate: d[5]
		});
	}
	return gcodeLines;
};
