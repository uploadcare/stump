web: gunicorn stump.wsgi --log-file - --log-level debug
worker: celery -A stump worker --events -l info 
beat: celery -A stump beat
