
def get_final_coordinates(gcode_filepath: str):
	"""
	Get final coordinates from gcode file
	"""
	with open(gcode_filepath, "r") as f:
		lines = f.readlines()
		last_line = lines[-3]
		xyz = last_line.split(" ")
		x = float(xyz[1][1:])
		y = float(xyz[2][1:])
		z = float(xyz[3][1:])
		return (x, y, z)