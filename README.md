# msdocsviewer
`msdocviewer` is a simple tool that parses Microsoft's win32 API and driver documentation to be used within IDA.

## Description
`msdocviewer` consists of two parts. The first is a parser (`run_me_first.py`) that searches for all markdown files in the Microsoft [sdk-api](https://github.com/MicrosoftDocs/sdk-api) and [driver](https://github.com/MicrosoftDocs/windows-driver-docs) repository, it then checks if the document is related to a function and if so, it copies the document to a directory and then renames the file with their corresponding API name. For example, the file `nf-fileapi-createfilea.md` is renamed to `CreateFileA.md`. The second part is a markdown viewer that exists within an IDA plugin (`ida_plugin/msdocviewida.py`) that displays the document in IDA. An example of the output can be seen below. 

![Example](./img/preview.png "Optional title")

`msdocviewer` is similar to the old MSDN IDA viewers but doesn't rely on browsers, network requests or extracting the documents from a Visual Studio SDK. Since Microsoft started storing their API documents in Markdown and hosting them on GitHub, all the documents can be easily downloaded by cloning a repository. This is super useful because it is easy to copy the repositories to a portable drive or have them in a VM or host that doesn't have network access. It should also make it easy to port this code to other tools (e.g. Binary Ninja, Ghidra, etc).

#### Note
 The `.git` log for the `sdk-api` and `driver` repository takes up over 2GB of space. Deleting these files or their downloaded repositories does not affect the usage of the plugin because all of the needed files are saved to the `apis_md` directory. 

### Installation 
Clone this repository. *Note: Since the repository is using submodules it might take some time to download. The Microsoft sdk-api repository is over 1GB in size.*
```
git clone https://github.com/alexander-hanel/msdocsviewer.git
```
If `sdk-api` or `windows-driver-docs` are empty, the following commands needs to be executed 
```
cd msdocviwer
git submodule update --init --recursive
```
If the above command errors, execute it again. 

Once downloaded, execute `python run_me_first.py` then wait.
```
C:\Users\yolo\Documents\repo\msdocsviewer>python run_me_first.py
STATUS: Creating API_MD directory at C:\Users\yolo\Documents\repo\msdocsviewer\apis_md
NOTE: Parsing can take sometime to complete
STATUS: Parsing sdk-api
        ERROR: title is not present: C:\Users\yolo\Documents\repo\msdocsviewer\sdk-api\sdk-api-src\content\oaidl\nn-oaidl-ierrorlog.md (likely can be ignored)
STATUS: Parsing drivers
STATUS: Finished
STATUS: If using IDA add path C:\Users\yolo\Documents\repo\msdocsviewer\apis_md to API_MD variable in idaplugin/msdocviewida.py

C:\Users\yolo\Documents\repo\msdocsviewer>
```
Edit `ida_plugin/msdocviewida.py` and add the directory path of `apis_md` to the `API_MD` variable (currently on line 18). Then copy `msdocviewida.py` to the `IDA` plugin directory. The following idapython command can be executed to find the plugin directory path. 

```
Python>import ida_diskio
Python>ida_diskio.get_user_idadir()
'C:\\Users\\yolo\\AppData\\Roaming\\Hex-Rays\\IDA Pro'
```
If a directory named `plugins` is not present, it needs to be created. 

### Requirements 
`pyaml` - strangely the yaml data can also be parsed as a markdown table   

### TODO 
* Port the plugin to Binary Ninja
