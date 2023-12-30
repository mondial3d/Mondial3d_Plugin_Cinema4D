import os
import tempfile
import fnmatch
from urllib import request, error
import json
import subprocess
import c4d
from c4d import gui

auth_token=""
user_email=""
temp_dir = tempfile.gettempdir()

def send_request(url, headers):
    try:
        req = request.Request(url, headers=headers)
        response = request.urlopen(req)
        data= response.read().decode()
        return json.loads(data)

    except error.HTTPError as e:
        return f"HTTP Error: {e.code}. Message: {e.reason}"
    except error.URLError as e:
        return f"URL Error. Reason: {e.reason}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

class Dialogs:
    def __init__(self):
        self.dialogs = []

    def add(self, dialog):
        self.dialogs.append(dialog)

dialogs = Dialogs()

class Authentication(gui.GeDialog):
    HEADER= 999
    LOGIN_BUTTON= 1000
    SIGNUP_BUTTON= 1001
    AUTH_TOKEN= 1002

    def CreateLayout(self):
        self.SetTitle("Mondial3d.com")
        self.GroupBorderSpace(10, 10, 10, 10)

        self.AddStaticText(self.HEADER, flags= c4d.BFV_CENTER, name="Welcome to Mondial3d.com",borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.AddStaticText(self.HEADER, flags= c4d.BFV_CENTER, name="")
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        
        self.AddEditText(self.AUTH_TOKEN, flags= c4d.BFH_SCALEFIT, initw=200)
        self.SetString(self.AUTH_TOKEN, "Authentication Token")

        self.GroupBegin(id=10000, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=2, rows=1)
        self.AddButton(self.LOGIN_BUTTON, flags=c4d.BFH_SCALEFIT, name="Login")
        self.AddButton(self.SIGNUP_BUTTON, flags=c4d.BFH_SCALEFIT, name="Sign Up")
        self.GroupEnd()
        
        return True

    def checkAuthentication(self, token):
        base_url = "https://api.mondial3d.studio/api/Nft/GetProfile"
        headers = {"Authorization" : "Bearer "+ token}
        response = send_request(base_url, headers)
        if isinstance(response, str) and (response.startswith("HTTP Error") or response.startswith("URL Error") or response.startswith("An error occurred")):
            c4d.gui.MessageDialog(response)
            return None
        else:
            return response

    def Command(self, id, msg):
        global auth_token, user_email
        if id == self.LOGIN_BUTTON:
            token= self.GetString(self.AUTH_TOKEN)
            if "Authentication Token" in token:
                c4d.gui.MessageDialog("Please Enter Your Authentication token.")
                return False
            else: 
                response=self.checkAuthentication(token)
                if response is not None and isinstance(response, dict):
                    try:
                        auth_token= token
                        user_email = response["email"]
                        
                        self.Close()
                        mondial_dialog = Mondial()
                        mondial_dialog.Open(dlgtype= c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=450, xpos=300, ypos= 300)
                        dialogs.add(mondial_dialog)

                    except json.JSONDecodeError:
                        c4d.gui.MessageDialog("Invalid JSON received from server.")
                return True
        elif id== self.SIGNUP_BUTTON:
            c4d.storage.GeExecuteFile('http://www.mondial3d.com')
            return True

    def DestroyDialog(self):
        self.DestroyWindow()
        return True

class Mondial(gui.GeDialog):
    HEADER= 999
    SIGNOUT_BUTTON= 1000
    AI_HEADER= 1001
    AI_PROMPT= 1002
    AI_BUTTTON= 1003
    AI_DOWNLOAD_BUTTON= 1004
    AI_LOAD= False
    AI_LABEL= []
    AI_LINK= ""

    def CreateLayout(self):
        self.SetTitle("Mondial3d.com")
        self.GroupBorderSpace(10, 10, 10, 10)

        # Signout
        self.GroupBegin(id=10000, flags=c4d.BFH_SCALEFIT, cols=2, rows=1)
        self.AddStaticText(self.HEADER, flags=c4d.BFH_CENTER, name=user_email)  # Assuming user_email is defined somewhere
        self.AddButton(self.SIGNOUT_BUTTON, flags=c4d.BFH_SCALEFIT, name="Sign out")
        self.GroupEnd()
        self.AddSeparatorH(c4d.BFH_SCALEFIT)

        # AI Prompt Scene
        self.AddStaticText(self.AI_HEADER, flags=c4d.BFH_CENTER, name="AI", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        # Input
        self.GroupBegin(id=10001, flags=c4d.BFH_SCALEFIT, cols=2, rows=1)
        self.AddEditText(self.AI_PROMPT, flags= c4d.BFH_SCALEFIT, initw=200)
        self.SetString(self.AI_PROMPT, "Write your 3D prompt")
        self.AddButton(self.AI_BUTTTON, flags=c4d.BFH_RIGHT, name="Imagine")
        self.GroupEnd()
        # Labels
        self.GroupBegin(id=10002, flags=c4d.BFH_SCALEFIT, cols=1, rows=1)
        self.GroupEnd()
        self.AddSeparatorH(c4d.BFH_SCALEFIT)

        return True
    
    def AIPromptScene(self, prompt):
        base_url=f"https://api.mondial3d.studio/api/Nft/ai-Add-complete-scene?categoryName={prompt}"
        headers = {"Authorization" : "Bearer "+ auth_token}
        response = send_request(base_url, headers)
        if isinstance(response, str) and (response.startswith("HTTP Error") or response.startswith("URL Error") or response.startswith("An error occurred")):
            c4d.gui.MessageDialog(response)
            return None
        else:
            return response

    def DownloadGLB(self, link):
        try:
            # Download the .glb file
            response = request.urlopen(link)
            save_path = os.path.join(temp_dir, "ai.glb")
            with open(save_path, 'wb') as f:
                f.write(response.read())

            return save_path
        
        except Exception as e:
            c4d.gui.MessageDialog(str(e))
            return None

    def FindBlenderPath(self, pattern='blender.exe', path='C:\\'):
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    blender_path = os.path.join(root, name)
                    return blender_path.replace("\\", "/")


    def Command(self, id, msg):
        global auth_token
        if id == self.SIGNOUT_BUTTON:
            for dialog in dialogs.dialogs:
                dialog.Close()
            dialogs.dialogs.clear()
            auth_token = ""
            auth = Authentication()
            auth.Open(dlgtype=c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=450, xpos=300, ypos= 300)
            dialogs.add(auth)

            return True

        elif id == self.AI_BUTTTON:
            prompt = self.GetString(self.AI_PROMPT)
            if "Write your 3D prompt" in prompt:
                c4d.gui.MessageDialog("Please write your 3D Prompt")
                return False
            else:
                prompt = prompt.replace(" ", "_")
                response = self.AIPromptScene(prompt)

                response = response["completeScene"]
                label = response["labels"]
                self.AI_LABEL = label.split(",")
                self.AI_LINK = response["fileLink"]
                self.AI_LOAD = True

                self.LayoutFlushGroup(10002)  
                for i in range(5):
                    self.AddStaticText(i, flags=c4d.BFH_SCALEFIT, name=self.AI_LABEL[i])
                self.AddButton(self.AI_DOWNLOAD_BUTTON, flags=c4d.BFH_SCALEFIT, name="Import Scene")
                self.LayoutChanged(10002)
                return True

        elif id == self.AI_DOWNLOAD_BUTTON:
            glb_save_path= self.DownloadGLB(self.AI_LINK)

            script_path = os.path.join(os.getcwd(), "ConvertGLBtoFBX.py")
            script_path= script_path.replace("\\", "/")
            print(script_path)

            blender_path= self.FindBlenderPath()

            cmd = [
                f'"{blender_path}"', 
                '--background', 
                '--python', 
                f'"{script_path}"', 
                f'"{glb_save_path}"'
            ]
            try:
                result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(result.stdout.decode('utf-8'))
                return True
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while converting .glb to .fbx: {str(e)}")
                print(e.stderr.decode('utf-8'))

    def DestroyDialog(self):
        self.DestroyWindow()
        return True

def main() -> None:
    auth = Authentication()
    auth.Open(dlgtype=c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=450, xpos=300, ypos= 300)
    dialogs.add(auth)



if __name__ == '__main__':
    main()
