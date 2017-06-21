import ConfigParser
import hashlib
import json
import requests
import zssdk

adminSession = None

class zstackdispatcher(object):

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('zstack.conf')
        self.managerip= self.config.get('ZStack', 'ManagerIP')
        self.adminpassword = self.config.get('ZStack', 'AdminPassword')

    def login(self, username, password):
        global adminSession
        try:
            zssdk.configure(hostname=self.managerip, port=8080, polling_interval=0.1)
            loginAction= zssdk.LogInByAccountAction()
            loginAction.accountName = username
            loginAction.password = hashlib.sha512(password).hexdigest()
            userSession = loginAction.call()
            if userSession.error:
                return False, userSession.error.details

            loginAction= zssdk.LogInByAccountAction()
            loginAction.accountName = 'admin'
            loginAction.password = hashlib.sha512(self.adminpassword).hexdigest()
            adminSession = loginAction.call()
            if adminSession.error:
                return False, userSession.error.details

        except Exception as conErr:
            return False, conErr
        return True, ''

    def getUserVms(self, username):
        global adminSession
        action = zssdk.QueryVmInstanceAction()
        action.sessionId = adminSession.value.inventory.uuid
        action.conditions = ["type=UserVm"]
        res = action.call()
        
        return vms

    def getVmById(self, id):
        global adminSession
        action = zssdk.QueryVmInstanceAction()
        action.sessionId = adminSession.value.inventory.uuid
        action.conditions = ["uuid={0}".format(id)]
        

        return api.vms.get(id)

    def startVm(self, vmid):
        global adminSession
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        session_auth = 'OAuth {0}'.format(adminSession)
        headers['Authorization'] = session_auth
        try:
            url = self.baseUrl + "/zstack/v1/vm-instances/" + id + "action"
            r = requests.put(url, json={"startVmInstance":{}}, headers=headers)
        except RequestError as reqErr:
            return False, reqErr.reason, reqErr.detail
        except ConnectionError as conErr:
            return False, 'Connection Error'
        return True, None, None

    def stopVm(self, vmid):
        global api
        try:
            api.vms.get(id=vmid).stop()
        except RequestError as reqErr:
            return False, reqErr.reason, reqErr.detail
        except ConnectionError as conErr:
            return False, 'Connection Error'
        return True, None, None

    def ticketVm(self, vmid):
        global api
        try:
            ticket = api.vms.get(id=vmid).ticket()
            return ticket.get_ticket().get_value(), ticket.get_ticket().get_expiry()
        except RequestError as reqErr:
            raise Exception(reqErr.reason, reqErr.detail)
        except ConnectionError as conErr:
            raise Exception('Connection Error', '')

    def consolevv(self, vmid):
        global adminSession
