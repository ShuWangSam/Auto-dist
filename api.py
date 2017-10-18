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

from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

ROOT = '/root/Auto-dist'

@app.route('/githook', methods=['POST'])
def githook():
    os.chdir(ROOT)
    data = request.get_json()
    pullRepo(data)
    return jsonify({})

def pullRepo(git_json):
    mapping = json.loads(open('./mapping.json').read())
    repo_name = "khalilleo/Githook-Test"#git_json['repository']['name']
    localPath = mapping[repo_name]['localPath']
    # First pull locally
    os.chdir(ROOT + '/' + localPath)
    call(shlex.split('git pull'))
    os.chdir(ROOT)
    # Then push
    servers = mapping[repo_name]['servers']
    for i in servers:
        doPull(localPath, i)
    print('succ')
    return

def doPull(localPath, server):
    os.chdir(localPath)
    commond = "git push " + server['name'] + " master"
    print("Running " + commond)
    child = pexpect.spawn(commond)
    child.sendline(commond)
    child.expect('root')
    child.sendline(server['password'])
    output = str(child.read()).replace('\\n', '')
    for o in output.split('\\r'):
        print(o.strip())
    print("================================")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081, debug=True, threaded=True)
    #pullRepo({})
