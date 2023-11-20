"""
Author: Alexander Hanel
Purpose: index the sdk-api and driver directory to parse yaml/mardown data and rename files to the api name
Requirements: pyyaml
Updates:
    * Version 1.0 Release
    * Version 1.1 Updated driver repo, added error handling for parsing  
    * Version 2.0  
        - fixed Python path slash #6 found by phdphuc
        - fixed [Bug] Incorrect md parsing logic #5 found by FuzzySecurity 
        - added debug logging to see parsed files as mentioned in issue #6 by phdphuc
        - added command line arguments 
        - added option to overwrite and regenerate api doc directory 
        - added functionality to flag functions that might have not been parsed correctly
        - replaced print output with logging.INFO

"""

import yaml 
import argparse
import glob 
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

SDK_API_DIR = "sdk-api"
SDK_DOCS_DIR = "sdk-api-src"
DRIVER_SDK_API_DIR = "windows-driver-docs-ddi"
DRIVER_SDK_DOCS_DIR = "wdk-ddi-src"
CONTENT_DIR = "content"
NEW_API_DIR = "apis_md"

# The data for identifying functions is not consistent so this removes some fps. 
IGNORE = ["Write.md", "WinUSB.md", "WIA.md", "WFP.md", "USB.md", "Universal.md", "UFX.md", "UEFI.md",
            "Testing.md", "Serial.md", "Root.md", "Querying.md", "Port.md", "Overview.md", "Native.md",
            "Can.md", "Calling.md", "Call.md", "Bring.md", "Battery.md", "AddTarget.md", "AddPoint.md",
            "AddLink.md", "Access.md", "IRP.md", "How.md", "Internet.md", "IPsec.md", "Language.md"]
SKIP_CHARs = ["+", "=", "()", "!" , "::" ] 

def percentage(part, whole):
    return 100 * float(part)/float(whole)

def parse_and_copy(file_path, debug_logging):
    try:
        # there are a lot of encoding errors with the sdk-api docs
        with open(file_path, "r", errors = "ignore") as infile:
            data = infile.read()
    except Exception as e:
        if debug_logging:
            debug_logging.debug("could not access file %s, %s" % (file_path, e))
        return None
    # the api docs start with a yaml and then markdown seperated by "---"
    data_len = len(data )
    try:
        data_split = data.split("---")
        yaml_data = yaml.safe_load(data_split[1])
    except Exception as e:
        if debug_logging:
            debug_logging.debug("yaml load issue on %s, %s"  % (file_path, e))
        return None
    if "title" not in yaml_data:
        if debug_logging:
            debug_logging.debug("title is not present in %s" % (file_path))
        return None
    if " function" not in yaml_data["title"]:
        if debug_logging:
            debug_logging.debug("function is not present in %s" % (file_path))
        return None
    # get api name 
    function_name = yaml_data["title"].split(" ")[0]
    if not function_name:
        if debug_logging:
            debug_logging.debug("api name was not found in %s"  % (file_path))
        return None 
    function_name = function_name.replace("\\", "")
    if function_name + ".md" in IGNORE:
        if debug_logging:
            debug_logging.debug("function name %s in ignore list in %s" % (function_name, file_path))
        return None 
    if any([x in function_name for x in SKIP_CHARs]):
        if debug_logging:
            debug_logging.debug("invalid function name %s in %s"  % (function_name, file_path))
        return None 
    api_path = os.path.join(NEW_API_DIR, function_name + ".md" )
    api_file_len = None
    try:
        with open(api_path, "w") as api_file:
            api_file.write("---".join(data_split[2:]))
            api_file.write(" " + os.linesep + "```")
            api_file.write(data_split[1])
            api_file.write("```" + os.linesep)
            api_file.seek(0, os.SEEK_END)
            api_file_len = api_file.tell() 
    except Exception as e:
        if debug_logging:
            debug_logging.debug("file creation of %s to %s exception %s" % (function_name, api_path, e))
        return None 
    if percentage(api_file_len, data_len) < 85.0:
        if debug_logging:
            debug_logging.debug("likely parsing issue with %s and %s" % (file_path, api_path))
    return  
    

def main():
    runmefirst = argparse.ArgumentParser(description="msdocviewer parser component") 
    runmefirst.add_argument("-l", "--log", action="store_true", default=False, help="Log all parsing errors to debug-parser.log")
    runmefirst.add_argument("-o", "--overwrite", action="store_true", default=False, help="overwrite apis_md directory")

    args = runmefirst.parse_args()
    debug_logging = None 
    if args.log:
        debug_logging = logging.getLogger('debug_logger')
        debug_logging.setLevel(logging.DEBUG)
        # disable stdout 
        debug_logging.propagate = False
        fh = logging.FileHandler('debug-parser.log')
        fh.setLevel(logging.DEBUG)
        debug_logging.addHandler(fh)
        
    if os.path.isdir(NEW_API_DIR):
        if args.overwrite:
            logging.info("deleting and overwriting %s directory" % NEW_API_DIR)
            import shutil
            shutil.rmtree(NEW_API_DIR) 
        else:
            logging.error("The directory %s is already present. Please use --overwrite to overwrite it" % NEW_API_DIR)
            return 

    logging.info("creating %s directory at %s" % (NEW_API_DIR, os.path.abspath(NEW_API_DIR)))
    os.makedirs(NEW_API_DIR)
    logging.info("starting the parsing, this can take a few minutes")
   
    if not os.path.isdir(SDK_API_DIR):
        logging.info("sdk-api directory could not be found")
        logging.info("try: git submodule update --recursive")
        logging.info("skipping sdk-api")    
    else: 
        # construct sdk path 
        full_sdk_path = os.path.join(os.path.abspath(SDK_API_DIR), SDK_DOCS_DIR, CONTENT_DIR)
        # parse sdk-api directory 
        logging.info("parsing %s" % full_sdk_path)
        # skip paths that start with an underscore _ 
        for dir_path in glob.glob(full_sdk_path + "/[!_]*"):
            for md_path in glob.glob(dir_path + "/*"):
                if not md_path.endswith(".md"):
                    continue 
                parse_and_copy(md_path, debug_logging)
        logging.info("parsing %s completed" % full_sdk_path)
    
    if not os.path.isdir(DRIVER_SDK_API_DIR):
        logging.info("windows-driver-docs directory could not be found")
        logging.info("try: git submodule update --recursive")
        logging.info("skipping sdk-api")    
    else:
        full_ddk_path = os.path.join(os.path.abspath(DRIVER_SDK_API_DIR), DRIVER_SDK_DOCS_DIR, CONTENT_DIR) 
        logging.info("parsing %s" % full_ddk_path)
        # skip paths that start with an underscore _ 
        for dir_path in glob.glob(full_ddk_path + "/[!_]*"):
            for md_path in glob.glob(dir_path + "/*"):
                if not md_path.endswith(".md"):
                    continue 
                parse_and_copy(md_path, debug_logging)  
        logging.info("parsing %s completed" % full_ddk_path)
    logging.info("finished parsing, if using IDA add path %s to API_MD variable in idaplugin/msdocviewida.py" % os.path.abspath(NEW_API_DIR))


if __name__ == "__main__":
    main()

