#!/usr/bin/python
from bottle import route, run, static_file, template
import socket

@route('/asset/js/<filename>')
def js_file(filename):
    return static_file(filename, root='./asset/js/')

@route('/asset/css/<filename>')
def css_files(filename):
    return static_file(filename, root='./asset/css/')

@route('/data/<filename>')
def data_files(filename):
    return static_file(filename, root='./data/')

@route('/')
def index():
    return template('index.html')

def getLocalIp():
    '''Get the local ip'''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def start():
    run(host=getLocalIp(), port=80)

if __name__ == '__main__':
    start()