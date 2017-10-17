import json
from subprocess import call
import shlex
import os

def addServer(repoName, serverName, serverIP, serverUser, serverPassword, serverPath):
    repos = json.loads(open('mapping.json').read().strip())
    if repoName in repos:
        new = {
            "name": serverName,
            "ip": serverIP,
            "user": serverUser,
            "password": serverPassword,
            "path": serverPath
          }
        repos[repoName]['servers'].append(new)
    else:
        return
    f = open("mapping.json", 'w')
    f.write(json.dumps(repos))
    f.close()
    # Login to server and config
    configServer(new)

def configServer(config):
    commond = "git push " + server['name'] + " master"
    print("Running " + commond)
    child = pexpect.spawn(commond)
    child.sendline(commond)
    child.expect('root')
    child.sendline(server['password'])
    output = str(child.read()).replace('\\n', '')


import sys
addServer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
