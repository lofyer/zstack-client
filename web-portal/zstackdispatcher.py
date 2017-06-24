#!/usr/local/bin/python2
# -*- coding: UTF-8 -*-
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
        self.adminpassword = self.config.get('ZStack', 'AdminPassword')
        self.zstackip = None

    def login(self, username, password, zstackip):
        global adminSession
        try:
            self.zstackip = zstackip
            zssdk.configure(hostname=zstackip, port=8080, polling_interval=0.1, read_timeout=5)
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
        action = zssdk.QueryAccountAction()
        action.sessionId = adminSession.value.inventory.uuid
        action.conditions = ["name={0}".format(username)]
        res = action.call()
        if res.value.inventories == []:
            return False
        userid = res.value.inventories[0].uuid
        print "User ID"
        print userid

        action = zssdk.QueryAccountResourceRefAction()
        action.sessionId = adminSession.value.inventory.uuid
        action.conditions = ["accountUuid={0}".format(userid), "resourceType=VmInstanceVO"]
        res = action.call()
        vms = res.value.inventories

        if vms == None:
            return False

        vmList = []

        for vm in vms:
            action = zssdk.QueryVmInstanceAction()
            action.sessionId = adminSession.value.inventory.uuid
            action.conditions = ["uuid={0}".format(vm.resourceUuid)]
            action.fields = ["uuid", "name", "state", "type"]
            print "NOT SUPPORT CHINESE VM NAME:"
            res = action.call()
            print "BBBBBBBBBBBBBBBBBBBBBBBBBBBB"
            if res.value.inventories[0].type != "UserVm":
                continue
            vmInfo = {}
            vmInfo["uuid"] = res.value.inventories[0].uuid
            vmInfo["name"] = res.value.inventories[0].name
            vmInfo["state"] = res.value.inventories[0].state
            vmInfo["console"] = self.getConsoleById(res.value.inventories[0].uuid)
            vmList.append(vmInfo)

        return vmList

    def getConsoleById(self, vmid):
        global adminSession
        action = zssdk.GetVmConsoleAddressAction()
        action.sessionId = adminSession.value.inventory.uuid
        action.uuid = vmid
        res = action.call()
        vmInfo = {}
        try:
            res.value.success
            vmInfo["hostIp"] = res.value.hostIp
            vmInfo["port"] = res.value.port
            vmInfo["protocol"] = res.value.protocol
            return vmInfo
        except:
            vmInfo["hostIp"] = None
            vmInfo["port"] = None
            vmInfo["protocol"] = None
            return vmInfo

    def startVm(self, vmid):
        global adminSession
        sessionId = adminSession.value.inventory.uuid
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        session_auth = 'OAuth {0}'.format(sessionId)
        headers['Authorization'] = session_auth
        try:
            url = "http://" + self.zstackip + ":8080/zstack/v1/vm-instances/" + vmid + "/actions"
            r = requests.put(url, json={"startVmInstance":{}}, headers=headers)
        except Exception as e:
            print e
            return False
        return True

    def stopVm(self, vmid):
        sessionId = adminSession.value.inventory.uuid
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        session_auth = 'OAuth {0}'.format(sessionId)
        headers['Authorization'] = session_auth
        try:
            url = "http://" + self.zstackip + ":8080/zstack/v1/vm-instances/" + vmid + "/actions"
            r = requests.put(url, json={"stopVmInstance":{}}, headers=headers)
        except Exception as e:
            print e
            return False
        return True

    def genConsolevv(self, vmid):
        global adminSession
        try:
            vmInfo = self.getConsoleById(vmid)
            vvFile = '''[virt-viewer]
type=spice
host={0}
port={1}
#password=KGdMzrGwSpXr
delete-this-file=1
fullscreen=1
title=zstack-vdi
toggle-fullscreen=shift+f11
release-cursor=shift+f12
secure-attention=ctrl+alt+end
enable-smartcard=1
enable-usb-autoshare=1
usb-filter=-1,-1,-1,-1,0'''.format(vmInfo["hostIp"],vmInfo["port"])
            return vvFile
        except Exception as e:
            return e

    def genRdp(self, vmid):
        global adminSession
        try:
            vmInfo = self.getConsoleById(vmid)
            rdpFile = '''screen mode id:i:2
use multimon:i:0
desktopwidth:i:800
desktopheight:i:600
session bpp:i:32
winposstr:s:0,3,0,0,800,600
compression:i:1
keyboardhook:i:2
audiocapturemode:i:0
videoplaybackmode:i:1
connection type:i:7
networkautodetect:i:1
bandwidthautodetect:i:1
displayconnectionbar:i:1
username:s:
enableworkspacereconnect:i:0
disable wallpaper:i:0
allow font smoothing:i:0
allow desktop composition:i:0
disable full window drag:i:1
disable menu anims:i:1
disable themes:i:0
disable cursor setting:i:0
bitmapcachepersistenable:i:1
full address:s:192.168.0.200
audiomode:i:0
redirectprinters:i:1
redirectcomports:i:1
redirectsmartcards:i:1
redirectclipboard:i:1
redirectposdevices:i:1
autoreconnection enabled:i:1
authentication level:i:2
prompt for credentials:i:0
negotiate security layer:i:1
remoteapplicationmode:i:0
alternate shell:s:
shell working directory:s:
gatewayhostname:s:
gatewayusagemethod:i:4
gatewaycredentialssource:i:4
gatewayprofileusagemethod:i:0
promptcredentialonce:i:0
gatewaybrokeringtype:i:0
use redirection server name:i:0
rdgiskdcproxy:i:0
kdcproxyname:s:'''.format(vmIP)
            return rdpFile
        except Exception as e:
            return e

    def sessionId(self):
        global adminSession
        return adminSession.value.inventory.uuid

