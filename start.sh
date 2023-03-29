# python3 ./frontend/run.py & flask --app ./memcache/run_cache.py run --port 5555 &

python3 run_frontend.py &
python3 flask_cache.py &
python3 ./manager/run.py & 
python3 ./Auto-Scaler/run.py
echo "project started"

# gunicorn --bind 0.0.0.0:5000 flask_frontend:webapp &
