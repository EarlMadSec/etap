import os
import json

from flask import Flask, request
import logging
import requests

import sys
sys.path.insert(0, '/home/ychen459/etaplib')
tap_address = 'http://127.0.0.1:5001'

import trigger

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


trigger.init()


# Additional API to receive circuit encoding info from client
@app.route('/add', methods=['POST'])
def add():
    trigger_id = int(request.files.get('id').read())
    secret_key = request.files.get('secret_key').read()

    formatter = request.files.get('formatter').read().decode()

    trigger.add_new_secret(trigger_id, secret_key, formatter)

    return 'success'



@app.route('/trigger', methods=['POST'])
def trigger_func():
    data = json.loads(request.data)

    trigger_id = data['id']

    trigger_data = data['data']

    trigger_payload = None

    circuit_id, X, ct = trigger.encode(trigger_id, trigger_data, trigger_payload)

    #  send trigger data to tap
    requests.request("POST",
                     f'{tap_address}/run',
                     files={
                         "trigger_id": trigger_id,
                         "circuit_id": circuit_id,
                         "j": circuit_id.to_bytes(4, byteorder='big'),
                         "X": X,
                         "ct": ct
                     })

    return app.make_response('success')
