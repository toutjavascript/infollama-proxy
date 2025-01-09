"""
Proxy for the Ollama API on localhost.
Author: toutjavascript.com
Created: 2025-01
"""
import requests
class InfollamaProxy:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
    def get(self, endpoint, **kwargs):
        url = f"http://{self.host}:{self.port}/{endpoint}"
        response = requests.get(url, params=kwargs)
        return response.json()  
    def post(self, endpoint, data=None, **kwargs):
        url = f"http://{self.host}:{self.port}/{endpoint}"
        response = requests.post(url, json=data, params=kwargs)
        return response.json()
    def put(self, endpoint, data=None, **kwargs):
        url = f"http://{self.host}:{self.port}/{endpoint}"
        response = requests.put(url, json=data, params=kwargs)
        return response.json()  
    def delete(self, endpoint, **kwargs):
        url = f"http://{self.host}:{self.port}/{endpoint}"
        response = requests.delete(url, params=kwargs)
        return response.json()
    def __getattr__(self, name):
        if hasattr(InfollamaProxy, name):
            return getattr(InfollamaProxy, name)
        raise AttributeError(f"'{name}' not found in InfollamaProxy")


    def check_connection(self):
        try:
            requests.get(f"http://{self.host}:{self.port}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Connection failed: {e}")
            return False
        


if __name__ == "__main__":
    proxy = InfollamaProxy("localhost", 8080)
    response = proxy.get("/api/data")
    print(response)  

