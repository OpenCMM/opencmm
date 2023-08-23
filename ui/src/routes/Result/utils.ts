export const displayCoordinates = (x: number, y: number, z: number) => {
	return `(${x}, ${y}, ${z})`;
};


export const displayLengthDifference = (length: number, rlength: number) => {
	return ((rlength - length) * 1000).toFixed(2);
};