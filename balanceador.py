import requests as req
import os
from flask import Flask, request, render_template, send_from_directory, jsonify, make_response, Response
import sys
from threading import Thread
import time

peers = []
all_peers = []

def create_app(config=None):
    app = Flask(__name__, static_folder=None, static_url_path='/none')
    peers.append(os.environ.get("PEER_A"))
    peers.append(os.environ.get("PEER_A_LINE"))
    all_peers.append(os.environ.get("PEER_A"))
    all_peers.append(os.environ.get("PEER_A_LINE"))
    print(peers)

    heart_beater_worker = Thread(target=heart_beater)
    heart_beater_worker.start()

    app.config.update(dict(DEBUG=True))
    app.config.update(config or {})

    @app.route('/', defaults={'path': ''}, methods=["GET", "POST"])
    @app.route('/<path>', methods=["GET", "POST"])
    def proxy(path):
        backend = hash((request.environ['REMOTE_ADDR'], request.environ['REMOTE_PORT'])) % len(peers)
        res = req.request(
        method          = request.method,
        url             = request.url.replace(request.host_url, f'http://{peers[backend]}/'),
        headers         = {k:v for k,v in request.headers if k.lower() != 'host'},
        data            = request.get_data(),
        cookies         = request.cookies,
        allow_redirects = False,
    )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers          = [
            (k,v) for k,v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        ]
        response = Response(res.content, res.status_code, headers)
        return response
    
    @app.route('/pub/<path>', methods=["GET", "POST"])
    def proxy_css(path):
        backend = hash((request.environ['REMOTE_ADDR'], request.environ['REMOTE_PORT'])) % len(peers)  
        res = req.request(
        method          = request.method,
        url             = request.url.replace(request.host_url, f'http://{peers[backend]}/'),
        headers         = {k:v for k,v in request.headers if k.lower() != 'host'},
        data            = request.get_data(),
        cookies         = request.cookies,
        allow_redirects = False,
    )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers          = [
            (k,v) for k,v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        ]
        response = Response(res.content, res.status_code, headers)
        return response

    return app

def heart_beater():
    while True:
        for service in all_peers:
            try:
                resp = req.get(f"http://{service}/check_alive",timeout=0.1)
                if service not in peers:
                    peers.append(service)
            except Exception:
                if service in peers:
                    peers.remove(service)
                print(f"{service} is dead! Removing from peer list..")
        time.sleep(5)

if __name__ == "__main__":
    port = 80
    app = create_app()
    app.run(host="0.0.0.0", port=port)