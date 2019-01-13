import requests
import numpy as np
import time
import threading
import facerecogsub
import json
import os
import sys

def wsid(surl):
    started = False
    t1 = None
    ct = 0
    clientstat = 'new'
    # surl = '' # address of main server
    clientid = -1
    headers = {'Content-Type': 'application/json', 'accept': 'application/json'}
    while True:
        send_data = {'clientstat':clientstat, 'clientid':clientid}
        try:
            r = requests.post(url = surl+"/wsid", data = json.dumps(send_data), headers=headers) 
            data = r.json()
        except:
            r = requests.post(url = surl+"/wsid", data = json.dumps(send_data), headers = headers) 
            data = r.json()
        if clientid == -1:
            clientid = data['clientid']
        if data['wsid'] == 'start' and not started:
            print('starting sub processing')
            known_face_encodings = data['encodings']
            known_face_names = data['names']
            for i in range(len(known_face_encodings)):
                known_face_encodings[i]=np.array(known_face_encodings[i])
            
            started = True
            facerecogsub.stop = False
            clientstat = 'running'
            t1 = threading.Thread(target=facerecogsub.main, args=[ct, known_face_encodings, known_face_names])
            t1.start()
            ct += 1
            
        elif data['wsid'] == 'stop' and started:
            print('stopping sub processing')
            facerecogsub.stop = True
            t1.join()
            started = False
            clientstat = 'stopped'
        elif data['wsid'] == 'stop' and clientstat == 'new':
            started = False
            clientstat = 'stopped'
        time.sleep(2)
if __name__=='__main__':
    if not os.environ.get('MAIN_SERVER_IP') or not os.environ.get('CAMERA_LOCATION'):
        sys.exit('Error: Set both environment variables MAIN_SERVER_IP and CAMERA_LOCATION')
    wsid(os.environ.get('MAIN_SERVER_IP'))
