export const displayCoordinates = (x: number | null, y: number | null, z: number | null) => {
	if (x === null || y === null || z === null) {
		return '';
	}
	return `(${x}, ${y}, ${z})`;
};

export const displayLengthDifference = (length: number, rlength: number) => {
	if (!rlength) {
		return '';
	}
	return (rlength - length).toFixed(3);
};

export const displayRadius = (radius: number | null) => {
	if (radius === null) {
		return '';
	}
	return radius.toFixed(3);
};

export const displayLength = (length: number | null) => {
	if (length === null) {
		return '';
	}
	return length.toFixed(3);
};
