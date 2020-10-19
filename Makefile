migrate_settings:
	poetry run python -m migrations.003_settings_pickle_to_json

serve:
	poetry run python runserver.py 8000