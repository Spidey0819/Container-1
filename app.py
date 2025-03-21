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
    try:
        # Get JSON data with silent=True to avoid raising an exception for invalid JSON
        input_data = request.get_json(silent=True)

        # Check if data is None or missing required fields
        if input_data is None or 'file' not in input_data or 'product' not in input_data:
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            })

        file_name = input_data.get('file')
        product_details = input_data.get('product')

        # Additional validation
        if not file_name:
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            })

        file_path = os.path.join(PERSISTENT_STORAGE_PATH, file_name)

        if not os.path.exists(file_path):
            return jsonify({
                "file": file_name,
                "error": "File not found."
            })

        # Send a request to Container 2 to calculate the sum
        api_response = requests.post(
            'http://container2-service:90/sum',
            json={"file": file_name, "product": product_details},
            timeout=10
        )
        return jsonify(api_response.json())
    except Exception as e:
        logger.error(f"Error in calculate: {str(e)}")
        # If we have a file_name, use it in the error response
        if 'file_name' in locals() and file_name:
            return jsonify({
                "file": file_name,
                "error": "Error processing request."
            })
        # Otherwise return a null file response
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=False)

    #Trigger