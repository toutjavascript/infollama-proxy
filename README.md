# InfoLlama Proxy

InfoLlama is a Python script that manage a proxy to Ollama
InfoLlama also retrieves and displays usefull details about Ollama server (models, running models, size, ram usage, ...) and some hardware informations.

## WARNING

Very first pre alpha release shared to debug and test on various devices.
Please report any issues or bugs you encounter during testing.

## Features

- Run a proxy with token that accesses to Ollama server API.
- Retrieve and display a list of models from an Ollama server.
- Display usefull details about Ollama server (models, running models, size, ram usage, ...) and some hardware informations.

## Requirements

- Python 3.13 or higher
- Ollama server running on your local machine

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

Open the browser and navigate to `http://localhost:11430/info` to access the InfoLlama Proxy web UI
