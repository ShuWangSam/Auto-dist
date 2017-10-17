import json
from subprocess import call
import shlex
import os

repos = json.loads(open('mapping.json').read().strip())
for repo_name in repos:
    localPath = repos[repo_name]['localPath']
    os.chdir(localPath)
    for server in repos[repo_name]['servers']:
        commond = 'git remote add ' + server['name'] + ' ' + server['user'] + '@' + server["ip"] + ":" + server['path']
        print("Running: " + commond)
        call(shlex.split(commond))
