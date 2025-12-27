import os
import random
import string

from Crypto.Cipher import AES
from flask import Flask, request, jsonify
from Crypto.Util.Padding import pad, unpad


app = Flask(__name__)

BLOCK_SIZE = 16
KEY = os.urandom(BLOCK_SIZE)  # AES-128 key


def get_random_message(length: int = None) -> str:
    if length is None:
        length = random.randint(4, 15)

    alphabet = string.ascii_letters + string.digits + string.punctuation + ' '
    message = ''.join(random.choice(alphabet) for _ in range(length))
    return message


@app.route('/get-message', methods=['GET'])
def get_message():
    message_length = request.args.get("length", default=None, type=int)
    message = get_random_message(message_length)

    iv = os.urandom(BLOCK_SIZE)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    padded_message = pad(message.encode(), BLOCK_SIZE)
    ciphertext = cipher.encrypt(padded_message)

    return jsonify({
        'iv': iv.hex(),
        'ciphertext': ciphertext.hex()
    })


@app.route('/check-padding', methods=['POST'])
def check_padding():
    data = request.get_json()
    iv = bytes.fromhex(data['iv'])
    ciphertext = bytes.fromhex(data['ciphertext'])

    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    try:
        decrypted = cipher.decrypt(ciphertext)
    except ValueError:
        return jsonify({
            'ok': False,
            'error': 'Decryption error'
        })

    try:
        unpad(decrypted, BLOCK_SIZE)
    except ValueError:
        return jsonify({
            'ok': False,
            'error': 'Invalid padding'
        })
    
    return jsonify({
        'ok': True
    })


@app.route('/check-message', methods=['POST'])
def check_message():
    data = request.get_json()
    iv = bytes.fromhex(data['iv'])
    ciphertext = bytes.fromhex(data['ciphertext'])
    message = data['message']

    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    try:
        decrypted = cipher.decrypt(ciphertext)
        unpadded = unpad(decrypted, BLOCK_SIZE)
    except ValueError:
        return jsonify({
            'ok': False,
            'error': 'Decryption or padding error'
        })

    if unpadded.decode('utf-8', errors='ignore') == message:
        return jsonify({'ok': True})
    else:
        return jsonify({'ok': False, 'error': 'Message does not match'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5834)
