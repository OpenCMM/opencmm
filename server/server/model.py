from server.config import MODEL_PATH
import os

def get_3dmodel_data():
	"""
	Get 3d model data on the model path.

	Data includes file name, file size, last modified time, and gcode status.
	"""

	models = os.listdir(MODEL_PATH)
	models.remove(".gitignore")
	models_data = []
	idx = 1
	for model in models:
		model_path = os.path.join(MODEL_PATH, model)
		model_size = os.path.getsize(model_path)
		model_modified_time = int(os.path.getmtime(model_path) * 1000)
		gcode_ready = os.path.exists(f"data/gcode/{model}.gcode")
		models_data.append(
			{
				"id": idx,
				"name": model,
				"size": model_size,
				"modified_time": model_modified_time,
				"gcode_ready": gcode_ready,
			}
		)
		idx += 1
	return models_data
