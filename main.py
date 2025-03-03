from flask import Flask, render_template
from waitress import serve

DEBUG = True

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    if DEBUG:
        print('Running debug server on http://localhost:8000...')
        app.run(host='0.0.0.0', port=8000, debug=True)

    else:
        # For production, use Waitress
        print("Starting production server on port 8000...")
        serve(app, host='0.0.0.0', port=8000)