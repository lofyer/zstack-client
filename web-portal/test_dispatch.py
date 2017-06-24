#!/usr/local/bin/python2
# -*- coding: UTF-8 -*-
import zstackdispatcher

a=zstackdispatcher.zstackdispatcher()
print("=====================LOGIN")
print a.login("admin", "password", "172.20.1.40")
print("=====================GET SESSION ID")
print a.sessionId()
print("=====================GET USER VM")
print a.getUserVms("admin")
print("=====================START VM")
print a.startVm("16a1c1881dec47f3957edb7c8ce67459")
print("=====================GET CONSOLE")
print a.getConsoleById("16a1c1881dec47f3957edb7c8ce67459")
print("=====================GEN CONSOLE VV")
print a.genConsolevv("16a1c1881dec47f3957edb7c8ce67459")
