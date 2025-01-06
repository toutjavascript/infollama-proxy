import requests
import argparse
import pytherminal

# Define main constants
BASE_URL= "http://localhost:11434" 

#Define class for model information
class ModelInfo:
    def __init__(self, name, modified_at, id, size, family, quantization_level, parameter_size, context_length):
        self.name = name
        self.size = size
        self.family = family
        self.quantization = quantization_level
        self.parameter_size = parameter_size
        self.context_length = context_length
        self.modified_at = modified_at
        self.id = id
    def __iter__(self):
        return iter([self.name, self.modified_at, self.id, self.size, self.family, self.quantization_level, self.parameter_size, self.context_length])
    def __repr__(self):
        return (f"ModelInfo(name={self.name}, modified_at={self.modified_at}, id={self.id}, size={self.size}, "
                f"family={self.family}, quantization_level={self.quantization_level}, parameter_size={self.parameter_size}, "
                f"context_length={self.context_length})")

def get_ollama_model_list(base_url):

    if (base_url[:7] != "http://"):
        base_url="http://"+base_url

    models=[]

    pytherminal.print_line(f"Getting list of models from Ollama @[b]{base_url}[/b]")

    response = requests.get(f"{base_url}/api/tags")
    if (response.status_code != 200):
        print("Error: Unable to retrieve model list")
        return None
    data = response.json()
    nb_model=len(data['models'])
    pytherminal.clear_line()
    pytherminal.print_line(f"{nb_model} models found from Ollama @[b]{base_url}[/b] ")

    totalGB=0
    no_model=0

    for model in data["models"]:
        no_model+=1
        totalGB+=model["size"]
        model["size"]="{0:.2f} GB".format(model["size"]/1024/1024/1024)
        json = {  "model": model["model"]}
        pytherminal.clear_line()
        pytherminal.print_line(f"Fetching details from model #[b]{str(no_model).rjust(3)} / {nb_model}[/b] from Ollama @[b]{base_url}[/b]")

        show = requests.post(f"{base_url}/api/show/", json=json)
        context_length=0
        parameter_size=0
        if (show.status_code == 200):           
            show=show.json()
            if "details" in show and "parameter_size" in show["details"]:
                parameter_size = show["details"]["parameter_size"]
            if "model_info" in show and model["details"]["family"]+".context_length" in show["model_info"]:
                context_length = "{0:.0f} k".format(show["model_info"][model["details"]["family"]+".context_length"]/1024).rjust(14," ")
            if "model_info" in show and "general.parameter_count" in show["model_info"]:
                parameter_size = "{0:.2f} B".format(show["model_info"]["general.parameter_count"]/1024/1024/1024).rjust(14," ")

                

        model_info=ModelInfo(model["model"], model["modified_at"][:10], model["digest"][:12], model["size"], model["details"]["family"], model["details"]["quantization_level"], parameter_size, context_length)
        models.append(model_info)

    totalGB="{0:.2f} GB".format(totalGB/1024/1024/1024)
    models.append(ModelInfo(f"  You got {no_model} model{'s' if no_model > 1 else ''}", "", "", totalGB, "", "", "", ""))


    pytherminal.clear_line()
    pytherminal.print_line(f"{nb_model} models found from Ollama [b]@{base_url}[/b] ")
    


    return models

def main(base_url):
    models = get_ollama_model_list(base_url)

    pytherminal.print_line("\n")
    pytherminal.table(models)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--base_url', type=str, default=BASE_URL, help='The base URL for the API')

    args = parser.parse_args()
    main(args.base_url)