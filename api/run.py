#!/usr/bin/env python3
import logging
import sys
from flask import jsonify, request
from app import create_app
from flask_cors import CORS

# Configure logging
# logging.basicConfig(level=logging.INFO,
#                         format='%(levelname)s - %(message)s',
#                         datefmt='%Y-%m-%d %H:%M:%S')


# logging.basicConfig(filename='test.log', level=logging.DEBUG)

#logger = logging.getLogger(__name__)

app = create_app('default')
CORS(app, resources={r"/*": {"origins": "http://my-garden:3000"}})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
