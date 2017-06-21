import ConfigParser
import hashlib
import json
import requests
import zssdk

cur_session = None

class OVirtDispatcher(object):

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read('zstack.conf')
        self.baseUrl = self.config.get('ZStack', 'ManagerIP')
        self.password = self.config.get('ZStack', 'AdminPassword')

    def login(self):
        global cur_session
        try:
            zssdk.configure(hostname=self.managerip, port=8080, polling_interval=0.1)

            login_action= zssdk.LogInByAccountAction()
            login_action.accountName = 'admin'
            login_action.password = hashlib.sha512(self.password).hexdigest()
            cur_session = login_action.call()

        except exception as conErr:
            return False, "Bad connection."
        return True, ''

    def getUserVms(self):
        global cur_session
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        session_auth = 'OAuth {0}'.format(cur_session)
        headers['Authorization'] = session_auth
        url = self.baseUrl + "/zstack/v1/vm-instances?type=UserVm"
        r = requests.get(url, headers=headers)
        vms = json.loads(r.content)
        
        return vms

    def getVmById(self, id):
        global cur_session
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        session_auth = 'OAuth {0}'.format(cur_session)
        headers['Authorization'] = session_auth
        url = self.baseUrl + "/zstack/v1/vm-instances/" + id + "/"
        r = requests.get(url, headers=headers)
        vm = json.loads(r.content)
        return api.vms.get(id)

    def startVm(self, vmid):
        global cur_session
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        session_auth = 'OAuth {0}'.format(cur_session)
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
        global cur_session
