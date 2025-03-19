from flask import Flask, request, jsonify
import os
import requests
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERSISTENT_STORAGE_PATH = '/dhruv_PV_dir'

@app.route('/store-file', methods=['POST'])
def store_file():
    input_data = request.get_json()

    if not input_data or 'file' not in input_data or 'data' not in input_data:
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        })

    file_name = input_data.get('file')
    file_data = input_data.get('data')

    file_path = os.path.join(PERSISTENT_STORAGE_PATH, file_name)

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the file data to the persistent storage
        with open(file_path, 'w') as f:
            f.write(file_data)

        logger.info(f"File {file_name} stored successfully.")
        return jsonify({
            "file": file_name,
            "message": "Success."
        })
    except Exception as e:
        logger.error(f"Error storing file: {str(e)}")
        return jsonify({
            "file": file_name,
            "error": "Error while storing the file to the storage."
        })

@app.route('/calculate', methods=['POST'])
def calculate():
    input_data = request.get_json()

    if not input_data or 'file' not in input_data or 'product' not in input_data:
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        })

    file_name = input_data.get('file')
    product_details = input_data.get('product')

    file_path = os.path.join(PERSISTENT_STORAGE_PATH, file_name)

    if not os.path.exists(file_path):
        return jsonify({
            "file": file_name,
            "error": "File not found."
        })

    try:
        # Send a request to Container 2 to calculate the sum
        api_response = requests.post(
            'http://container2-service:90/sum',
            json={"file": file_name, "product": product_details}
        )
        return jsonify(api_response.json())
    except Exception as e:
        logger.error(f"Error communicating with Container 2: {str(e)}")
        return jsonify({
            "error": "Internal Server Error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=False)