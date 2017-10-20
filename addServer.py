import json
from subprocess import call
import shlex
import pexpect
import os
from pexpect import pxssh
import sys
import AutoDeployManager

deployManager = AutoDeployManager.AutoDeployManager()
method = sys.argv[1]
available_methods = ['add_server', 'init_proj']
if method in available_methods:
    if method == 'add_server':
        deployManager.addServer(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
    if method == 'init_proj':
        # sys.argv[2]: github
        deployManager.initProj(sys.argv[2])
else:
    print('method not found')

'''
python3 addServer.py init_proj https://github.com/khalilleo/Githook-Test

python3 addServer.py add_server khalilleo/Githook-Test test1 45.77.110.160 root 'Uq*1R1,_QFLXB(=L' project1 API master

config = {
    "name": "test1",
    "ip": "45.77.110.160",
    "user": "root",
    "password": "Uq*1R1,_QFLXB(=L",
    "path": "proj"
}
configServer(config, 'khalilleo/Githook-Test')
'''
