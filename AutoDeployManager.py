import json
from subprocess import call
import shlex
import pexpect
import os
from pexpect import pxssh

ROOT = '/root/Auto-dist'

class AutoDeployManager:
    def __init__(self):
        pass

    def getMappingJson(self):
        return json.loads(open('./mapping.json').read())

    def pullRepo(self, git_json):
        os.chdir(ROOT)
        mapping = self.getMappingJson()
        repo_name = git_json['repository']['full_name']
        localPath = mapping[repo_name]['localPath']
        # First pull locally
        os.chdir(ROOT + '/' + localPath)
        call(shlex.split('git pull'))
        os.chdir(ROOT)
        # Then push
        servers = mapping[repo_name]['servers']
        for i in servers:
            self.doPull(localPath, i)
        print('Successfully push to all remote')
        return

    def doPull(self, localPath, server):
        if localPath:
            os.chdir(ROOT + '/' + localPath)
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

    # Add server
    def addGitRemote(self, server):
        commond = 'git remote add ' + server['name'] + ' ' + server['user'] + '@' + server["ip"] + ":" + server['path']
        print("Running: " + commond)
        call(shlex.split(commond))

    def sendCommond(self, pxssh, commond):
        pxssh.sendline(commond)
        pxssh.prompt()
        print(pxssh.before)

    def configServer(self, config ,repo_name):
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
            self.sendCommond(s, 'mkdir ' + path + ' && cd ~/' + path + ' && git init --bare')
            self.sendCommond(s, 'cd hooks && rm * -R')
            self.sendCommond(s, 'wget ' + POST_RECIEVE_FILE + ' && chmod +x post-receive')
            self.sendCommond(s, 'wget ' + POST_CHECKOUT_FILE + ' && chmod +x post-checkout')
            s.logout()
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)
            return False

        return True

    def addServer(self, repoName, serverName, serverIP, serverUser, serverPassword, serverPath):
        repos = json.loads(open('mapping.json').read().strip())
        if repoName in repos:
            new_server = {
                "name": serverName,
                "ip": serverIP,
                "user": serverUser,
                "password": serverPassword,
                "path": serverPath
              }
            repos[repoName]['servers'].append(new_server)
        else:
            return
        f = open("mapping.json", 'w')
        f.write(json.dumps(repos))
        f.close()
        # Login to server and config
        localPath = repos[repoName]['localPath']
        if self.configServer(new_server, repoName):
            # if setup succ, do add remote and pull
            os.chdir(localPath)
            self.addGitRemote(new_server)
            self.doPull(None, new_server)
