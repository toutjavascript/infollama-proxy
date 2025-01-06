# Python Console Module that allows to print BB code in terminal 
# Pimp your terminal with colors 
#  @toutjavascript  https://github.com/toutjavascript
#  V1 : 2025



import re
import inspect
import utils
import sys

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

def table(my_array):
    # Looking for the values of the table
    # Loooking for the titles of the table 
    titles=[]
    types=[]    
    rows=[]


    for (num_row, row) in enumerate(my_array[:5000]):
        #print(num_row, row)
        values=[]
        if hasattr(row, '__dict__'):
            row = row.__dict__.items()
        for (num_col, col) in enumerate(row):
            # print("  ", get_value_type(col))
            # print("     ", num_col, col)
            title, value=col

            if (num_row==0):
                titles.append(title)
                types.append(get_value_type(value))
            # Check typeof value and convert it to the right type
            type=get_value_type(value)
            if (type=="str"):
                value=str(value)
            elif (type=="int"):
                value=int(value)
                if (titles[num_col]=="size"):
                    value=utils.formatBytes(value)
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
    for (num_col, title) in enumerate(titles):
        widths.append(len(str(title)))

    #Get the new max of each column width
    for (num_row, row) in enumerate(rows):
        for (num_col, col) in enumerate(row):
            if (len(str(row[num_col]))>widths[num_col]):
                widths[num_col]=len(str(row[num_col]))


    #Printing the table with right width
    line=""
    for (num_col, title) in enumerate(titles):
        line+=""+title.ljust(widths[num_col]+1)+" "
    printBB("[header]"+line+"[/header]")

    for (num_row, row) in enumerate(rows):
        line=""
        for (num_col, col) in enumerate(row):
            value=str(col)
            if (types[num_col]=="int"):
                line+=""+value.rjust(widths[num_col]+1," ")+" "                
            elif (types[num_col]=="float"):
                line+=""+value.rjust(widths[num_col]+1," ")+" "        
            else:
                if (value[-3:]==" GB"):
                    line+=value.rjust(widths[num_col]+1," ")+" "
                else:
                    line+=(" " if num_col>0 else "")+value.ljust(widths[num_col]+1," ")

        printBB(line)

    



# parse BB code and print it in console
def parseBB(text):
    text=re.sub(r"(\[h1\])([^\[\]]+)(\[/h1\])", "\033[32;1m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[ok\])(.+)(\[/ok\])", "\033[32;1m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[error\])([^\[\]]+)(\[/error\])", "\033[31;1m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[b\])([^\[\]]+)(\[/b\])","\033[1m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[u\])([^\[\]]+)(\[/u\])","\033[4m\\2\033[24m",text,re.IGNORECASE)
    text=re.sub(r"(\[d\])([^\[\]]+)(\[/d\])","\033[2m\\2\033[22m",text,re.IGNORECASE)
    text=re.sub(r"(\[fade\])([^\[\]]+)(\[/fade\])","\033[2m\\2\033[22m",text,re.IGNORECASE)
    text=re.sub(r"(\[warning\])([^\[\]]+)(\[/warning\])","\033[33m\\2\033[22m",text,re.IGNORECASE)
    text=re.sub(r"(\[reset\])","\033[0m\033[49m",text,re.IGNORECASE)
    text=re.sub(r"(\[reverse\])(.+)(\[/reverse\])","\033[7m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[header\])([^\[\]]+)(\[/header\])","\\033[1m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[hour\])([^\[\]]+)(\[/hour\])","\\033[48;5;255m\\2\033[0m",text,re.IGNORECASE)
    text=re.sub(r"(\[shell\])([^\[\]]+)(\[/shell\])","\\033[44;1;97m\\2\033[0m",text,re.IGNORECASE)
    return text


def printBB(text): 
    print(parseBB(text))


def printExceptionError(error):
    caller_name = inspect.stack()[1].function
    file=inspect.stack()[1].filename
    file=file[file.rfind("\\")+1:]
    printBB("[error]Exception Error on "+file+"/"+caller_name+"():[/error]");
    printBB("  [error]"+repr(error)+"[/error]")

# From this great tuto https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
def test():

    print(get_terminal_size())
    printBB("[h1]Test of ANSI escape sequences[/h1]");
    printBB("[fade]Test of ANSI escape sequences[/fade]");
    printBB("[reverse][b]Test of ANSI escape sequences[/b][/reverse]");

    for i in range(30, 37 + 1):
        print("\033[%dm%d\t\t\033[%dm%d" % (i, i, i + 60, i + 60))


