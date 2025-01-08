"""
Application to display Ollama installed model informations.

Author: toutjavascript.com
Date: 2025-01
"""

# Standard imports
import argparse
import re
import sys
from datetime import datetime

# Third party imports
import requests
from rich import print as rprint


# Local imports
import pytherminal



# Define main constants
BASE_URL= "http://localhost:11434" 
VERSION="0.1"
GITHUB_REPO="https://github.com/toutjavascript/infollama"

#Define class for model information

class ModelInfo:
    def __init__(self, name, modified_at, id, size, size_number, family, quantization_level, parameter_size, context_length, context_length_number, running, parameters=""):
        self.name = name
        #Modify name to name_sort: Ex qwen2.5:1.5b becomes qwen2.5:001.5b
        name_sort = re.sub(r':([0-9]+)', lambda m: f":{m.group(1).zfill(5)}", name)
        self.name_sort=name_sort
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
        self.running=running
        self.parameters=parameters
        
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


def get_diff_date(dt1, dt2="now"):
    if dt2 == "now":
        dt2 = datetime.now().isoformat()
    dt1 = datetime.fromisoformat(dt1)
    dt2 = datetime.fromisoformat(dt2)
    
    if dt1.tzinfo is None and dt2.tzinfo is not None:
        dt1 = dt1.replace(tzinfo=dt2.tzinfo)
    elif dt1.tzinfo is not None and dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=dt1.tzinfo)
    
    delta = dt1 - dt2
    return str(round(delta.total_seconds() / 60))+" min"  # return difference in minutes


# parse BB code and print it in console
def parseBB(text):
    text=re.sub(r"(\[h1\])([^\[\]]+)(\[/h1\])", "\033[32;1m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[ok\])(.+)(\[/ok\])", "\033[32;1m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[error\])([^\[\]]+)(\[/error\])", "\033[31;1m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[b\])([^\[\]]+)(\[/b\])", "\033[1m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[u\])([^\[\]]+)(\[/u\])", "\033[4m\\2\033[24m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[d\])([^\[\]]+)(\[/d\])", "\033[2m\\2\033[22m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[fade\])([^\[\]]+)(\[/fade\])", "\033[2m\\2\033[22m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[warning\])([^\[\]]+)(\[/warning\])", "\033[33m\\2\033[22m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[reset\])", "\033[0m\033[49m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[reverse\])(.+)(\[/reverse\])", "\033[7m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[header\])([^\[\]]+)(\[/header\])", "\033[1m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[hour\])([^\[\]]+)(\[/hour\])", "\033[48;5;255m\\2\033[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[shell\])([^\[\]]+)(\[/shell\])", "\033[44;1;97m\\2\033[0m", text, flags=re.IGNORECASE)
    return text


def printBB(text): 
    print(parseBB(text))

def get_now_as_iso():
    return datetime.now().isoformat()[:10]

def check_date_format(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def get_date_diff(date1, date2, round_to=0):
    # Convert the dates to datetime objects and return a number of days if diff is less than 7 days or weeks or months
    date_format = "%Y-%m-%d"
    date1 = datetime.strptime(date1, date_format)
    date2 = datetime.strptime(date2, date_format)
    diff = abs(date2 - date1).days
    if diff < 7:
        return f"{diff} day{'s' if diff > 1 else ''} ago"
    elif diff >= 7 and diff < 30:
        w=int(round(diff / 7, round_to))
        return f"{w} week{'s' if w > 1 else ''} ago"
    else:
        m=int(round(diff / 30, round_to))
        return f"{m} month{'s' if m > 1 else ''} ago"

def format_bytes(B, round_to=2):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return f"{0:.{round_to}f} KB".format(B/KB)
    elif MB <= B < GB:
        return f"{0:.{round_to}f} MB".format(B/MB)
    elif GB <= B < TB:
        return f"{0:.{round_to}f} GB".format(B/GB)
    elif TB <= B:
        return f"{0:.{round_to}f} TB".format(B/TB)

def get_terminal_size():
    import os
    size=os.popen('stty size', 'r').read().split()
    return int(size[0]),int(size[1])


def print_line(text):
    sys.stdout.write(parseBB(text))
    sys.stdout.flush()

def clear_line():
    sys.stdout.write('\033[2K')  # Clear the entire line
    sys.stdout.write('\033[0G')  # Move the cursor to the beginning of the line
    sys.stdout.flush()

def get_value_type(obj):
    return str(type(obj)).replace("<class '", "").replace("'>", "")


####################################################################################################################

def get_ollama_version(base_url):
    response = requests.get(f"{base_url}/api/version")
    if (response.status_code != 200):
        print("Error: Unable to retrieve model list")
        return "?"
    data = response.json()
    return data["version"]

def get_ollama_ps(base_url):
    response = requests.get(f"{base_url}/api/ps")
    if (response.status_code != 200):
        print("Error: Unable to retrieve model list")
        return None
    data = response.json()
    #print(data)
    return data


def get_ollama_model_list(base_url, sort="date", filter=""):
    models=[]

    pytherminal.print_line(f"Getting list of models from Ollama @[b]{base_url}[/b]")

    response = requests.get(f"{base_url}/api/tags")
    if (response.status_code != 200):
        print("Error: Unable to retrieve model list")
        return None
    data = response.json()
    nb_model=len(data['models'])

    version=get_ollama_version(base_url)
 
    pytherminal.clear_line()
    pytherminal.print_line(f"{nb_model} models found from Ollama V{version} @[b]{base_url}[/b] ")

    ps=get_ollama_ps(base_url)
    runnings=ps["models"]


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
        pytherminal.print_line(f"Fetching details from model #[b]{str(no_model).rjust(3)} / {nb_model}[/b] from Ollama V{version} @[b]{base_url}[/b]")

        show = requests.post(f"{base_url}/api/show/", json={"model": model["model"]})
        context_length=0
        parameter_count=0
        parameters=""
        running=""
        if (show.status_code == 200):           
            show=show.json()
            if "parameters" in show:
                parameters=str(show["parameters"])
                parameters=parameters.replace("\n", "   ")
                parameters=re.sub(r'\s{4,}', '===', parameters)
                parameters=parameters.strip()
                parameters=""
            if "model_info" in show and model["details"]["family"]+".context_length" in show["model_info"]:
                context_length = "{:,.0f} k".format(show["model_info"][model["details"]["family"]+".context_length"]/1024).rjust(8," ")
                context_length_number=show["model_info"][model["details"]["family"]+".context_length"]
            if "model_info" in show and "general.parameter_count" in show["model_info"]:
                parameter_count = "{:,.1f} B".format(show["model_info"]["general.parameter_count"]/1024/1024/1024).rjust(10," ")
               

        #Searching for running models
        for run in runnings:
            if run["digest"][:12] == model["digest"][:12]:
                pct="{:.0f}%".format(run["size_vram"]/run["size"]*100)
                ram="{:.1f} GB".format(run["size"]/1024/1024/1024)
                running="ill "+get_diff_date(run["expires_at"], "now")+ ", RAM: "+ram+ " ("+pct+" GPU)"
                break
  

        model_info=ModelInfo(model["model"], model["modified_at"][:10], model["digest"][:12], size, size_number, model["details"]["family"], " "+model["details"]["quantization_level"], parameter_count, context_length, context_length_number, running, parameters)
        models.append(model_info)

    #Sorting models array by sort parameter
    sort_mapping={"date":"modified_at", "size":"size_number", "name":"name_sort", "family": "family", "context": "context_length_number"}
    sort_key = sort_mapping.get(sort, "modified_at")
    models.sort(key=lambda x: getattr(x, sort_key))

    totalGB="{0:.2f} GB".format(totalGB/1024/1024/1024)
    models.append(ModelInfo(f"  You got {no_model} model{'s' if no_model > 1 else ''}", "", "", totalGB, "", "", "", "", "", "", ""))


    pytherminal.clear_line()
    if filter!="":
        pytherminal.print_line(f"{len(models)-1}/{nb_model} models found from Ollama [b]@{base_url}[/b] sorted by [u]{sort}[/u]{", filtered with '[u]"+filter+"[/u]'" if filter!="" else ''}")
    else:
        pytherminal.print_line(f"{nb_model} models found from Ollama V{version} [b]@{base_url}[/b] sorted by [u]{sort}[/u]")
        


    return models

def print_table(my_array, ignore_columns=None, align_right_columns=None, titles_mapping=None):
    titles=[]
    display_titles=[]
    types=[]    
    rows=[]

    for (num_row, row) in enumerate(my_array[:5000]):
        values=[]
        if hasattr(row, '__dict__'):
            row = row.__dict__.items()
        for (num_col, col) in enumerate(row):
            title, value=col
            if title in ignore_columns:
                continue

            if (num_row==0):
                titles.append(title)
                display_titles.append(titles_mapping.get(title, title))
                types.append(pytherminal.get_value_type(value))
            
            # Check typeof value and convert it to the right type
            type=get_value_type(value)
            if (type=="str"):
                value=str(value)
                if (check_date_format(value)):
                    type="date"
                    value=get_date_diff(value, get_now_as_iso())
            elif (type=="int"):
                value=int(value)
                if (titles[num_col]=="size"):
                    value=format_bytes(value, 1)
            elif (type=="float"):
                value=float(value)
            elif (type=="bool"):
                value=bool(value)
            else:
                value=str(value)
            values.append(value)

            #print("   ",num_col, col, get_value_type(col), " => ", title, "=", value)

        rows.append(values)


    #Looking for the max columns width
    #Init the widths with the lenghts of the first row (titles array)
    widths=[]
    for (num_col, title) in enumerate(display_titles):
        widths.append(len(str(title)))

    #Get the new max of each column width
    for (num_row, row) in enumerate(rows):
        for (num_col, col) in enumerate(row):
            if (len(str(row[num_col]))>widths[num_col]):
                widths[num_col]=len(str(row[num_col]))


    #Printing the table with right width
    line=""
    for (num_col, title) in enumerate(display_titles):
        line+=""+title.ljust(widths[num_col]+1)+" "
    printBB("[header]"+line+"[/header]")

    for (num_row, row) in enumerate(rows):
        line=""
        running=False
        for (num_col, col) in enumerate(row):
            value=str(col)
            if (types[num_col]=="int"):
                line+=""+value.rjust(widths[num_col]+1," ")+" "                
            elif (types[num_col]=="float"):
                line+=""+value.rjust(widths[num_col]+1," ")+" "        
            else:
                if (value[-3:]==" GB"):
                    line+=value.rjust(widths[num_col]+1," ")+" "
                elif (value.strip()=="0 k"):
                    line+=(" " if num_col>0 else "")+"[fade]"+value.ljust(widths[num_col]+1," ")+"[/fade]"
                else:  
                    if (titles[num_col] in align_right_columns):
                        line+=(" " if num_col>0 else "")+value.rjust(widths[num_col]," ")+" "
                    else:                  
                        line+=(" " if num_col>0 else "")+value.ljust(widths[num_col]+1," ")
            if (titles[num_col]=="running" and value!=""):
                running=True
        if running==True:
            printBB("[reverse][h1]"+line+"[/h1][/reverse]")
        else:
            printBB(line)




def main(base_url, sort, filter):
    models = get_ollama_model_list(base_url, sort, filter)
    pytherminal.print_line("\n")
    print_table(
        models, 
        ignore_columns=["size_number","context_length_number", "name_sort"], 
        align_right_columns=["family", "modified_at"],
        titles_mapping={"name": "Model Name", "size": "File Size", "modified_at": "Loaded", "context_length": "Max Ctx", "parameter_size": "Parameters", "quantization": "Quantiz."}
    )

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

    base_url=args.base_url
    if (base_url[:7] != "http://"):
        base_url="http://"+base_url

    main(base_url, args.sort, args.filter)