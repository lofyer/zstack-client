import zssdk
import json

zssdk.configure(port=8989, polling_interval=0.1)

login = zssdk.LogInByAccountAction()
login.accountName = 'admin'
login.password = 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86'
r = login.call()

action = zssdk.CreateZoneAction()
action.sessionId = r.value.inventory.uuid
action.name = "zone"
action.description = "desc"
z = action.call()

q = zssdk.QueryZoneAction()
q.sessionId = r.value.inventory.uuid
q.conditions = ['uuid=%s' % z.value.inventory.uuid]
q.sortBy = 'name'
q.start = 0
q.limit = 100
q.fields = ['name']
q.call()

def func(res):
    print res

d = zssdk.DeleteZoneAction()
d.sessionId = r.value.inventory.uuid
d.uuid = z.value.inventory.uuid
d.call(func)

import time
time.sleep(2)
