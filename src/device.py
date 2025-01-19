import psutil
import cpuinfo
import traceback
import timeit
import platform
import os
from src import utils

# Get the size of the file
def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return 0

# Get hardware informations about the device (CPU, RAM, GPU)
def get_device_info():
    start_time0 = timeit.default_timer()

    start_time = timeit.default_timer()
    gpus=None
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()

        gpu_info = [{'id': gpu.id, 
                    'uuid': gpu.uuid, 
                    'name': gpu.name, 
                    'serial': gpu.serial, 
                    'temperature': gpu.temperature, 
                    'load': gpu.load, 
                    'memoryTotal':gpu.memoryTotal if gpu.memoryTotal>1000000 else gpu.memoryTotal*1024*1024, 
                    'memoryUtil': gpu.memoryUtil if gpu.memoryUtil>1000000 else gpu.memoryUtil*1024*1024,
                    'memoryUsed': gpu.memoryUsed if gpu.memoryUsed>1000000 else gpu.memoryUsed*1024*1024,
                    'memoryFree': gpu.memoryFree if gpu.memoryFree>1000000 else gpu.memoryFree*1024*1024,
                    'display_mode': gpu.display_mode,
                    'display_active': gpu.display_active
                    } 
                    for gpu in gpus]
        if len(gpu_info)==0:
            gpu_info=None
    except Exception as e:
        print("Error get_device_info():", e)
        print("[b]Error get_device_info():[/b]", e)
        print("[b]Try to update your install with this command:\n pip install -U pip setuptools wheel[/b]")
        gpu_info = None


    end_time = timeit.default_timer()
    #print(f"Execution time GPUtil.getGPUs(): {end_time - start_time} seconds")

    try:
        cpu_util = psutil.cpu_freq()
        end_time = timeit.default_timer()
        #print(f"Execution time psutil.cpu_freq(): {end_time - start_time0} seconds")
        #print(f"CPU Util: {cpu_util}")
        
        start_time = timeit.default_timer()
        cpu_name = cpuinfo.get_cpu_info()
        end_time = timeit.default_timer()
        #print(f"Execution time cpuinfo.get_cpu_info(): {end_time - start_time} seconds")
        #print(f"CPU name: {cpu_name}")
        
        start_time = timeit.default_timer()
        ram_info = psutil.virtual_memory()
        end_time = timeit.default_timer()
        #print(f"Execution time psutil.virtual_memory(): {end_time - start_time} seconds")
        #print(f"RAM: {ram_info}")
             

        start_time = timeit.default_timer()
        hdd_info = psutil.disk_usage('/')
        end_time = timeit.default_timer()
        #print(f"Execution time psutil.disk_usage(): {end_time - start_time} seconds")
        #print(f"HDD: {hdd_info}")

        cpu_freq=0
        cpu_freq_max=0
        cpu_name_text=""
        l3_cache_size=0
        ram_installed=0
        ram_available=0
        os_version=""
        cpu_max_freq=0



        os_name=platform.system()
        cpu_brand=cpu_name.get("vendor_id_raw")
        os="Linux"

        os_detail=platform.platform()
        if (os_detail.upper().startswith("MACOS")):
            cpu_brand="Apple"
            versions=os_detail.split("-")
            os_version=versions[1]
            os="Mac"
            os_name="macOS "+os_name+" "+os_version
            cpu_freq = cpu_name.get("hz_advertised", cpu_util.max)
            cpu_freq_max=cpu_name.get("hz_advertised", cpu_util.max)
            if (cpu_freq<10000):
                cpu_freq=cpu_freq*1e6
                cpu_freq_max=cpu_freq_max*1e6

            cpu_name_text=cpu_name.get("brand_raw")
            l3_cache_size=cpu_name.get("l3_cache_size", 0)
            ram_available=ram_info.available
            ram_installed=ram_info.total            

        if (os_name=="Windows"):
            os="Windows"
            versions=os_detail.split("-")
            os_version=versions[1]
            if os_version=="10":
                build=os_detail[os_detail.rfind(".")+1:]
                if (build>="22000"):
                    os_version="11"
            cpu_brand= cpu_name.get("vendor_id_raw")
            cpu_freq= cpu_name.get("hz_advertised")[0]
            cpu_freq_max= cpu_name.get("hz_advertised")[0]
            l3_cache_size= cpu_name.get("l3_cache_size")
            ram_installed= ram_info[0]
            ram_available= ram_info[1]
            cpu_name_text= cpu_name.get("brand_raw")

        cpu_name_text=cpu_name_text.replace("Processor","").strip()

        import socket
        hostname = socket.gethostname()

        device = {
            "detected": True,
            "raw": {
                "cpu_util": cpu_util,
                "cpu_name": cpu_name,
                "ram_info": ram_info,
                "gpus": gpu_info,
                "hdd_info": hdd_info
            },
            
            "cpu_brand": cpu_brand,
            "cpu_name": cpu_name_text,
            "cpu_freq": cpu_freq,
            "cpu_threads": cpu_name.get("count"),
            "cpu_max_freq": cpu_freq_max,
            "l3_cache_size": l3_cache_size,
            "cpu_arch": cpu_name.get("arch"),
            "ram_info": ram_info,
            "ram_installed": ram_installed,
            "ram_available": ram_available,
            "hdd_total": hdd_info.total,
            "hdd_used": hdd_info.used,
            "hdd_free": hdd_info.free,
            "gpus": gpu_info,
            "getDeviceInfoTime": end_time - start_time0,
            "os": os,
            "os_name": os_name,
            "os_version": os_version,
            "os_details": platform.platform(),
            "hostname": hostname,
            "description": ""
        }


        try:
            device["description"] = f"""CPU: {device.get("cpu_name")} - {utils.formatFrequencies(cpu_freq)} {device.get("cpu_threads")} threads 
            RAM: {utils.formatBytes(round(ram_installed), 0)}
            HDD: Total: {utils.formatBytes(device.get("hdd_total"))} Free: {utils.formatBytes(device.get("hdd_free"))}\n"""
        except:
            traceback.print_exc()

            device["description"] = f"""CPU: {device.get("cpu_name")}""" 

        if gpu_info is None:
            device["description"] = f" No GPU found"
        else:
            gpu=device.get("gpus")[0]
            device["description"] += f""" GPU: {gpu.get("name")} ({gpu.get("memoryTotal")/1024} GB)"""

        device["description"] += f"""\n OS: {device.get("os_name")} {device.get("os_version")}"""


    except Exception as e:
        traceback.print_exc()
        device = {
            "detected": False,
            "raw": {
                "cpu_util": "",
                "cpu_name": "",
                "ram_info": "",
                "gpus": gpu_info,
                "hdd_info": ""
            },
            "cpu_brand": "",
            "cpu_name": "",
            "cpu_freq": "",
            "cpu_threads": "",
            "cpu_max_freq": "",
            "l3_cache_size": "",
            "cpu_arch": "",
            "ram_installed": "",
            "hdd_total": "",
            "hdd_used": "",
            "hdd_free": "",
            "gpus": gpu_info,
            "getDeviceInfoTime": 0,
            "os": os,
            "os_name": platform.system(),
            "os_version": platform.release(),
            "os_details": platform.platform(),
            "hostname": "",
            "description": "Hardware not detected"
        }


    return device


