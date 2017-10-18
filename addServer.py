import json
from subprocess import call
import shlex
import pexpect
import os
from pexpect import pxssh
import sys
import AutoDeployManager

deployManager = AutoDeployManager.AutoDeployManager()
deployManager.addServer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

'''
python3 addServer.py khalilleo/Githook-Test test1 45.77.110.160 root 'Uq*1R1,_QFLXB(=L' proj

config = {
    "name": "test1",
    "ip": "45.77.110.160",
    "user": "root",
    "password": "Uq*1R1,_QFLXB(=L",
    "path": "proj"
}
configServer(config, 'khalilleo/Githook-Test')
'''
