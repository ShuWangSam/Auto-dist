import json
from subprocess import call
import shlex
import pexpect
import os
from pexpect import pxssh

ROOT = '/root/Auto-dist'
#ROOT = '/Users/khalil/Documents/Auto-dist'

class AutoDeployManager:
    def __init__(self):
        pass

    def getMappingJson(self):
        return json.loads(open('./mapping.json').read())

    def runLocalCommond(self, commond):
        print("Running: " + commond)
        call(shlex.split(commond))

    def pullRepo(self, git_json):
        os.chdir(ROOT)
        mapping = self.getMappingJson()
        repo_name = git_json['repository']['full_name']
        localPath = mapping[repo_name]['localPath']
        branch = git_json['ref'].split("/")[-1]
        # First pull locally
        os.chdir(ROOT + '/' + localPath)

        #os.chdir(ROOT)
        # Then push
        servers = mapping[repo_name]['servers']
        for i in servers:
            if branch == i['branch']:
                self.doPull(i)
        print('Successfully push to all remote')
        return

    def doPull(self, server):
        '''
        if localPath:
            os.chdir(ROOT + '/' + localPath)
        '''
        # Switch branch locally
        #commond = 'git stash && git pull origin ' + server['branch'] + ' -f'
        self.runLocalCommond('git checkout -f ' + server['branch'])
        self.runLocalCommond('git reset -f origin/' + server['branch'])
        self.runLocalCommond('git pull origin ' + server['branch'])

        commond = "git push " + server['name'] + " " + server['branch']
        print("Running " + commond)
        child = pexpect.spawn(commond)
        child.sendline(commond)
        child.expect(server['user'])
        child.sendline(server['password'])
        output = str(child.read()).replace('\\n', '')
        for o in output.split('\\r'):
            print(o.strip())
        print("================================")

    # Add server
    def addGitRemote(self, server):
        commond = 'git remote add ' + server['name'] + ' ' + server['user'] + '@' + server["ip"] + ":" + server['path']
        self.runLocalCommond(commond)

    def sendCommond(self, pxssh, commond):
        pxssh.sendline(commond)
        pxssh.prompt()
        print(pxssh.before)

    def getPostReceiveContent(self, config):
        text = "'#!/bin/bash \n while \nread oldrev newrev ref \ndo if [[ $ref =~ .*/" + config['branch'] + "$ ]]; \nthen \ngit --work-tree=/var/www/" + config['deploy_path'] + ' --git-dir=/root/' + config['path'] + " checkout " + config['branch']  + " -f \nfi \ndone'"
        return text

    def getPostCheckoutContent(self, config):
        text = 'echo "Done customization"'
        return text

    def configServer(self, config ,repo_name):
        ip = config['ip']
        user = config['user']
        password = config['password']
        path = config['path']
        deploy_path = config['deploy_path']

        # ignore ssh key confirm
        # call(shlex.split('ssh-keyscan ' + ip + ' >> ~/.ssh/known_hosts'))
        POST_RECIEVE_FILE = 'http://khalil.one/ok/post-receive'
        POST_CHECKOUT_FILE = 'http://khalil.one/ok/post-checkout'

        try:
            s = pxssh.pxssh()
            s.login(ip, user, password)
            self.sendCommond(s, 'mkdir ' + path + ' && cd ~/' + path + ' && git init --bare')
            self.sendCommond(s, 'cd hooks && rm * -R')
            #self.sendCommond(s, 'wget ' + POST_RECIEVE_FILE + ' && chmod +x post-receive')
            #self.sendCommond(s, 'wget ' + POST_CHECKOUT_FILE + ' && chmod +x post-checkout')
            self.sendCommond(s, 'echo ' + self.getPostReceiveContent(config) + ' > post-receive && chmod +x post-receive')
            self.sendCommond(s, 'echo ' + self.getPostCheckoutContent(config) + ' > post-checkout && chmod +x post-checkout')

            s.logout()
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)
            return False

        return True

    def addServer(self, repoName, serverName, serverIP, serverUser, serverPassword, serverPath, deployPath, branch):
        repos = json.loads(open('mapping.json').read().strip())
        if repoName in repos:
            new_server = {
                "name": serverName,
                "ip": serverIP,
                "user": serverUser,
                "password": serverPassword,
                "path": serverPath,
                "deploy_path": deployPath,
                "branch": branch
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
            self.doPull(new_server)

    # Init proj
    def initProj(self, git_url):
        user = git_url.split('/')[-2]
        proj_name = git_url.split('/')[-1]
        full_name = user + '/' + proj_name
        if not os.path.isdir(user):
            commond = 'mkdir ' + user
            self.runLocalCommond(commond)
        os.chdir(user)
        commond = 'git clone ' + git_url
        self.runLocalCommond(commond)

        # Write to json
        os.chdir(ROOT)
        repos = json.loads(open('mapping.json').read().strip())
        if full_name not in repos:
            repos[full_name] = {}
            repos[full_name]['localPath'] = full_name
            repos[full_name]['servers'] = []
        else:
            print('Proj already exist')
            return
        f = open("mapping.json", 'w')
        f.write(json.dumps(repos))
        print("Proj init successfully")
