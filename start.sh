docker compose up -d
source venv/bin/activate
wait
python3.9 manage.py runserver
