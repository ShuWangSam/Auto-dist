from flask import logging, Flask, Response, jsonify, request, url_for, redirect, render_template
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
    data = request.get_json()
    deployManager.pullRepo(data)
    return jsonify({})

@app.route('/init_proj')
def init_proj():
    return render_template("init_proj.html", route='init_proj')

@app.route('/all_proj')
def all_proj():
    repos = json.loads(open('mapping.json').read().strip())
    new = []
    for i in repos:
        data = {
        'name': i,
        'url': repos[i]['localPath'],
        'numOfServers': len(repos[i]['servers']),
        }
        new.append(data)
    return render_template("all_proj.html", route = 'all_proj', data = new)

@app.route('/add_server')
def add_server():
    repos = json.loads(open('mapping.json').read().strip())
    new = []
    for i in repos:
        new.append(i)
    return render_template("add_server.html", route='add_server', data=new)

@app.route('/all_server')
def all_server():
    repos = json.loads(open('mapping.json').read().strip())
    new = []
    for proj in repos:
        for server in repos[proj]['servers']:
            server['proj'] = proj
            new.append(server)
    return render_template("all_server.html", route='all_server', data = new)

@app.route('/do/init_proj', methods=['POST'])
def do_init_proj():
    data = json.loads(request.form.get("payload"))
    git_url = data['git_url']
    result = deployManager.initProj(git_url)
    return jsonify(result)


@app.route('/do/add_server', methods=['POST'])
def do_add_server():
    data = json.loads(request.form.get("payload"))
    project = data['project']
    name = data['name']
    ip = data['ip']
    user = data['user']
    password = data['password']
    path = data['path']
    deploy_path = data['deploy_path']
    branch = data['branch']
    result = deployManager.addServer(project, name, ip, user, password, path, deploy_path, branch)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    #pullRepo({})
