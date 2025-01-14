## WARNING

Very first pre alpha release shared to debug and test on various devices.
Please report any issues or bugs you encounter during testing.

# InfoLlama

InfoLlama is a Python script that retrieves and displays a list of models from an Ollama server. It provides detailed information about each model, including name, size, family, quantization level, parameter size, and context length. The output is formatted and displayed in the terminal with BB code support for enhanced readability.

## Features

- Retrieve and display a list of models from an Ollama server.
- Sort models by date, name, size, family, or context length.
- Filter models by name.
- Display detailed information about each model.

## Requirements

- Python 3.13 or higher
- `requests` library

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/toutjavascript/infollama.git
   cd infollama
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
