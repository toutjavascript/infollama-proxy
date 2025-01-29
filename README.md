# Infollama Proxy

Infollama is a Python script that manages a token protection proxy for Ollama.
Infollama also retrieves and displays usefull details about Ollama server (models, running models, size, ram usage, ...) and hardware informations, especially RAM and VRAM.

## WARNING

Very first pre alpha release shared to debug and test on various devices. Please report any issues or bugs you encounter during testing. You can share your ideas and needs.

## Features

![The Infollama Proxy web UI, with models running, models available and hardware details](https://github.com/user-attachments/assets/268dd860-691e-46eb-b236-7be858b195a9)

- Run a proxy to access your Ollama API server, on localhost, LAN and WAN
- Protect your Ollama server with one token by user or usage
- Display usefull details about Ollama server (models, running models, size) and hardware device informations (CPU, GPUS, RAM and VRAM usage).
- Log Ollama API calls in a log file (as an HTTP log file type) with different levels: NEVER, ERROR, INFO, and ALL, including the full JSON prompt request

## Requirements

- Python 3.10 or higher
- Ollama server running on your local machine ([See Ollama repository](https://github.com/ollama/ollama))
- Tested on Linux Ubuntu, Windows 10/11, macOS with Mx Silicon Chip

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/toutjavascript/infollama-proxy.git
   cd infollama-proxy
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the script with the following command:

```sh
python proxy.py
```

Open the browser and navigate to `http://localhost:11430/info` to access the Infollama Proxy web UI and start API calls.

You can modify launch configuration with theses parameters:

```
usage: proxy.py [-h] [--base_url BASE_URL] [--host HOST] [--port PORT] [--cors CORS] [--anonym ANONYM] [--log LOG]
  --base_url BASE_URL  The base_url of localhost Ollama server (default: http://localhost:11434)
  --host HOST          The host name for the proxy server (default: 0.0.0.0)
  --port PORT          The port for the proxy server (default: 11430)
  --cors CORS          The cors policy for the proxy server (default: *)
  --anonym ANONYM      Authorize the proxy server to be accessed anonymously without token (default: False)
  --log LOG            Define the log level that is stored in proxy.log (default: PROMPT, Could be NEVER|ERROR|INFO|PROMPT|ALL)
```

## Update

This repository is under heavy construction. To update the source code from GitHub, open a terminal in the `infollama-proxy` folder and launch a pull request:

```sh
git pull
```

## Check the status of the hardware

Infollama is not only a proxy server but also a powerfull web UI that displays hardware status, like GPU usage and temperatures, memory usage, and other information.

<img width="440" alt="GPU RAM usage" src="https://github.com/user-attachments/assets/ff44cba3-fd4d-4e3d-8956-45da44554d82" />

## API Calls

You can now use the proxy to chat with your Ollama server. You must modify default port configuration. Proxy port is `11430`:

- base_url is now http://localhost:11430

Do not forget to provide a valid token, **starting with `pro_`**, defined in `users.conf` file:

- api_key = "pro_xxxxxxxxxxxxxx"

## Define tokens

Token definitions are set in the `users.conf` file. During first launch, the `users.conf` is created with `users.default.conf` file. This text file lists the tokens line by line with this format:

```
user_type:user_name:token
```

`user_type` can be `user` or `admin`. An `admin` user can access more APIs (like, pull, delete, copy, ...) and can view the full log file in the web UI.
`user_name` is a simple string of text
`token` is a string that needs to starts with `pro_`
Parameters are separated with `:`

If `--anonym` parameter is set to something at starts, the `users.conf` is ignored and all the accesses are authorised. User name is set to `openbar`.

## Logging events

You can log every prompt that are sent to server. Note that responses are not logged to preserve privacy and disk size. This proxy app has several levels of logging:

- `NEVER`: No logs at all.
- `ERROR`: Log only error and not authorised requests.
- `INFO`: Log usefull access (not api/ps, api/tags, ...), **excluding prompts**
- `PROMPT`: Log useful access (not api/ps, api/tags, ...), **including prompts**
- `ALL`: Log every event, **including prompts**

By default, the level is set to `PROMPT`.

Log file uses Apache server log format. For example, one line with `PROMPT` level looks like this:

```
127.0.0.1 - user1 [16/Jan/2025:15:53:10] "STREAM /v1/chat/completions HTTP/1.1" 200	{'model': 'falcon3:1b', 'messages': [{'role': 'system', 'content': "You are a helpful web developer assistant and you obey to user's commands"}, {'role': 'user', 'content': ' Give me 10 python web servers. Tell me cons and pros. Conclude by choosing the easiest one. Do not write code.'}], 'stream': True, 'max_tokens': 1048}
```

## Roadmap

Correcting bug and user issues is priority.

- [ ] Add buttons to start and stop models
- [ ] Add a GPU database to compare LLM performances
- [ ] Create a more efficient installation process
- [ ] Add a dockerfile for easy deployment and easy autostart
- [ ] Add a simple API to that returns the current usage from server (running models, hardware details, Free available VRAM, ...)
- [ ] Add a web UI to view or export logs (by user or full log if admin is connected)
- [ ] Add integrated support for tunneling to web
- [ ] Add a fallback system to access an other LLM provider if the current one is down
- [ ] Add an easy LLM speed benchmark
- [ ] Add a log file size checker

## FAQ

### No GPU information displayed

If you see this error message `Error get_device_info(): no module name 'distutils'`, try to update your install with:

```
pip install -U pip setuptools wheel
```

### Tunneling is already working

Fully tested with solutions like

- nGrok
  `ngrok http http://localhost:11430`

- bore.pub (but no SSL support)
  `bore local 11430 --to bore.pub`

**IF YOU OPEN INFOLLAMA OVER THE WEB, DO NOT FORGET TO CHANGE THE DEFAULT TOKENS IN `users.conf` FILE**

With a web access, the diagram shows you acces from outside your LAN
<img width="953" alt="Diagram with external acces" src="https://github.com/user-attachments/assets/e1f86f8d-62c4-471d-922b-5becf9808c84" />

## Contributing

We welcome contributions from the community. Please feel free to open an issue or a pull request.
