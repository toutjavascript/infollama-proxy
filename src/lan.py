import socket
def get_lan_ip():
    """ Return the LAN ip address of the machine. """
    try:
        # Create a socket and connect to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # We don't actually send any data - this is just to get our local IP
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        #return f"Error: {e}"
        return "undefined"

if __name__ == "__main__":
    print(f"LAN IP: {get_lan_ip()}")
