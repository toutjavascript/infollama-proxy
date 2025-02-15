"""
Proxy for the Ollama API on localhost.
Author: toutjavascript.com
Created: 2025-01
"""
import requests
import os
import shutil
import json
import argparse
import multiprocessing
import traceback
import logging                      # Needed to remove terminal flask log 
from flask_cors import CORS
import src.pytherminal as pytherminal
import src.device    as device
import src.utils     as utils
import src.lan       as lan
from rich.pretty import pprint
from datetime import datetime, timezone, timedelta
from typing import Optional

from flask import Flask, render_template, request, send_from_directory, Response, stream_with_context, abort

# Constants to identify version and execution modalities
OLLAMA_PROXY_RELEASE="0.0.1"
OLLAMA_MIN_RELEASE="0.5.5"

# List of endpoints that are allowed to be accessed by the different types of users
# All users have access to that endpoints. This endpoints are necessary for the proxy to start and function properly. 
anonymous_allowed_endpoints=  ["api/tags", "v1/models", "api/version"]

# Only users with a valid token can access that endpoints
user_allowed_endpoints= ["api/show", 
                         "api/version",
                         "api/ps",
                         "api/generate",
                         "api/chat",
                         "api/embed",
                         "v1/chat/completions",
                         "v1/completions",
                         "v1/models",
                         "v1/models/",
                         "v1/embeddings",
                         "info/device",
                         "info/ps"
                        ]
# Only users with a valid admin token can access that endpoints
admin_allowed_endpoints=["api/create", "api/copy", "api/delete", "api/pull", "api/push",
                         "info/admin_api/"]

class InfollamaUser:
    def __init__(self, user_type: str, user_name: str, token: str):
        self.user_type=user_type
        self.user_name=user_name
        self.token=token
    def __str__(self):
        return f"User: {self.user_name}, Type: {self.user_type}"
    def to_dict(self):
        return {"user_type": self.user_type, "user_name": self.user_name, "token": self.token}
    def to_dict_no_token(self):
        return {"user_type": self.user_type, "user_name": self.user_name, "token": "***"}



class InfollamaAccess:
    def __init__(self, user_name: str, is_authorised: bool, desc: str):
        self.user_name=user_name
        self.is_authorised=is_authorised
        self.desc=desc
    def __str__(self):
        if (self.is_authorised):
            return f"Access to {self.user_name} is authorised ({self.desc})"
        else:
            return f"Access to {self.user_name} is forbidden ({self.desc})"

class InfollamaPing:
    def __init__(self, ping: bool, user: InfollamaUser):
        self.ping=ping
        self.user=user
        self.ollama_version=""
        self.proxy_version=OLLAMA_PROXY_RELEASE
        self.config: Optional[InfollamaConfig] = None
    def __str__(self):
        return f"Ping status: {self.ping}, User: {self.user}, Ollama version: {self.ollama_version}, Config: {self.config}"
    def to_dict(self):        
        return {
            'ping': self.ping,
            'proxy_version': self.proxy_version,
            'ollama_version': self.ollama_version,
            'user': self.user.to_dict_no_token(),
            'config': self.config.to_dict()
        }

class InfollamaConfig: 
    def __init__(self, base_url, host, port, cors_policy, user_file, log_file, anonymous_access=False, log_level="ALL"):
        self.base_url=base_url
        self.host=host
        self.port=port
        self.cors_policy=cors_policy
        self.user_file=user_file
        self.log_level=log_level
        self.log_file=log_file
        self.anonymous_access=anonymous_access  
        self.lan_ip=lan.get_lan_ip()
    def __str__(self):
        return f"Base URL: {self.base_url}, Host: {self.host}, Port: {self.port}, Cors Policy: {self.cors_policy}, User File: {self.user_file}, anonymous_access: {self.anonymous_access} Log Level: {self.log_level}, Lan IP: {self.lan_ip}, log_file: {self.log_file}, log_size: {self.log_size}"
    def to_dict(self):        
        return {
            'base_url': self.base_url,
            'host': self.host,
            'port': self.port,
            'cors_policy': self.cors_policy,
            'user_file': self.user_file,
            'log_level': self.log_level,
            'lan_ip': self.lan_ip,
            "anonymous_access": self.anonymous_access  ,
            'log_file': self.log_file,
        }
    def get_log_size(self):
        return os.path.getsize(self.log_file)

class InfollamaProxy:
    def __init__(self, base_url, host, port, cors_policy, user_file, log_file="proxy.log", anonymous_access=False, log_level="ALL"):
        base_url=base_url.rstrip('/').rstrip('/')
        if (base_url.startswith("http://") or base_url.startswith("https://")):
            self.base_url = base_url
        else:
            self.base_url = "http://" + base_url
        self.localhost="localhost"
        self.config=InfollamaConfig(base_url, host, port, cors_policy, user_file, log_file, anonymous_access=anonymous_access, log_level=log_level)
        self.ollama_base_url=base_url
        self.host=host
        self.port=port
        self.server = Flask("infollama_proxy")
        self.ollama_version=None
        self.ollama_running=False
        self.env_vars=dict()
        self.user_file: str=user_file
        self.users= []
        self.get_ollama_env_var()
        self.device=self.update_device_info()
        
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
    
    def update_device_info(self) -> dict:
        """Get device information"""
        device_info = device.get_device_info(self.config.log_file)
        return device_info
    
    def log_event(self, user="internal", method="GET", url="", http_status=200, log_level=0, event="") -> None:
        """ Log an event to the console and the log_file file
            Use the log level to detect the severity of the event
        """



        config_level=self.config.log_level
        # CONFIG LOG LEVEL can be: NEVER|ERROR|INFO|PROMPT|ALL
        if config_level=="NEVER":
            return

        to_be_log=False
        # Only log the event level > 5 on ERROR
        if config_level=="ERROR":
            if log_level>=5:
                to_be_log=True

        # Log each usefull event if the event is level > 1 but without extra event text
        if config_level=="INFO":
            if log_level>=1:
                to_be_log=True
                event=""
        
        # Log each usefull event level > 1 with extra event text (wich contains prompts if provided)
        if config_level=="PROMPT":
            if log_level>=1:
                to_be_log=True
        

        # Log every event (even if the event is level == 0) with extra event text (wich contains prompts if provided)
        if config_level=="ALL":
            if log_level>=0:
                to_be_log=True
        
        if to_be_log is False:
            return

        if url.startswith("/") is False:
            url="/"+url
        
        ip=self.get_user_ip()

        try:
            with open(self.config.log_file, "a") as log_file:
                http_version="HTTP/1.1"                
                current_date = datetime.now().strftime("%d/%b/%Y:%H:%M:%S")
                log_file.write(f"{ip} - {user} [{current_date}] \"{method} {url} {http_version}\" {http_status}\t{event}".strip()+"\n")
        except Exception as e:
            print(f"Error logging event: {e}")
        

    def load_user_file(self) -> None:
        """Load the user file from the self.user_file file formated as type_of_user:user_name:token
        typeof user can be admin or user
        user_name is a string with letters or numbers
        toke is a secret string starting with pro_ followed by a random text string of 10 characters
        Example: admin:john_doe:pro_1234567890
        users found are stored in self.users as a InfollamaUser object
        """

        # Check if user_file exists to copy default values
        if not os.path.exists(self.user_file):
            if (self.user_file=="users.conf"):
                pytherminal.console(f"[info]User file {self.user_file} not found. a default users.conf file is creacted.[/info]", False)
                shutil.copy2("./users.default.conf", "users.conf") 

        try:
            # read the file line by line and create a list of InfollamaUser objects
            with open(self.user_file, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    parts = line.strip().split(':')
                    if len(parts) == 3 and parts[0] in ['admin', 'user']:
                        user_type, user_name, token = parts[0], parts[1], parts[2]
                        self.users.append(InfollamaUser(user_type=user_type, user_name=user_name, token=token))                        
        except FileNotFoundError:
            pytherminal.console(f"[error]User file {self.user_file} not found. No users defined![/error]", False)


        

    def get_user(self, token: str) -> InfollamaUser:
        """Return an InfollamaUser object based on the token"""
        if self.config.anonymous_access is True:
            return InfollamaUser("administrator", "openbar", "")
        if (token is None): 
            return InfollamaUser("anonymous", "anonymous", "")
        for user in self.users:
            if user.token == token:
                return user
        return InfollamaUser("anonymous", "anonymous", "")
    
    def get_token(self, headers = None) -> str:
        """Return the token passed in Bearer Authorization header or return None if not found"""
        if self.config.anonymous_access is True:
            return None                
        if headers is None:
            return None
        auth_header = headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    def check_user_access(self, headers: str, endpoint: str) -> InfollamaAccess:
        """Check if the token is associated to a user who has access to the specified endpoint"""
        if self.config.anonymous_access is True:
            return InfollamaAccess(self.get_user("").user_name, True, "No access control defined by config. Returns openbar user")

        token=self.get_token(headers)
        user=self.get_user(token)
        # Check wich endpoints are allowed for the user type
        if user.user_type=="anonymous":
            allowed_endpoints=anonymous_allowed_endpoints
        elif user.user_type=="user":
            allowed_endpoints=anonymous_allowed_endpoints+user_allowed_endpoints
        elif user.user_type=="admin":
            allowed_endpoints=anonymous_allowed_endpoints+user_allowed_endpoints+admin_allowed_endpoints

        if endpoint not in allowed_endpoints:
            r=InfollamaAccess(user.user_name, False, f"Endpoint {endpoint} is not allowed for user named {user.user_name}, type {user.user_type}")
            return r
        else:
            r=InfollamaAccess(user.user_name, True, f"Access to Endpoint {endpoint} granted to user named {user.user_name}, type {user.user_type}")
            return r

    def get_user_ip(self) -> str:
        """Get the IP address of the user"""
        try:
            return request.remote_addr
        except Exception as e:
            return "0.0.0.0"
    
    def get_info_ps(self, headers) -> dict:
        """Get running models with computed informations"""
        try:
            ps = self.get("api/ps", headers)
            for model in ps["models"]:
                model["expires_in"] = utils.get_diff_date(model.get("expires_at"))
            return ps
        except Exception as e:
            return {"error get_info_ps()": str(e)}

    def get_ollama_env_var(self) -> None:
        """Get the Ollama environment variables from the system"""
        return None # Return None as we don't need to get the environment variables from the system
        try:
            self.env_vars.clear()
            for key in ["OLLAMA_HOST", "OLLAMA_MODELS" ,"OLLAMA_MAX_LOADED_MODELS", "OLLAMA_NUM_PARALLEL", "OLLAMA_MAX_QUEUE", "OLLAMA_FLASH_ATTENTION", "OLLAMA_KV_CACHE_TYPE"]:
                self.env_vars[key]=os.getenv(key)
        except KeyError:
            pass


    def create_url(self, endpoint: str) -> str:
        """Create a URL for the Ollama API, with base_url and endpoint"""
        if (endpoint.startswith("/")):
            endpoint = endpoint[1:]
        return f"{self.ollama_base_url}/{endpoint}"
    
    def get(self, endpoint, headers, **kwargs):
        """Send a GET request to the Ollama API if the token access to endpoint is validated"""

        if endpoint =="":
            return "<script>window.location.href='/info';</script>"

        access=self.check_user_access(headers, endpoint)
        if access.is_authorised is False:
            self.log_event(access.user_name, "GET", endpoint, 403, log_level=9)
            # return a status code 403 to flask server
            return abort(403)
        log_level=1
        if endpoint=="api/ps" or endpoint=="api/tags" or endpoint=="v1/models" or endpoint=="api/show":
            # if access is authorized and the endpoint are not sensible, log_level is 0 and no log is stored
            log_level=0
        self.log_event(access.user_name, "GET", endpoint, 200, log_level=log_level)

        url = self.create_url(endpoint)
        try:
            response = requests.get(url, params=kwargs)
            if (utils.is_json(response.text)):
                return response.json()      
            else:
                return response.text
        except Exception as e:
            pytherminal.console(f"self.get() [error]{e}[/error]");
            return abort(500)
    
    def post(self, endpoint, headers, data=None, **kwargs):
        """Transmit a POST call"""
        access=self.check_user_access(headers, endpoint)
        if access.is_authorised is False:
            self.log_event(access.user_name, "POST", endpoint, 403, log_level=9)
            return abort(403)
        log_level=1
        if endpoint=="api/ps" or endpoint=="api/tags" or endpoint=="v1/models" or endpoint=="api/show":
            # if access is authorized and the endpoint are not sensible, log_level is 0 and no log is stored
            log_level=0

        url = self.create_url(endpoint)     
        try:
            response = requests.post(url, json=request.json, params=kwargs)
            self.log_event(access.user_name, "POST", endpoint, 200, log_level=log_level, event=request.json.__str__())
            if (utils.is_json(response.text)):
                return response.json()      
            else:
                return response.text
        except Exception as e:
            pytherminal.console(f"self.post() [error]{e}[/error]");
            abort(500)
    
    def stream(self, endpoint, headers, data=None, **kwargs):
        """Transmit and listen to a stream"""
        access=self.check_user_access(headers, endpoint)
        if access.is_authorised is False:
            self.log_event(access.user_name, "STREAM", endpoint, 403, log_level=9)
            return abort(403)
        log_level=1
        if endpoint=="api/ps" or endpoint=="api/tags" or endpoint=="v1/models" or endpoint=="api/show":
            # if access is authorized and the endpoint are not sensible, log_level is 0 and no log is stored
            log_level=0        
        self.log_event(access.user_name, "STREAM", endpoint, 200, log_level=log_level, event=request.json.__str__())

        url = self.create_url(endpoint)        
        return Response(stream_with_context(stream_request('POST', url, json=request.json, params=request.args)), content_type=request.headers.get('Content-Type'))


    # Check python version and venv
    def print_versions(self) -> None:
        """Display Python version and OS information on terminal"""
        pythonVersion=utils.getPythonVersion()
        OS=utils.getOS()
        pytherminal.console(" ", False)
        pytherminal.console(" You are running [b]Python V"+pythonVersion+"[/b] on [b]"+OS+"[/b]", False)
        if utils.in_venv():
            pytherminal.console(" [b] (virtual env) is activated[/b]", False)
        else:
            pytherminal.console(" [error] Carefull, (virtual env) is not activated. You may experience module version issues[/error]", False)


    def check_ollama_connection(self) -> bool:
        """
        Trying to connect to ollama server and checking if it's running."""
        try:
            response=requests.get(f"{self.ollama_base_url}")
            self.ollama_running=True
            return True
        except requests.exceptions.RequestException as e:
            self.ollama_running=False
            return False
        
        
    def get_ollama_version(self) -> str|None:
        """ Trying to read the /api/version to ensure this is a real ollama server on base_url. """
        url=self.create_url("/api/version")
        response=requests.get(url)

        try:
            response=json.loads(response.text)
            self.ollama_version=response["version"]
            self.ollama_running=True
            return self.ollama_version
        except Exception as e:
            
            print(f"get_ollama_version() failed: {e}")
            self.ollama_running=False
            self.ollama_version=None
            return None        


if __name__ == "__main__":
    # Only one instance of this proxy server can be run at a time. This is done by freezing the support for multiprocessing.
    multiprocessing.freeze_support()
   

    ########## CONFIGURATION #################################################################################################################
    tjs_host="0.0.0.0"                      # host of the proxy server (localhost or 127.0.0.1 to keep on the same machine, 0.0.0.0 to allow connections from any machine)
    tjs_port=11430                          # port of the proxy server
    cors_policy="*"                         # cors policy of the proxy server (* allows all origins, None fixes policy to same origin)
    base_url="http://localhost:11434"       # base url of the Ollama server
    user_file="users.conf"                  # path to the user file containing credentials
    log_level="PROMPT"                      # log level of the proxy server
    log_file="infollama.log"                # path to the log file for the proxy server
    anonymous_access=False                  # Allows anonymous access to all API without providing token (default false)
    ##########################################################################################################################################

    # Reading the argument parameters
    parser = argparse.ArgumentParser(description='Run a proxy filtered server to forward API requests to Ollama server defined by base_url.')
    parser.add_argument('--base_url', type=str, default=base_url, help=f'The base_url of localhost Ollama server (default: {base_url})')
    parser.add_argument('--host', type=str, default=tjs_host, help=f'The host name for the proxy server (default: {tjs_host})')
    parser.add_argument('--port', type=str, default=tjs_port, help=f'The port for the proxy server (default: {tjs_port})')
    parser.add_argument('--cors', type=str, default=cors_policy, help=f'The cors policy for the proxy server (default: {cors_policy})')
    parser.add_argument('--anonym', type=bool, default=anonymous_access, help=f'Authorize the proxy server to be accessed anonymously without token (default: {anonymous_access})')
    parser.add_argument('--log', type=str, default=log_level, help=f'Define the log level that is stored in {log_file} (default: {log_level}, Could be NEVER|ERROR|INFO|PROMPT|ALL)')
    args = parser.parse_args()

    proxy = InfollamaProxy(base_url=args.base_url, host=args.host, port=args.port, cors_policy=args.cors, user_file=user_file, log_level=args.log, log_file=log_file,  anonymous_access=args.anonym )
    #print("proxy after init()", proxy)

    # Display on terminal the state of application.
    pytherminal.console("[reverse][h1]*******************    Infollama Proxy V "+OLLAMA_PROXY_RELEASE+" started    ******************[/h1][/reverse]", False)
    pytherminal.console("  [ok]Thanx for using. Please report issues and ideas on[/ok]", False)
    pytherminal.console("  [url]https://github.com/toutjavascript/infollama-proxy[/url]", False) 
    proxy.print_versions()
    proxy.check_ollama_connection()
    if proxy.ollama_running:
        proxy.get_ollama_version()

        if (proxy.ollama_version is not None):
            pytherminal.console(f"[green]Ollama [u]V {proxy.ollama_version}[/u] is running @[url]{proxy.ollama_base_url}[/url][/green]", False)
        else:
            pytherminal.console(f"[error]Are you sure Ollama is running @[url]{proxy.ollama_base_url}[/url][/error]", False)
    else:
        pytherminal.console(f"[error]Ollama not found or stopped @[url]{proxy.ollama_base_url}[/url][/error]", False)



    proxy.load_user_file()
    
    appPath=utils.getAppPath()
    # Prevent http flask web server logging in terminal 
    log = logging.getLogger('werkzeug')
    log.disabled = True
    
    if proxy.ollama_running:
        pytherminal.console(f"[ok]Proxy server is listening your LLM API Calls @[url]{proxy.localhost}:{proxy.port}[/url][/ok]", False)
        pytherminal.console(f"[ok]Ollama and Host hardware informations are displayed in this web UI: [url]http://{proxy.localhost}:{proxy.port}/info[/url][/ok]", False)
    else:
        pytherminal.console(f"[error]Proxy server is running on port @ [url]{proxy.localhost}:{proxy.port}[/url] but Ollama not found[/error]", False)

    if proxy.config.host=="0.0.0.0":
        pytherminal.console(f"   [warning]Be aware that this Infollama Proxy server is accessible on your Local Area Network  @[url]{proxy.config.lan_ip}:{proxy.port}[/url][/warning]", False)

    if proxy.config.anonymous_access is True:
        pytherminal.console(f"   [error]Be carefull: this proxy server is openbar because you launch it with --anonym param. No token needed ![/error]", False)
    else:
        pytherminal.console(f"   Here the {len(proxy.users)} users who have an access token (listed in {user_file}) :", False)
        for user in proxy.users:
            pytherminal.console(f"      {user.user_name.ljust(15, " ")}   [b]{user.user_type}[/b] ", False)

    # Define the proxy server routes
    @proxy.server.route('/info')
    def info():
        """ Serve the home page with localhost hardware informations & ollama server details (models available, models running, etc)"""
        proxy.log_event("anonymous", "GET", "/info", 200, log_level=1)
        return render_template('index.html', release=OLLAMA_PROXY_RELEASE)

    @proxy.server.route("/info/ping",  methods=['GET', 'POST'])
    def ping():
        """ Ping the Ollama server to check if it's running and get user/token information """
        user=proxy.get_user(proxy.get_token(request.headers))
        ping=InfollamaPing(False, user)
        try:
            response = proxy.get("api/tags", request.headers)
            if response:
                ping.ping=True
                ping.config=proxy.config
                ping.ollama_version=proxy.ollama_version
                proxy.get_ollama_version() # To update version number
                return ping.to_dict()
            else:
                return ping.to_dict()
        except requests.RequestException as e:
            return ping.to_dict()
    
    @proxy.server.route("/info/device")
    def info_device():
        """ Get device information only to authorized users """
        if proxy.check_user_access(request.headers, "info/device").is_authorised:
            try:
                proxy.device=device.get_device_info(proxy.config.log_file)
            except Exception as e:
                traceback.print_exc()
                print("[b]Error get_device_info():[/b]", e)
                print("[b]Try to update your install with this command:\n pip install -U pip setuptools wheel[/b]")
                proxy.device=None

            return proxy.device
        else:
            return abort(403)
        
    @proxy.server.route("/info/ps")
    def info_ps():
        """ Get running models with computed informations """
        if proxy.check_user_access(request.headers, "info/ps").is_authorised:
            return proxy.get_info_ps(request.headers)
        else:
            return abort(403)



    @proxy.server.route('/favicon.ico', methods=['GET'])
    def serveFavicon():
        """ Serve the favicon.ico file (to avoid 404 errors)"""
        return send_from_directory(os.path.join(appPath, 'static/picto'), 'infollama.png', mimetype='image/vnd.microsoft.icon')

    @proxy.server.route('/robots.txt', methods=['GET'])
    def serveRobots():
        """ Serve the robots.txt file (to avoid 404 errors)"""
        return "deny: all"

    @proxy.server.route('/')
    def home():
        return proxy.get("", None, **request.args)
    
    @proxy.server.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
    def catch_all(path):
        """ Catch all routes and forward them to the ollama server """
        if request.method == 'GET':
            # A simple get request will be forwarded to the ollama server
            return proxy.get(path, request.headers, **request.args)
        elif request.method == 'POST':
            # A POST request will be forwarded to the ollama server and must be streamed if stream parameter is set
            if "stream" in request.json:
                if request.json["stream"] is not False:
                    url=proxy.create_url(path)
                    return proxy.stream(path, request.headers, **request.args)
                else:
                    return proxy.post(path, request.headers, **request.args)
            else:
                #By default, the response will be returned as a stream
                return proxy.stream(path, request.headers, **request.args)
                

        elif request.method == 'OPTIONS':
            # Handle CORS preflight requests called by browsers on the frontend when cors origin must be checked
            # Always accept CORS preflight requests called by browsers on the frontend when cors origin must be checked
            if proxy.config.cors_policy=="*":
                return '', 204 
        else:
            proxy.log_event("-", "POST", path, 405, log_level=9)
            return "Method not allowed", 405

    # Manage the streaming chat completions
    def stream_request(method, url, **kwargs):
        """ Stream a request to the ollama server with Flask """
        with requests.request(method, url, stream=True, **kwargs) as r:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk



    # Starting the Flask proxy server with the specified host and port
    proxy.log_event(event=f"Proxy server starting on {args.host}:{args.port}", log_level=5)
    proxy.server.run(host=args.host, port=tjs_port)
