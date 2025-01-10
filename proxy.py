"""
Proxy for the Ollama API on localhost.
Author: toutjavascript.com
Created: 2025-01
"""
import requests
import os
import multiprocessing
from flask_cors import CORS
import src.pytherminal as pytherminal
import src.device    as device
import src.utils     as utils
from flask import Flask, render_template, request, send_from_directory, Response, stream_with_context

# Constants to identify version and execution modalities
OLLAMA_PROXY_RELEASE="0.0.1"
OLLAMA_MIN_RELEASE="0.5.0"

class InfollamaProxy:
    def __init__(self, port=11430, base_url="http://localhost:11434/"):
        self.port = port
        base_url=base_url.rstrip('/').rstrip('/')
        if (base_url.startswith("http://") or base_url.startswith("https://")):
            self.base_url = base_url
        else:
            self.base_url = "http://" + base_url            
        self.ollama_base_url=base_url

    def __getattr__(self, name):
        if hasattr(InfollamaProxy, name):
            return getattr(InfollamaProxy, name)
        raise AttributeError(f"'{name}' not found in InfollamaProxy")

    def __str__(self):
        return f"InfollamaProxy(port={self.port}, base_url={self.base_url})"

    def create_url(self, endpoint: str):
        """Create a URL for the Ollama API, with base_url and endpoint"""
        if (endpoint.startswith("/")):
            endpoint = endpoint[1:]
        return f"{self.ollama_base_url}/{endpoint}"
    
    def get(self, endpoint, **kwargs):
        url = self.create_url(endpoint)
        print(url)
        try:
            response = requests.get(url, params=kwargs)
        except Exception as e:
            print(e);
        return response.json()      
    
    def post(self, endpoint, data=None, **kwargs):
        url = self.create_url(endpoint)        
        response = requests.post(url, json=data, params=kwargs)
        # Check if the response is streamed
        #print("data", data)
        if data["stream"]==True:
            print("Streaming data")
            for chunk in response.iter_content(chunk_size=1024): 
                stream_Data=chunk.decode('utf-8')   # Get each chunk of data
                return Response(stream_Data, mimetype='text/event-stream')
        else:
            return response.json()
    def put(self, endpoint, data=None, **kwargs):
        url = self.create_url(endpoint)
        response = requests.put(url, json=data, params=kwargs)
        return response.json()  
    def delete(self, endpoint, **kwargs):
        url = self.create_url(endpoint)        
        response = requests.delete(url, params=kwargs)
        return response.json()


    def check_connection(self):
        """
        Trying to connect to ollama server and checking if it's running."""
        try:
            response=requests.get(f"{self.ollama_base_url}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Connection failed: {e}")
            return False
        


if __name__ == "__main__":
    multiprocessing.freeze_support()

    tjs_host="localhost"
    tjs_port=11430
    cors_policy="*"

    proxy = InfollamaProxy()
    response = proxy.check_connection()
    print(response)
    response = proxy.get("api/version")
    print("proxy", proxy)
    print(response)

    print(device.getDeviceInfo())  
    
    appPath=utils.getAppPath()
    app = Flask(__name__)
    if cors_policy == "*":
        CORS(app)  # Enable CORS for all routes

    @app.route('/')
    def home():
        return render_template('index.html', release=OLLAMA_PROXY_RELEASE)

    @app.route('/favicon.png', methods=['GET'])
    def serveFavicon():
        return send_from_directory(os.path.join(appPath, 'static/picto'), 'favicon.png', mimetype='image/vnd.microsoft.icon')

    @app.route('/robots.txt', methods=['GET'])
    def serveRobots():
        return "deny: all"


    def stream_request(method, url, **kwargs):
        with requests.request(method, url, stream=True, **kwargs) as r:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

    # Serve all the other endpoints with flask
    @app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
    def catch_all(path):
        if request.method == 'GET':
            return proxy.get(path, **request.args)
        elif request.method == 'POST':
            # print("Method POST received", "path: ", path, "json: ", request.json)
            #return proxy.post(path, request.json, **request.args)
            url=proxy.create_url(path)
            print(url)
            return Response(stream_with_context(stream_request('POST', url, json=request.json, params=request.args)), content_type=request.headers.get('Content-Type'))
    
        elif request.method == 'OPTIONS':
            # Handle CORS preflight requests
            return '', 204 
        else:
            return "Method not allowed", 405


    app.run(host=tjs_host, port=tjs_port)