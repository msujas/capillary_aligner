import socket
import numpy as np
import logging
import types, selectors
from selectors import SelectorKey, DefaultSelector
from _typeshed import FileDescriptorLike
import os, pathlib

logger = logging.getLogger()
PORT = 50015
home = pathlib.Path.home()
logfile = f'{home}/microscopeserverlog/server.log'
os.makedirs(os.path.dirname(logfile),exist_ok=True)

class ImageServer():
    def __init__(self,acceptedhosts:list, host, port = PORT):
        self.acceptedhosts=acceptedhosts
        self.host=host
        self.port = port
        self.image:bytes=None
    def accept_wrapper(self,sock:FileDescriptorLike,sel:DefaultSelector):
        conn,addr =sock.accept()
        conn.setblocking(False)
        print(f'Accepted connection from {addr}',plevel=1)
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
            print(f'closing connection to {data.addr}', plevel=1)
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
            try:
                recvData = sock.recv(1024)
                
            except (ConnectionAbortedError, ConnectionResetError):
                
                print(connectionLostMessage)
                #logger.info(connectionLostMessage)
                recvData = b''
            if recvData:
                print(recvData,plevel=1)
                data.outb += recvData
                strmessage = data.outb.decode()
                try:
                    address = int(strmessage.split(';')[0])
                    #bytemessage += bytes(fullmessage,encoding='utf-8')
                except (ValueError, KeyError):
                    bytemessage = b'invalid message!'
                except ConnectionResetError:
                    print(f'connection lost with client: {data.addr}')
                    bytemessage = b''
                    closeConnection()
            else:
                #logger.debug(f'no data received from {data.addr}')
                closeConnection()
        if mask & selectors.EVENT_WRITE:

            if bytemessage:
                print(f'sending data to {data.addr}', plevel=1)
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
        if self.debug:
            loglevel = logging.DEBUG
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

    def decodeimage(self,imagestring:bytes):
        stringsplit = imagestring.split(b';')
        d1s = stringsplit[0].decode()
        d2s = stringsplit[1].decode()
        d3s = stringsplit[2].decode()
        d1 = int(d1s.split('_')[1])
        d2 = int(d2s.split('_')[1])
        d3 = int(d3s.split('_')[1])
        image = np.frombuffer(stringsplit[-1],dtype=np.uint8)
        image = image.reshape(d1,d2,d3)
        return image