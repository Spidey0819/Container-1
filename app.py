from flask import Flask, request, jsonify
import os
import requests
import logging
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERSISTENT_STORAGE_PATH = '/dhruv_PV_dir'

@app.route('/store-file', methods=['POST'])
def store_file():
    try:
        input_data = request.get_json()

        if input_data is None:
            logger.error("Null JSON input received")
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            })

        if 'file' not in input_data or 'data' not in input_data:
            logger.error(f"Missing required fields in input: {input_data}")
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
    except Exception as e:
        logger.error(f"Unexpected error in store_file: {str(e)}")
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        })

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        input_data = request.get_json(silent=True)

        if input_data is None:
            logger.error("Null JSON input received")
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            })

        if 'file' not in input_data:
            logger.error(f"Missing 'file' in input: {input_data}")
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            })

        if 'product' not in input_data:
            logger.error(f"Missing 'product' in input: {input_data}")
            return jsonify({
                "file": None,
                "error": "Invalid JSON input."
            })

        file_name = input_data.get('file')
        product_details = input_data.get('product')

        file_path = os.path.join(PERSISTENT_STORAGE_PATH, file_name)

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({
                "file": file_name,
                "error": "File not found."
            })

        try:
            # Send a request to Container 2 to calculate the sum
            logger.info(f"Sending request to container2-service for {file_name}, product {product_details}")
            api_response = requests.post(
                'http://container2-service:90/sum',
                json={"file": file_name, "product": product_details},
                timeout=10
            )
            response_json = api_response.json()
            logger.info(f"Received response from container2-service: {response_json}")
            return jsonify(response_json)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error communicating with Container 2: {str(e)}")
            return jsonify({
                "file": file_name,
                "error": "Error communicating with calculation service."
            })
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Container 2: {str(e)}")
            return jsonify({
                "file": file_name,
                "error": "Invalid response from calculation service."
            })
        except Exception as e:
            logger.error(f"Error communicating with Container 2: {str(e)}")
            return jsonify({
                "file": file_name,
                "error": "Internal Server Error"
            })
    except Exception as e:
        logger.error(f"Unexpected error in calculate: {str(e)}")
        return jsonify({
            "file": None,
            "error": "Invalid JSON input."
        })

if __name__ == '__main__':
    logger.info("Starting Container 1 application on port 6000")
    app.run(host='0.0.0.0', port=6000, debug=False)