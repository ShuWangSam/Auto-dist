import json
from subprocess import call
import shlex
import pexpect
import os
from pexpect import pxssh

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
    configServer(new, repoName)

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
    '''
    commond = "ssh " + user + '@' + ip
    print("Running " + commond)
    child = pexpect.spawn(commond)
    child.expect(user)
    child.sendline(config['password'])
    #output = str(child.read()).replace('\\n', '')
    print(child.before)
    #child = pexpect.spawn('git clone https://github.com/' + repo_name)
    child.prompt()
    child.sendline('pwd')
    print(child.read())
    '''
    try:
        s = pxssh.pxssh()
        s.login(ip, user, password)
        sendCommond(s, 'cd ~')
        sendCommond(s, 'git clone https://github.com/' + repo_name + ' ' + path)
        s.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(e)

'''
import sys
addServer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
'''
config = {
    "name": "test1",
    "ip": "45.77.110.160",
    "user": "root",
    "password": "Uq*1R1,_QFLXB(=L",
    "path": "proj"
}
configServer(config, 'khalilleo/Githook-Test')
