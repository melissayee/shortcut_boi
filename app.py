import hashlib
import hmac
import os
import time

from flask import Flask, request, jsonify

from messages import build_single_shortcut_response
from models import System
from shortcuts import get_random_shortcut

app = Flask(__name__)

SIGNING_SECRET = os.environ.get('SIGNING_SECRET')


def is_valid_request(request_body: str, timestamp: str, slack_signature: str) -> bool:
    # Confirm that message was sent within last 5 minutes
    if abs(time.time() - float(timestamp)) > 60 * 5:
        return False
    request_signature = f'v0:{timestamp}:{request_body}'
    server_signature = 'v0=' + hmac.new(bytes(SIGNING_SECRET, 'UTF-8'), request_signature.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(server_signature, slack_signature)


@app.route('/shortcut_help', methods=['POST'])
def get_help():
    if is_valid_request(request.get_data().decode('utf-8'), request.headers['X-Slack-Request-Timestamp'],
                        request.headers['X-Slack-Signature']):
        if request.method == 'POST':
            return jsonify(response_type='in_channel',
                           text='You can get help from me!')
    else:
        return jsonify(response_type='in_channel',
                       text='Invalid Signature')


@app.route('/shortcut_random', methods=['POST'])
def get_random():
    if is_valid_request(request.get_data().decode('utf-8'), request.headers['X-Slack-Request-Timestamp'],
                        request.headers['X-Slack-Signature']):
        if request.method == 'POST':
            request_params = request.form['text']
            if request_params == '':
                return jsonify(response_type='in_channel',
                               text='You need to specify which system you want a shortcut for')
            else:
                if request_params.lower() in ['mac', 'macos', 'm', 'apple']:
                    system = System(0)
                elif request_params.lower() in ['win', 'windows', 'w', 'microsoft']:
                    system = System(1)
                elif request_params.lower() in ['h', 'help']:
                    return jsonify(response_type='in_channel',
                                   text='You can use /shortcut_random [system]. The current systems available are '
                                        'mac, win')
                else:
                    return jsonify(response_type='in_channel',
                                   text="Sorry! That's not a valid system. Please select from one of: mac, win or use "
                                        "help")
                shortcut = get_random_shortcut(system)
                response_blocks = build_single_shortcut_response(shortcut)
                return jsonify(response_type='in_channel',
                               blocks=response_blocks)
        else:
            return jsonify(response_type='in_channel',
                           text='Invalid Signature')


if __name__ == '__main__':
    app.run()
