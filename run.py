# run.py
from waitress import serve
from ugeeapp import app

#app = create_app()

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000,threads=4)
# if __name__ == '__main__':

#     app.run(debug=True, use_reloader=True)