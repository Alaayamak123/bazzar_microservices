from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

CATALOG_SERVER_URL = "http://172.18.160.1:4000"
ORDER_SERVER_URL = "http://172.18.160.1:5000"

@app.get('/test')
def test_front_tier():
    return jsonify({
        'success': True
    })


@app.get('/search/<string:item_type>')
def search(item_type):
    try:
        response = requests.get(
            f"{CATALOG_SERVER_URL}/books/search/{item_type}")
        data = response.json()
        app.logger.info(f"Response from catalog server: {data}")
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.get('/info/<int:item_number>')
def info(item_number):
    try:
        response = requests.get(f"{CATALOG_SERVER_URL}/books/{item_number}")
        data = response.json()
        app.logger.info(f"Response from catalog server: {data}")
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.post('/purchase/<int:item_id>')
def purchase(item_id):
    try:
        response = requests.post(f"{ORDER_SERVER_URL}/purchase/{item_id}")
        data = response.json()
        app.logger.info(f"Response from order server: {data}")
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
