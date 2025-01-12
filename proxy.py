"""
Proxy for the Ollama API on localhost.
Author: toutjavascript.com
Created: 2025-01
"""
import requests
import os
import argparse
import multiprocessing
from flask_cors import CORS
import src.pytherminal as pytherminal
import src.device    as device
import src.utils     as utils
from rich.pretty import pprint

from flask import Flask, render_template, request, send_from_directory, Response, stream_with_context, abort

# Constants to identify version and execution modalities
OLLAMA_PROXY_RELEASE="0.0.1"
OLLAMA_MIN_RELEASE="0.5.0"

# List of endpoints that are allowed to be accessed by the user
user_allowed_endpoints= ["/api/tags",
                         "/api/show",
                         "/api/version",
                         "/api/ps", 
                         "/api/generate",
                         "/api/chat",
                         "/api/embed",
                         "/v1/chat/completions",
                         "/v1/completions",
                         "/v1/models",
                         "/v1/models/",
                         "/v1/embeddings",
                         "/info/api/"
                        ]
admin_allowed_endpoints=["/api/create", "/api/copy", "/api/delete", "/api/pull", "/api/push",
                         "/info/admin_api/"]

class InfollamaUser:
    def __init__(self, user_type: str, user_name: str, token: str):
        self.user_type=user_type
        self.user_name=user_name
        self.token=token
    def __str__(self):
        return f"User: {self.user_name}, Type: {self.user_type}"
       

class InfollamaProxy:
    def __init__(self, base_url, host, port, cors_policy, user_file, log_level="ALL"):
        base_url=base_url.rstrip('/').rstrip('/')
        if (base_url.startswith("http://") or base_url.startswith("https://")):
            self.base_url = base_url
        else:
            self.base_url = "http://" + base_url            
        self.ollama_base_url=base_url
        self.host=host
        self.port=port
        self.cors_policy=cors_policy
        self.server = Flask("infollama_proxy")
        self.ollama_version=None
        self.ollama_running=False
        self.env_vars=dict()
        self.user_file=user_file
        self.log_level=log_level
        self.users=[]
        self.get_ollama_env_var()
        if cors_policy == "*":
            CORS(self.server)  # Enable CORS for all origins
        else:
            if cors_policy != "":
                CORS(self.server, resources={"/": {"origins": self.cors_policy}})

    def __getattr__(self, name):
        if hasattr(InfollamaProxy, name):
            return getattr(InfollamaProxy, name)
        raise AttributeError(f"'{name}' not found in InfollamaProxy")

    def __str__(self):
        users = ", ".join([f"{user.user_name} is {user.user_type}" for user in self.users])
        return f"""InfollamaProxy(base_url={self.base_url}, 
        host={self.host}, 
        port={self.port}, 
        cors_policy={self.cors_policy}, 
        ollama_version={self.ollama_version}, 
        ollama_running={self.ollama_running}, 
        env_vars=[{self.env_vars}],
        users=[{users}]"""
    
    def log_event(self, event, log_level):
        """Log an event to the console"""
        print(f"Event logged: {event}")

    def load_user_file(self):
        """Load the user file from the self.user_file file formated as type_of_user:user_name:token
        typeof user can be admin or user
        user_name is a string with letters or numbers
        toke is a secret string starting with pro_ followed by a random text string of 10 characters
        Example: admin:john_doe:pro_1234567890
        users found are stored in self.users as a InfollamaUser object
        """
        try:
            # read the file line by line and create a list of InfollamaUser objects
            with open(self.user_file, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(':')
                    print(line, parts)
                    if len(parts) == 3 and parts[0] in ['admin', 'user']:
                        user_type, user_name, token = parts[0], parts[1], parts[2]
                        self.users.append(InfollamaUser(user_type=user_type, user_name=user_name, token=token))                        
        except FileNotFoundError:
            print(f"User file {self.user_file} not found. No user auth definition.")

    def get_user(self, token: str):
        """Return an InfollamaUser object based on the token"""
        for user in self.users:
            if user.token == token:
                return user
        return None

    def check_user(self, token: str, endpoint: str):
        """Check if the token is associated to a user who has access to the specified endpoint"""
        # Implement your logic here
        user=self.get_user(token)
        if user is not None:
            return False
        return True

    def get_ollama_env_var(self):
        """Get the Ollama environment variables from the system"""
        try:
            self.env_vars.clear()
            for key in ["OLLAMA_HOST", "OLLAMA_MODELS" ,"OLLAMA_MAX_LOADED_MODELS", "OLLAMA_NUM_PARALLEL", "OLLAMA_MAX_QUEUE", "OLLAMA_FLASH_ATTENTION", "OLLAMA_KV_CACHE_TYPE"]:
                self.env_vars[key]=os.getenv(key)
        except KeyError:
            pass

    def create_url(self, endpoint: str):
        """Create a URL for the Ollama API, with base_url and endpoint"""
        if (endpoint.startswith("/")):
            endpoint = endpoint[1:]
        return f"{self.ollama_base_url}/{endpoint}"
    
    def get(self, endpoint, **kwargs):
        url = self.create_url(endpoint)
        try:
            response = requests.get(url, params=kwargs)
            if (utils.is_json(response.text)):
                return response.json()      
            else:
                return response.text
        except Exception as e:
            pytherminal.console(f"[error]{e}[/error]");
            abort(500)
    
    def post(self, endpoint, data=None, **kwargs):
        url = self.create_url(endpoint)        
        response = requests.post(url, json=data, params=kwargs)
        if data["stream"]==True:
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


    # Check python version and venv
    def check_versions(self):
        pythonVersion=utils.getPythonVersion()
        OS=utils.getOS()
        pytherminal.console(" ", False)
        pytherminal.console(" You are running [b]Python V"+pythonVersion+"[/b] on [b]"+OS+"[/b]", False)
        if utils.in_venv():
            pytherminal.console(" [b] (virtual env) is activated[/b]", False)
        else:
            pytherminal.console(" [error] Carefull, (virtual env) is not activated. You may experience module version issues[/error]", False)


    def check_ollama_connection(self):
        """
        Trying to connect to ollama server and checking if it's running."""
        try:
            response=requests.get(f"{self.ollama_base_url}")
            self.ollama_running=True
            return True
        except requests.exceptions.RequestException as e:
            self.ollama_running=False
            return False
        
        
    def get_ollama_version(self):
        """ Trying to read the /api/version to ensure this is a real ollama server on base_url. """
        response=self.get("/api/version")
        try:
            self.ollama_version=response["version"]
            self.ollama_running=True
            return self.ollama_version
        except Exception as e:
            print(e)
            self.ollama_running=False
            self.ollama_version=None
            return None        


if __name__ == "__main__":
    multiprocessing.freeze_support()
   

    ########## CONFIGURATION #################################################################################################################
    tjs_host="localhost"                    # host of the proxy server
    tjs_port=11430                          # port of the proxy server
    cors_policy="*"                         # cors policy of the proxy server (* allows all origins, None fixes policy to same origin)
    base_url="http://localhost:11434/"      # base url of the ollama server
    user_file="users.conf"                  # path to the user file containing credentials
    log_level="INFO"                        # log level of the proxy server
    log_file="proxy.log"                    # path to the log file for the proxy server
    ##########################################################################################################################################

    # Reading the argument parameters
    parser = argparse.ArgumentParser(description='Run a proxy filtered server to forward API requests to Ollama')
    parser.add_argument('--host', type=str, default=tjs_host, help=f'The host name for the proxy server (default: {tjs_host})')
    parser.add_argument('--port', type=str, default=tjs_port, help=f'The port for the proxy server (default: {tjs_port})')
    args = parser.parse_args()

    proxy = InfollamaProxy(base_url=base_url, host=tjs_host, port=tjs_port, cors_policy=cors_policy, user_file=user_file )
    #print("proxy after init()", proxy)

    # Display on terminal the state of application.
    pytherminal.console("[reverse][h1]*******************    Ollama Localhost Proxy V "+OLLAMA_PROXY_RELEASE+" started    ******************[/h1][/reverse]", False)
    pytherminal.console("  [ok]Thanx for using. Please report issues and ideas on[/ok]", False)
    pytherminal.console("  [url]https://github.com/toutjavascript/ollama-localhost-proxy[/url]", False) 
    proxy.check_versions()
    #print("proxy after check_versions()", proxy)
    proxy.check_ollama_connection()
    #print("proxy after check_ollama_connection()", proxy)
    if proxy.ollama_running:
        proxy.get_ollama_version()
        if (proxy.ollama_version is not None):
            pytherminal.console(f"[green]Ollama [u]V {proxy.ollama_version}[/u] is running @[url]{proxy.ollama_base_url}[/url][/green]", False)
        else:
            pytherminal.console(f"[error]Are you sure Ollama is running @[url]{proxy.ollama_base_url}[/url][/error]", False)
    else:
        pytherminal.console(f"[error]Ollama not found or stopped @[url]{proxy.ollama_base_url}[/url][/error]", False)


    #pprint(device.get_device_info())  

    proxy.load_user_file()
    print(proxy)  
    
    appPath=utils.getAppPath()
    # Prevent http flask web server logging in terminal 
    #log = logging.getLogger('werkzeug')
    #log.disabled = True
    
    if proxy.ollama_running:
        pytherminal.console(f"[ok]Ollama Localhost Proxy server is listening your LLM API Calls @[url]{proxy.host}:{proxy.port}[/url][/ok]", False)
        pytherminal.console(f"[ok]Ollama and Host hardware informations are displayed in this web UI: [url]http://{proxy.host}:{proxy.port}/info[/url][/ok]", False)
    else:
        pytherminal.console(f"[error]Ollama Localhost Proxy server is running on port @ [url]{proxy.host}:{proxy.port}[/url] but Ollama not found[/error]", False)


    # Define the proxy server routes
    @proxy.server.route('/info')
    def info():
        """ Serve the home page with localhost hardware informations & ollama server details (models available, models running, etc)"""
        return render_template('index.html', release=OLLAMA_PROXY_RELEASE)

    @proxy.server.route('/favicon.ico', methods=['GET'])
    def serveFavicon():
        """ Serve the favicon.ico file (to avoid 404 errors)"""
        return send_from_directory(os.path.join(appPath, 'static/picto'), 'llama.png', mimetype='image/vnd.microsoft.icon')

    @proxy.server.route('/robots.txt', methods=['GET'])
    def serveRobots():
        """ Serve the robots.txt file (to avoid 404 errors)"""
        return "deny: all"


    @proxy.server.route('/')
    def home():
        return proxy.get("", **request.args)
    
    @proxy.server.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
    def catch_all(path):
        """ Catch all routes and forward them to the ollama server """
        if request.method == 'GET':
            # A simple get request will be forwarded to the ollama server
            return proxy.get(path, **request.args)
        elif request.method == 'POST':
            # A POST request will be forwarded to the ollama server and must be streamed
            url=proxy.create_url(path)
            return Response(stream_with_context(stream_request('POST', url, json=request.json, params=request.args)), content_type=request.headers.get('Content-Type'))
        elif request.method == 'OPTIONS':
            # Handle CORS preflight requests called by browsers on the frontend when cors origin must be checked
            return '', 204 
        else:
            return "Method not allowed", 405

    # Manage the streaming chat completions
    def stream_request(method, url, **kwargs):
        """ Stream a request to the ollama server with Flask """
        with requests.request(method, url, stream=True, **kwargs) as r:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk



    # Starting the Flask proxy server with the specified host and port
    proxy.server.run(host=tjs_host, port=tjs_port)

