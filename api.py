from flask import logging, Flask, Response, jsonify, request, url_for, redirect
import sys
import os
from functools import wraps
import json
import time
import random
import urllib.parse
from subprocess import call
import shlex
import pexpect
import AutoDeployManager

from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

deployManager = AutoDeployManager.AutoDeployManager()

@app.route('/githook', methods=['POST'])
def githook():
    os.chdir(ROOT)
    data = request.get_json()
    deployManager.pullRepo(data)
    return jsonify({})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True, threaded=True)
    #pullRepo({})
