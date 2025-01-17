# Python Console Module that allows to print BB code in terminal 
# Pimp your terminal with colors 
#  @toutjavascript  https://github.com/toutjavascript
#  V1 : 2025


import re
import inspect
import sys
import platform
import os
from datetime import datetime

#Init functions for BB code printing in terminal on Windows
if platform.system() == 'Windows':
    # Windows-specific handling
    os.system('color')


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

# Dynamic terminal display
def print_line(text):
    """Print the text in the terminal. The line can be deleted by the clear_line() function."""
    sys.stdout.write(parseBB(text))
    sys.stdout.flush()

def clear_line():
    """Clear the terminal line. The line can be printed again by the print_line() function."""
    sys.stdout.write('\u001b[2K')  # Clear the entire line
    sys.stdout.write('\u001b[0G')  # Move the cursor to the beginning of the line
    sys.stdout.flush()


def console(txt: str, display_time: bool = True) -> None:
    """
    Print text in the terminal with formatting
    Args:
        txt (str): text to display
        display_time (bool): whether to display the current time before the text
    """
    from rich.console import Console
    import datetime
    console = Console()
    if display_time:
        now = datetime.datetime.now()
        time = "[fade]" + now.strftime("%H:%M:%S.%f")[:-3] + "[/fade]  "  # Include milliseconds and trim to 3 digits
    else:
        time=""
    print(parseBB(f"{time}{txt}"))


def get_value_type(obj):
    return str(type(obj)).replace("<class '", "").replace("'>", "")

def table(my_array, ignore_columns=None, align_right_columns=None):
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
            if title in ignore_columns:
                continue

            if (num_row==0):
                titles.append(title)
                types.append(get_value_type(value))
            
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
                elif (value.strip()=="0 k"):
                    line+=(" " if num_col>0 else "")+"[fade]"+value.ljust(widths[num_col]+1," ")+"[/fade]"
                else:  
                    if (titles[num_col] in align_right_columns):
                        line+=(" " if num_col>0 else "")+value.rjust(widths[num_col]," ")+" "
                    else:                  
                        line+=(" " if num_col>0 else "")+value.ljust(widths[num_col]+1," ")

        printBB(line)

    



def parseBB(text):
    """Parse BB code into ASCII colored plain text."""
    text=re.sub(r"(\[h1\])(.+)(\[/h1\])", "\u001b[32;1m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[ok\])(.+)(\[/ok\])", "\u001b[32;1m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[green\])(.+)(\[/green\])", "\u001b[32m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[size\])(.+)(\[/size\])", "\u001b[95m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[error\])(.+)(\[/error\])", "\u001b[31;1m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[b\])([^\[\]]+)(\[/b\])", "\u001b[1m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[url\])(.+)(\[/url\])", "\u001b[4m\\2\u001b[24m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[file\])(.+)(\[/file\])", "\u001b[4m\\2\u001b[24m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[u\])(.+)(\[/u\])", "\u001b[4m\\2\u001b[24m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[d\])(.+)(\[/d\])", "\u001b[2m\\2\u001b[22m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[fade\])(.+)(\[/fade\])", "\u001b[2m\\2\u001b[22m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[warning\])(.+)(\[/warning\])", "\u001b[33m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[reset\])", "\u001b[0m\u001b[49m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[reverse\])(.+)(\[/reverse\])", "\u001b[7m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[header\])(.+)(\[/header\])", "\u001b[1m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[hour\])(.+)(\[/hour\])", "\u001b[48;5;255m\\2\u001b[0m", text, flags=re.IGNORECASE)
    text=re.sub(r"(\[shell\])(.+)(\[/shell\])", "\u001b[44;1;97m\\2\u001b[0m", text, flags=re.IGNORECASE)
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

    print(get_now_as_iso())
    print(get_date_diff("2024-12-10", get_now_as_iso()))

    print(get_terminal_size())
    printBB("[h1]Test of ANSI escape sequences[/h1]");
    printBB("[fade]Test of ANSI escape sequences[/fade]");
    printBB("[reverse][b]Test of ANSI escape sequences[/b][/reverse]");

    for i in range(30, 37 + 1):
        print("\u001b[%dm%d\t\t\u001b[%dm%d" % (i, i, i + 60, i + 60))


if __name__ == "__main__":
    test()