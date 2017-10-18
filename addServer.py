import json
from subprocess import call
import shlex
import pexpect
import os
from pexpect import pxssh

def doPull(localPath, server):
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
    if configServer(new, repoName):
        doPull(repos[repoName]['localPath'], new)

def sendCommond(pxssh, commond):
    pxssh.sendline(commond)
    pxssh.prompt()
    print(pxssh.before)

def configServer(config ,repo_name):
    ip = config['ip']
    user = config['user']
    password = config['password']
    path = config['path']

    # ignore ssh key confirm
    #call(shlex.split('ssh-keyscan ' + ip + ' >> ~/.ssh/known_hosts'))
    POST_RECIEVE_FILE = 'http://khalil.one/ok/post-receive'
    POST_CHECKOUT_FILE = 'http://khalil.one/ok/post-checkout'

    try:
        s = pxssh.pxssh()
        s.login(ip, user, password)
        sendCommond(s, 'mkdir ' + path + ' && cd ~/' + path + ' && git init --bare')
        sendCommond(s, 'cd hooks && rm * -R')
        sendCommond(s, 'wget ' + POST_RECIEVE_FILE + ' && chmod +x post-receive')
        sendCommond(s, 'wget ' + POST_CHECKOUT_FILE + ' && chmod +x post-checkout')
        s.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(e)
        return False

    return True


import sys
addServer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

'''
python3 addServer.py khalilleo/Githook-Test test1 45.77.110.160 root Uq*1R1,_QFLXB(=L proj

config = {
    "name": "test1",
    "ip": "45.77.110.160",
    "user": "root",
    "password": "Uq*1R1,_QFLXB(=L",
    "path": "proj"
}
configServer(config, 'khalilleo/Githook-Test')
'''
