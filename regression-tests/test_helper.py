from datetime import datetime
import os
import requests
import urlparse
import unittest
import json
from subprocess import call, check_output

DAEMON = os.environ.get('DAEMON', 'authoritative')


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        # TODO: config
        self.server_address = '127.0.0.1'
        self.server1_port = int(os.environ.get('WEBPORT', '8084'))
        self.server1_url = 'http://%s:%s/' % (self.server_address, self.server1_port)
        self.server2_port = 8085
        self.server2_url = 'http://%s:%s/' % (self.server_address, self.server2_port)
        self.session = requests.Session()
        self.session.auth = ('foo', os.environ.get('APIKEY', 'super'))
        #self.session.keep_alive = False
        #        self.session.headers = {'X-API-Key': os.environ.get('APIKEY', 'changeme-key'), 'Origin': 'http://%s:%s' % (self.server_address, self.server_port)}

    def writeFileToConsole(self, file):
        fp = open(file)
        cmds_nl = fp.read()
        # Lua doesn't need newlines and the console gets confused by them e.g.
        # function definitions
        cmds = cmds_nl.replace("\n", " ")
        return call(["../wforce", "-c", "./wforce1.conf", "-e", cmds])

    def writeCmdToConsole(self, cmd):
        return check_output(["../wforce", "-c", "./wforce1.conf", "-e", cmd])

    def writeFileToConsoleReplica(self, file):
        fp = open(file)
        cmds_nl = fp.read()
        # Lua doesn't need newlines and the console gets confused by them e.g.
        # function definitions
        cmds = cmds_nl.replace("\n", " ")
        return call(["../wforce", "-c", "./wforce2.conf", "-e", cmds])

    def writeCmdToConsoleReplica(self, cmd):
        return check_output(["../wforce", "-c", "./wforce2.conf", "-e", cmd])
    
    def allowFunc(self, login, remote, pwhash):
        return self.allowFuncAttrsInternal(login, remote, pwhash, {}, False)

    def allowFuncAttrs(self, login, remote, pwhash, attrs):
        return self.allowFuncAttrsInternal(login, remote, pwhash, attrs, False)

    def allowFuncReplica(self, login, remote, pwhash):
        return self.allowFuncAttrsInternal(login, remote, pwhash, {}, True)
    
    def allowFuncAttrsReplica(self, login, remote, pwhash, attrs):
        return self.allowFuncAttrsInternal(login, remote, pwhash, attrs, True)

    def allowFuncAttrsInternal(self, login, remote, pwhash, attrs, replica):
        payload = dict()
        payload['login'] = login
        payload['remote'] = remote
        payload['pwhash'] = pwhash
        payload['attrs'] = attrs
        if not replica:
            return self.session.post(
                self.url("/?command=allow"),
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})
        else:
            return self.session.post(
                self.url2("/?command=allow"),
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})

    def reportFunc(self, login, remote, pwhash, success):
        return self.reportFuncAttrsInternal(login, remote, pwhash, success, {}, False)

    def reportFuncReplica(self, login, remote, pwhash, success):
        return self.reportFuncAttrsInternal(login, remote, pwhash, success, {}, True)
    
    def reportFuncAttrs(self, login, remote, pwhash, success, attrs):
        return self.reportFuncAttrsInternal(login, remote, pwhash, success, attrs, False)

    def reportFuncAttrsReplica(self, login, remote, pwhash, success, attrs):
        return self.reportFuncAttrsInternal(login, remote, pwhash, success, attrs, True)

    def reportFuncAttrsInternal(self, login, remote, pwhash, success, attrs, replica):
        payload = dict()
        payload['login'] = login
        payload['remote'] = remote
        payload['pwhash'] = pwhash
        payload['success'] = success
        payload['attrs'] = attrs
        if not replica:
            return self.session.post(
                self.url("/?command=report"),
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})
        else:
            return self.session.post(
                self.url2("/?command=report"),
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})            

    def resetFunc(self, login, ip):
        return self.resetFuncInternal(login, ip, False)

    def resetFuncReplica(self, login, ip):
        return self.resetFuncInternal(login, ip, True)

    def resetFuncInternal(self, login, ip, replica):
        payload = dict()
        payload['login'] = login
        payload['ip'] = ip
        if not replica:
            return self.session.post(
                self.url("/?command=reset"),
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})
        else:
            return self.session.post(
                self.url2("/?command=reset"),
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'})
            

    def pingFunc(self):
        return self.session.get(self.url("/?command=ping"))

    def getBLFunc(self):
        return self.session.get(self.url("/?command=getBL"))

    def getBLFuncReplica(self):
        return self.session.get(self.url2("/?command=getBL"))
    
    def getDBStatsIPLogin(self, ip, login):
        payload = dict()
        payload['login'] = login
        payload['ip'] = ip
        return self.session.post(
            self.url("/?command=getDBStats"),
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}) 

    def getDBStatsIP(self, ip):
        payload = dict()
        payload['ip'] = ip
        return self.session.post(
            self.url("/?command=getDBStats"),
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}) 

    def getDBStatsLogin(self, login):
        payload = dict()
        payload['login'] = login
        return self.session.post(
            self.url("/?command=getDBStats"),
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}) 
    
    def url(self, relative_url):
        return urlparse.urljoin(self.server1_url, relative_url)

    def url2(self, relative_url):
        return urlparse.urljoin(self.server2_url, relative_url)
    
    def assert_success_json(self, result):
        try:
            result.raise_for_status()
        except:
            print result.content
            raise
        self.assertEquals(result.headers['Content-Type'], 'application/json')
