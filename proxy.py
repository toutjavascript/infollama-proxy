"""
Proxy for the Ollama API on localhost.
Author: toutjavascript.com
Created: 2025-01
"""
import requests
import src.pytherminal as pytherminal
import src.device    as device

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
    proxy = InfollamaProxy()
    response = proxy.check_connection()
    print(response)
    response = proxy.get("api/version")
    print("proxy", proxy)
    print(response)

    print(device.getDeviceInfo())  

