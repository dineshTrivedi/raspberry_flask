from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"

from datetime import datetime
from flask import request
from flask import jsonify

@app.route('/api/alert/email', methods=['POST'])
def alert_by_email():
    content = request.get_json()
    content['received_at'] = datetime.now()
    return jsonify({'received': content}), 200


if __name__ == '__main__':
    app.run(debug=True)