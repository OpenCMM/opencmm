## Start development server
```bash
poetry run uvicorn server.main:app
```

or 

```bash
poetry run start
```

## Lint
```bash
poetry run ruff check .
```


# Export requirements
```bash
poetry export -f requirements.txt --output requirements.txt
```

# Calibration of the camera
```bash
poetry run python calibration.py
```