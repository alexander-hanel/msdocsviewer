"""
Author: Alexander Hanel
Version: 1.0
Purpose: index the sdk-api and driver directory to parse yaml/mardown data and rename files to the api name
Requirements: pyyaml
Updates:
    * Version 1.0 Release
"""
import yaml 
import glob 
import os

SDK_API_DIR = "sdk-api"
SDK_DOCS_DIR = "sdk-api-src\\content"
NEW_API_DIR = "apis_md"

DRIVER_SDK_API_DIR = "windows-driver-docs"
DRIVER_SDK_DOCS_DIR = "windows-driver-docs-pr"

# The data for identifying functions is not consistent so this removes some fps. 
IGNORE = ["Write.md", "WinUSB.md", "WIA.md", "WFP.md", "USB.md", "Universal.md", "UFX.md", "UEFI.md",
            "Testing.md", "Serial.md", "Root.md", "Querying.md", "Port.md", "Overview.md", "Native.md",
            "Can.md", "Calling.md", "Call.md", "Bring.md", "Battery.md", "AddTarget.md", "AddPoint.md",
            "AddLink.md", "Access.md", "IRP.md", "How.md", "Internet.md", "IPsec.md", "Language.md"]


def parse_and_copy(file_path):
    try:
        # there are a lot of encoding errors with the sdk-api docs
        with open(file_path, "r", errors = "ignore") as infile:
            data = infile.read()
    except Exception as e:
        print("\tERROR: can not access file: ", file_path, e)
        return None
    # the api docs start with a yaml and then markdown seperated by "---"
    try:
        data_split = data.split("---")
        yaml_data = yaml.safe_load(data_split[1])
    except:
        return None
    if "title" not in yaml_data:
        print("\tERROR: title is not present: %s (likely can be ignored)" %  file_path)
        return None
    if " function" not in yaml_data["title"]:
        return None
    # get api name 
    function_name = yaml_data["title"].split(" ")[0]
    if not function_name:
        return None 
    function_name = function_name.replace("\\", "")
    if function_name + ".md" in IGNORE:
        return None 
    api_path = os.path.join(NEW_API_DIR, function_name + ".md" )
    with open(api_path, "w") as api_file:
        api_file.write(data_split[2])
        api_file.write(" \n```")
        api_file.write(data_split[1])
        api_file.write("```\n")
    return  

def main():
    # parse api sdk 
    if not os.path.isdir(SDK_API_DIR):
        print("\tERROR: sdk-api directory could not be found")
        print("\tMaybe try: git submodule update --recursive")
        return 
    full_path = os.path.join(os.path.abspath(SDK_API_DIR), SDK_DOCS_DIR)
    # skip paths that start with an underscore _ 
    os.makedirs(NEW_API_DIR)
    print("STATUS: Creating API_MD directory at %s" % os.path.abspath(NEW_API_DIR))
    print("NOTE: Parsing can take sometime to complete ")
    print("STATUS: Parsing sdk-api") 
    for dir_path in glob.glob(full_path + "/[!_]*"):
        for md_path in glob.glob(dir_path + "/*"):
            if not md_path.endswith(".md"):
                continue 
            parse_and_copy(md_path)
    # parse driver api sdk 
    if not os.path.isdir(DRIVER_SDK_API_DIR):
        print("\tERROR: windows-driver-docs could not be found")
        print("\tMaybe try: git submodule update --recursive")
        return 
    print("STATUS: Parsing drivers")
    full_path = os.path.join(os.path.abspath(DRIVER_SDK_API_DIR), DRIVER_SDK_DOCS_DIR)
    # skip paths that start with an underscore _ 
    for dir_path in glob.glob(full_path + "/[!_]*"):
        for md_path in glob.glob(dir_path + "/*"):
            if not md_path.endswith(".md"):
                continue 
            parse_and_copy(md_path)
    print("STATUS: Finished") 
    print("STATUS: If using IDA add path %s to API_MD variable in idaplugin/msdocviewida.py" % os.path.abspath(NEW_API_DIR))
    
main()

