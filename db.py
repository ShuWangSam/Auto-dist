from pymongo import MongoClient
import json
import pprint
from bson.objectid import ObjectId

DB_URL = 'mongodb://lvyuan95:1q2w3e4r@auto-deply-shard-00-00-zvd2m.mongodb.net:27017,auto-deply-shard-00-01-zvd2m.mongodb.net:27017,auto-deply-shard-00-02-zvd2m.mongodb.net:27017/test?ssl=true&replicaSet=auto-deply-shard-0&authSource=admin'

class db:
    def __init__(self):
        self.client = MongoClient(DB_URL)
        self.db = self.client.auto

    def getAllRepo(self):
        repos = self.db.repo.find()
        result = {}
        for i in repos:
            result[i['name']] = {
                "localPath": i['localPath'],
                "servers": []
            }
            for server_id in i['servers']:
                #print(server_id)
                server = self.db.server.find_one({"_id": ObjectId(server_id)})
                if not server['deleted']:
                    result[i['name']]['servers'].append(server)
        return result

    def addServer(self, newServer, repoName):
        server_id = self.db.server.insert_one(newServer).inserted_id

        self.db.repo.update_one({
          'name': repoName
        },{
          '$push': {
            'servers': str(server_id)
          }
        }, upsert=False)
        return True

    def addProject(self, name, localPath):
        proj = {'name': name, "localPath": localPath, 'servers': []}
        self.db.repo.insert_one(proj)
        return True

    def deleteServer(self, server_id):
        # Just hide, not really delete
        self.db.server.update_one({
          '_id': ObjectId(server_id)
        },{
          '$set': {
            'deleted': True
          }
        })
        return {'status': 0}

a = db()
a.deleteServer('59fcd459b8979b390593aa64')

# print(a.getAllRepo())
# print(a.addServer({'name': '123'}, 'khalilleo/augustctl'))
