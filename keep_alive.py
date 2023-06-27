from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def root():
    return "I'm alive!", 200


def run_flask_app():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    flask_app_thread = Thread(target=run_flask_app)
    flask_app_thread.start()
