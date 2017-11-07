import MySQLdb
import json
import pprint

DB_HOST = "sql9.freemysqlhosting.net"
DB_USER = "sql9203618"
DB_PASSWORD = "RVuDFfuDXM"
DB_NAME = "sql9203618"

class mysql:
    def __init__(self):
        pass

    def connect(self):
        self.db = MySQLdb.connect(
                     host=DB_HOST,    # your host, usually localhost
                     user=DB_USER,         # your username
                     passwd=DB_PASSWORD,  # your password
                     db=DB_NAME)        # name of the data base
        self.cur = self.db.cursor()

    def query(self, commond):
        self.connect()
        self.cur.execute(commond)
        return self.cur.fetchall()
        # try:
        #     self.connect()
        #     self.cur.execute(commond)
        #     return self.cur.fetchall()
        # except:
        #     return False

    def get_last_insert_id(self):
        try:
            self.cur.execute("SELECT LAST_INSERT_ID() ;")
            return self.cur.fetchall()[0][0]
        except:
            return False

    def insert(self, commond):
        try:
            self.connect()
            self.cur.execute(commond)
            self.db.commit()
            new_object_id = self.get_last_insert_id()
            return new_object_id
        except:
            self.db.rollback()
            return None

    def update(self, commond):
        try:
            self.connect()
            self.cur.execute(commond)
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return None

    def getAllRepo(self):
        query = self.query("SELECT id, name, localPath FROM Project")
        result = {}
        for row in query:
            result[row[1]] = {
                "id": row[0],
                "localPath": row[2],
                "servers": self.getServerForProject(row[0])
            }
        return result

    def getServerForProject(self, projectId):
        result = self.query("\
                            SELECT \
                                project.ID as 'project_id', \
                                server.ID as 'server_id', \
                                server.name as 'server_name', \
                                server.ip as 'server_ip', \
                                server.user as 'server_user', \
                                server.password as 'server_password', \
                                server.path as 'server_path', \
                                server.deploy_path as 'server_deploy_path', \
                                server.branch as 'server_branch' \
                            From\
                                Project project\
                                    INNER JOIN\
                                Relation relation ON (project.id = relation.repo_id)\
                                    INNER JOIN\
                                Server server ON (relation.server_id = server.id)\
                            WHERE project.id = " + str(projectId) + " AND server.deleted = 0")

        #clean up result
        servers = []
        #print(result)
        for row in result:
                servers.append(
                    {
                        "id": row[1],
                        "name": row[2],
                        "ip": row[3],
                        "user": row[4],
                        "password": row[5],
                        "path": row[6],
                        "deploy_path": row[7],
                        "branch": row[8]
                    }
                )
        return servers

    def addServer(self, newServer, projectId):
        # Add server
        commond = "INSERT INTO Server (name,ip,user,password, path, deploy_path, branch, deleted) VALUES ('" + newServer['name'] +"','" + newServer['ip'] +"', '" + newServer['user'] +"', '" + newServer['password'] +\
        "', '" + newServer['path'] + "', '" + newServer['deploy_path'] +"', '" + newServer['branch'] + "', 0);"
        new_server_id = self.insert(commond)

        if new_server_id:
            return self.addRelation(new_server_id, projectId)
        else:
            return False

    def addRelation(self, serverId, projectId):
        commond = "INSERT INTO Relation (server_id, repo_id) VALUES (" + str(serverId) +", " + str(projectId) + ");"
        return self.insert(commond)

    def addProject(self, name, localPath):
        commond = "INSERT INTO Project (name, localPath) VALUES ('" + name +"', '" + localPath + "');"
        return self.insert(commond)

    def deleteServer(self, server_id):
        # Just hide, not really delete
        return self.update("UPDATE Server SET deleted=1 WHERE id=" + str(server_id))

    # def deleteProject(self, project_id):
    #     # Just hide, not really delete
    #     return self.update("UPDATE Server SET deleted=1 WHERE id=" + str(server_id))

# a = mysql()
# a.deleteServer(36)

# a = mysql()
# print(a.getAllRepo())

# a = mysql()
# print(
# a.addServer({
# "name": "master-server66666666",
# "ip": "45.77.110.160",
# "user": "root",
# "password": "Uq*1R1,_QFLXB(=L",
# "path": "master-pro",
# "deploy_path": "API",
# "branch": "master"
# },
# 6))

# print(a.getAllRepo())
# print(a.addServer({'name': '123'}, 'khalilleo/augustctl'))
