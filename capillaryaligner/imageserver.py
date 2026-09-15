import socket
import logging
import types, selectors
from selectors import SelectorKey, DefaultSelector
import os, pathlib
import argparse

logger = logging.getLogger()
PORT = 50015
home = pathlib.Path.home()
logfile = f'{home}/microscopeserverlog/server.log'
os.makedirs(os.path.dirname(logfile),exist_ok=True)

def getargs():
    ap = argparse.ArgumentParser()
    ap.add_argument('host', type=str,help='host to run server on (default: localhost)', default='localhost', nargs='?')
    ap.add_argument('-p','--port', type = int, default=PORT, help=f'server port number (default: {PORT})')
    ap.add_argument('-ah','--acceptedhosts', type=str, default=None,help='comma separated list of accepted hosts')
    args = ap.parse_args()
    ah:str = args.acceptedhosts
    if ah:
        ah = ah.split(',')
    return args.host, args.port, ah

class ImageServer():
    def __init__(self, host, port,acceptedhosts:list):
        self.acceptedhosts=acceptedhosts
        self.host=host
        self.port = port
        self.image:bytes=None
    def accept_wrapper(self,sock,sel:DefaultSelector):
        conn,addr =sock.accept()
        conn.setblocking(False)
        print(f'Accepted connection from {addr}')
        data = types.SimpleNamespace(addr=addr,inb = b'',outb = b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn,events,data=data)

    def service_connection(self,key:SelectorKey,mask:int,sel:DefaultSelector):
        sock = key.fileobj
        data = key.data
        #logger.debug(f'accepted connection from {data.addr}')
        connectionLostMessage = f'connection lost with client: {data.addr}'
        bytemessage = b''
        def closeConnection():
            print(f'closing connection to {data.addr}')
            sel.unregister(sock)
            sock.close()
        if self.acceptedhosts:
            acceptedIPs = [socket.gethostbyname(h) for h in self.acceptedhosts]
            hostName = data.addr[0]
            if hostName not in self.acceptedhosts and hostName not in acceptedIPs:
                print('host name not in accepted hosts')
                closeConnection()
                return
        if mask & selectors.EVENT_READ:
            while True:
                try:
                    recvData = sock.recv(1024)
                    
                except (ConnectionAbortedError, ConnectionResetError):
                    
                    print(connectionLostMessage)
                    #logger.info(connectionLostMessage)
                    recvData = b''
                if recvData:
                    print(recvData)
                    data.outb += recvData
                    try:
                        if data.outb.startswith(b'request'):
                            bytemessage = self.image
                            break
                        elif data.outb.startswith(b'send') and data.outb.endswith(b'!'):
                            self.image = data.outb
                            bytemessage = b'received!'
                            break
                    except (ValueError, KeyError):
                        bytemessage = b'invalid message!'
                    except ConnectionResetError:
                        print(f'connection lost with client: {data.addr}')
                        bytemessage = b''
                        closeConnection()
                        break
                else:
                    logger.debug(f'no data received from {data.addr}')
                    closeConnection()
                    break
        if mask & selectors.EVENT_WRITE:

            if bytemessage:
                print(f'sending data to {data.addr}')
                try:
                    sent = sock.send(bytemessage)
                    bytemessage = bytemessage[sent:]
                    #logger.debug(f'data sent to {data.addr}')
                except ConnectionResetError:
                    print(connectionLostMessage)
                    #logger.info(connectionLostMessage)
                    bytemessage = b''
                    closeConnection()

    def multiServer(self):
        
        loglevel = logging.INFO

        logging.basicConfig(filename=logfile, level = loglevel, format = '%(asctime)s %(levelname)-8s %(message)s',
                            datefmt = '%Y/%m/%d_%H:%M:%S')
        logger.info('server started')
        
        allhosts = []
        if not self.acceptedhosts:
            ahstring = 'all'
        else:
            ahstring = ','.join(self.acceptedhosts)
        print(f'accepted hosts: {ahstring}')

        sel = selectors.DefaultSelector()
        print('running multiServer')
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        s.settimeout(5)
        #s.setblocking(False)
        sel.register(s,selectors.EVENT_READ,data=None)

        try:
            while True:
                events = sel.select(timeout=5)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj,sel)
                    else:
                        hostname = socket.gethostbyaddr(key.data.addr[0])
                        if not hostname in allhosts:
                            allhosts.append(hostname)
                            logger.info(f'new client {hostname}')
                            print(f'connection from {hostname}')
                        self.service_connection(key, mask,sel)
        except KeyboardInterrupt:
            logger.info('keyboard interupt')
            print("caught keyboard interrupt, exiting")
        except Exception as e:
            logger.exception(e)
            raise e
        finally:
            sel.close()


def startserver():
    host, port, ah = getargs()
    iserver = ImageServer(host,port,ah)
    iserver.multiServer()