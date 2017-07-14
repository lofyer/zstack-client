#!/usr/local/bin/python2
# -*- coding: UTF-8 -*-
import zstackdispatcher
from flask import Flask, session, redirect, url_for, escape, request, make_response

app = Flask(__name__)

dispatcher = None

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        session['zstackip'] = request.form['zstackip']
        return redirect(url_for('verification'))
    return '''<html><body align="center">
        Login Required.
        <form method="post">
            <p>Username: <input type=text name=username>
            <p>Password: <input type=password name=password>
            <p>ZStack IP: <input type=text name=zstackip>
            <p><input type=submit value=Login>
        </form></body><html>
    '''

@app.route('/verification')
def verification():
    global dispatcher
    dispatcher = zstackdispatcher.zstackdispatcher()
    loggedin, message = dispatcher.login(session["username"], session["password"], session["zstackip"])
    if loggedin:
        return redirect(url_for('vms'))
    return redirect(url_for('login'))

@app.route('/vms')
def vms():
    global dispatcher
    if dispatcher == None:
        return redirect(url_for('login'))
    if 'username' in session:
        form = '''
            <html>
            <head>
             <meta http-equiv="refresh" content="10" />
        '''
        form = form + '''
            </head>
            <body>
            <center><br/><br/>
            <table cellpadding="5" style='border-width: 1px; border-spacing: 2px; border-style: outset; border-color: gray; border-collapse: separate; background-color: white;'>
            Login as {0}
            <tr>
                <th>VM Name</th>
                <th>Status</th>
                <th>Display</th>
                <th>Start</th>
                <th>Stop</th>
                <th>Console</th>
                <th>RDP</th>
            </tr>
        '''.format(escape(session['username']))
        if dispatcher.getUserVms(escape(session['username'])) == False:
            return form
        for vm in dispatcher.getUserVms(escape(session['username'])):
            startbtn = "<button onclick=javascript:location.href='action?vmid=%s&action=start' type='button'>Start</button>" % (vm["uuid"])
            stopbtn = "<button onclick=javascript:location.href='action?vmid=%s&action=stop' type='button'>Stop</button>" % (vm["uuid"])
            connectbtn = "<button onclick=javascript:location.href='action?vmid=%s&action=consolevv' type='button'>Console</button>" % (vm["uuid"])
            rdpbtn = "<button onclick=javascript:location.href='action?vmid=%s&action=rdp' type='button'>Remote Desktop</button>" % (vm["uuid"])

            form = form + '''       <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
        </tr> ''' % (vm["name"], vm["state"], vm["console"]["protocol"], startbtn if vm["state"] != "Running" else None, stopbtn if vm["state"] == "Running" else None, connectbtn if vm["state"] == "Running" else None, rdpbtn if vm["state"] == "Running" else None)

        form = form + '''
            <tr>
                <td><button onclick=javascript:location.href='/'>Logout</button></td>
                <td><button onclick=javascript:location.href='/vms'>Refresh</button></td>
            </tr>
        </table></center></body></html>'''
        return form
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/action')
def action():
    global dispatcher
    if dispatcher == None:
        return redirect(url_for('login'))

    vmid = request.args.get('vmid')
    action = request.args.get('action')

    if action == "start":
        dispatcher.startVm(vmid)
    elif action == "stop":
        dispatcher.stopVm(vmid)
    elif action == "consolevv":
        vvFile = dispatcher.genConsolevv(vmid)
        response = make_response(vvFile)
        #response.headers["Content-Type"] = "Application/octet-stream"
        response.headers["X-Application-Context"] = "application:development:9000"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, DELETE"
        response.headers["Access-Control-Max-Age"] = "3600"
        response.headers["Content-Type"] = "Application/x-vv;charset=ISO-8859-1"
        response.headers["Content-Disposition"] = "attachment; filename=console.vv"
        return response
    elif action == "rdp":
        rdpFile = dispatcher.genRdp(vmid)
        response = make_response(rdpFile)
        response.headers["Content-Type"] = "Application/x-rdp"
        response.headers["Content-Disposition"] = "attachment; filename=Default.rdp"
        return response

    return redirect(url_for('vms'))

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='0.0.0.0', port=8888, debug = True)
