# run.py

from app import create_app

app = create_app(port=5555, debug=True)

if __name__ == '__main__':
    app.run()