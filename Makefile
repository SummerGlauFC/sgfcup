migrate_003:
	poetry run python -m migrations.003_settings_pickle_to_json

migrate_004:
	poetry run python -m migrations.004_file_details

migrate: migrate_003 migrate_004

serve:
	poetry run python runserver.py 8000