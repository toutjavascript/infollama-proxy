import requests
import argparse
import pytherminal

# Define main constants
BASE_URL= "http://localhost:11434" 
VERSION="0.1"
GITHUB_REPO="https://github.com/toutjavascript/"

#Define class for model information
class ModelInfo:
    def __init__(self, name, modified_at, id, size, size_number, family, quantization_level, parameter_size, context_length, context_length_number):
        self.name = name
        self.family = family
        self.size = size
        self.size_number = size_number
        self.parameter_size = parameter_size
        self.context_length = context_length
        self.context_length_number = context_length_number
        self.quantization = quantization_level
        self.modified_at = modified_at
        self.id = id
    def __iter__(self):
        return iter([self.name, self.modified_at, self.id, self.size, self.family, self.quantization_level, self.parameter_size, self.context_length])
    def __repr__(self):
        return (f"ModelInfo(name={self.name}, modified_at={self.modified_at}, id={self.id}, size={self.size}, "
                f"family={self.family}, quantization_level={self.quantization}, parameter_size={self.parameter_size}, "
                f"context_length={self.context_length})")

class PrintVersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        pytherminal.printBB(f"[h1]Version of infollama: {VERSION}[/h1]. More informations @ [u]{GITHUB_REPO}[/u]")
        parser.exit()


def get_ollama_model_list(base_url, sort="date", filter=""):
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
        if (filter != "") and filter not in model["name"]:
            continue

        no_model+=1
        totalGB+=model["size"]
        size_number=model["size"]
        size="{0:.2f} GB".format(model["size"]/1024/1024/1024)
        pytherminal.clear_line()
        pytherminal.print_line(f"Fetching details from model #[b]{str(no_model).rjust(3)} / {nb_model}[/b] from Ollama @[b]{base_url}[/b]")

        show = requests.post(f"{base_url}/api/show/", json={"model": model["model"]})
        context_length=0
        parameter_size=0
        if (show.status_code == 200):           
            show=show.json()
            if "details" in show and "parameter_size" in show["details"]:
                parameter_size = show["details"]["parameter_size"]
            if "model_info" in show and model["details"]["family"]+".context_length" in show["model_info"]:
                context_length = "{0:.0f} k".format(show["model_info"][model["details"]["family"]+".context_length"]/1024).rjust(14," ")
                context_length_number=show["model_info"][model["details"]["family"]+".context_length"]
            if "model_info" in show and "general.parameter_count" in show["model_info"]:
                parameter_size = "{0:.2f} B".format(show["model_info"]["general.parameter_count"]/1024/1024/1024).rjust(14," ")

                

        model_info=ModelInfo(model["model"], model["modified_at"][:10], model["digest"][:12], size, size_number, model["details"]["family"], "      "+model["details"]["quantization_level"], parameter_size, context_length, context_length_number)
        models.append(model_info)

    #Sorting models array by sort parameter
    sort_mapping={"date":"modified_at", "size":"size_number", "name":"name", "family": "family", "context": "context_length_number"}
    sort_key = sort_mapping.get(sort, "modified_at")
    models.sort(key=lambda x: getattr(x, sort_key))

    totalGB="{0:.2f} GB".format(totalGB/1024/1024/1024)
    models.append(ModelInfo(f"  You got {no_model} model{'s' if no_model > 1 else ''}", "", "", totalGB, "", "", "", "", "", ""))


    pytherminal.clear_line()
    if filter!="":
        pytherminal.print_line(f"{len(models)-1}/{nb_model} models found from Ollama [b]@{base_url}[/b] sorted by [u]{sort}[/u]{", filtered with '[u]"+filter+"[/u]'" if filter!="" else ''}")
    else:
        pytherminal.print_line(f"{nb_model} models found from Ollama [b]@{base_url}[/b] sorted by [u]{sort}[/u]")
        
    


    return models

def main(base_url, sort, filter):
    models = get_ollama_model_list(base_url, sort, filter)

    pytherminal.print_line("\n")
    pytherminal.table(models, ignore_columns=["size_number","context_length_number"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get a readable and sortable list of installed models, name, size and details from Ollama')
    parser.add_argument('--base_url', type=str, default=BASE_URL, help='The base URL for the Ollama server')
    parser.add_argument('--sort', type=str, choices=['date', 'name', 'size', 'family', "context"], default='date', help='Sort the models by params')
    parser.add_argument('--filter', type=str, default='', help='Filter the models by names')
    parser.add_argument('--version',  nargs=0, action=PrintVersionAction, help='Print version of this programm infollama')

    args = parser.parse_args()

    if (args.version):
        print(parser.format_help())
        exit(0)

    main(args.base_url, args.sort, args.filter)