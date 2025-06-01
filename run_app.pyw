import os
import logging
from waitress import serve
from ugeeapp import app

pid_file = 'ugeeapp.pid'

logging.basicConfig(
    filename='ugeeapp.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

if __name__ == "__main__":
    pid = os.getpid()
    with open(pid_file, 'w') as f:
        f.write(str(pid))

    logging.info(f"App started with PID {pid}")

    try:
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except Exception as e:
        logging.exception("\nApp crashed")

    # Cleanup PID file on shutdown
    if os.path.exists(pid_file):
        os.remove(pid_file)
