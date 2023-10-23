"""
Author: Alexander Hanel
Version: 1.0
Purpose: Microsoft Document (sdk-api & Driver) document viewer for IDA. 
Updates:
    * Version 1.0 Release
"""

import os
import ida_kernwin
import ida_idaapi
import ida_name

from idaapi import PluginForm
from PyQt5 import QtWidgets

# Path to the Markdown docs. Folder should start with 
API_MD = r"c:\\Users\\alexa\\Documents\\repo\\msdocsviewer\\apis_md"

# global variables used to track initialization/creation of the forms.  
started = False
frm = None 

def get_selected_api_name():
    """
    get selected item and extract function name from it 
    via https://github.com/idapython/src/blob/e1c108a7df4b5d80d14d8b0c14ae73b924bff6f4/Scripts/msdnapihelp.py#L48
    return: api name as string 
    """
    try:
        v = ida_kernwin.get_current_viewer()
        name, ok = ida_kernwin.get_highlight(v)
        if not ok:
            # print("No identifier was highlighted")
            return None 
        t = ida_name.FUNC_IMPORT_PREFIX
        if name.startswith(t):
            return name[len(t):]
        return name
    except:
        return None 

class MSDN(PluginForm):
    def OnCreate(self, form):
        """
        defines widget layout 
        """
        self.parent = self.FormToPyQtWidget(form)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.markdown_viewer_label = QtWidgets.QLabel()
        self.markdown_viewer_label.setText("API MSDN Docs")
        self.markdown_viewer = QtWidgets.QTextEdit()
        self.markdown_viewer.setReadOnly(True)
        self.main_layout.addWidget(self.markdown_viewer)
        self.parent.setLayout(self.main_layout)
        self.load_markdown()

    def load_markdown(self):
        """
        gets api and load corresponding (if present) api markdown 
        """
        api_name = get_selected_api_name()
        if not api_name:
            api_markdown ="#### Invalid Address Selected"
            self.markdown_viewer.setMarkdown(api_markdown)
            return
        md_path = os.path.join(API_MD, api_name + ".md" )
        if os.path.isfile(md_path):
            with open(md_path, "r") as infile:
                api_markdown = infile.read()
        else:
                api_markdown ="#### docs for %s could not be found" % api_name
        self.markdown_viewer.setMarkdown(api_markdown)

    def OnClose(self, form):
        """
        Called when the widget is closed
        """
        del frm

class MSDNPlugin(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_MOD
    comment = "API MSDN Docs"
    help = ""
    wanted_name = "API MSDN Docs"
    wanted_hotkey = "Ctrl-Shift-Z"

    def init(self):
        self.options = (ida_kernwin.PluginForm.WOPN_MENU |
            ida_kernwin.PluginForm.WOPN_ONTOP |
            ida_kernwin.PluginForm.WOPN_RESTORE |
            ida_kernwin.PluginForm.WOPN_PERSIST |
            ida_kernwin.PluginForm.WCLS_CLOSE_LATER)
        return ida_idaapi.PLUGIN_KEEP

    def run(self, arg):
        global started
        global frm  
        if not started:
            #API_MD
            if not os.path.isdir(API_MD):
                print("ERROR: API_MD directory could not be found. Make sure to execute python run_me_first.py ")
            frm = MSDN()
            frm.Show("MSDN API Docs: hotkey: Ctrl-Shift-Z", options=self.options)
            started = True
        else:
            frm.load_markdown()
        
    def term(self):
        pass

# -----------------------------------------------------------------------
def PLUGIN_ENTRY():
    return MSDNPlugin()
