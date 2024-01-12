import os
import tempfile
import fnmatch
from urllib import request, error
from urllib.request import Request, urlopen
import json
import subprocess
import base64
import mimetypes
import c4d
from c4d import gui, documents, plugins, bitmaps

PLUGIN_ID = 1000001

class MyPlugin(c4d.plugins.CommandData):
    def __init__(self):
        self.dialogs = []

    def Register(self):
        return plugins.RegisterCommandPlugin(PLUGIN_ID, "Mondial3d.com", 0, None, "Author: Amirsaleh Naderzadeh Mehrabani", self)

    def Execute(self, doc):
        auth = Authentication()
        auth.Open(dlgtype=c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=450, xpos=300, ypos= 300)
        self.dialogs.append(auth)
        return True

auth_token=""
user_email=""
temp_dir = tempfile.gettempdir()

def send_request(url, headers=None):
    try:
        if headers and len(headers) > 0:
            req = request.Request(url, headers=headers)
        else:
            req = request.Request(url)

        response = request.urlopen(req)
        data= response.read().decode()

        if data:
            return json.loads(data)
        else:
            return "Received empty response"

    except json.JSONDecodeError as e:
        return f"JSON Decode Error: {str(e)}"
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
    
    def __init__(self):
        self.HEADER= 999
        self.LOGIN_BUTTON= 1000
        self.SIGNUP_BUTTON= 1001
        self.AUTH_TOKEN= 1002

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
                        mondial_dialog.Open(dlgtype= c4d.DLG_TYPE_ASYNC, defaultw=300, defaulth=450, xpos=-0, ypos= -0)
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

class MyUserArea(c4d.gui.GeUserArea):
    def __init__(self, image_path):
        super(MyUserArea, self).__init__()
        self.user_areas = []
        self.image = c4d.bitmaps.BaseBitmap()
        result, is_movie = self.image.InitWith(image_path)

        if result != c4d.IMAGERESULT_OK:
            c4d.gui.MessageDialog("Could not load image: " + image_path)
            return False
        else:
            resized_bmp = c4d.bitmaps.BaseBitmap()
            resized_bmp.Init(120, 120)
            self.image.ScaleIt(resized_bmp, 256, 120, c4d.INITBITMAPFLAGS_0)
            self.image = resized_bmp

    def GetMinSize(self):
        width, height = self.image.GetSize()
        return (width, height)

    def DrawMsg(self, x1, y1, x2, y2, msg):
        width, height = self.image.GetSize()
        self.DrawBitmap(self.image, 0, 0, width, height, 0, 0, width, height, c4d.BMP_NORMAL)

class Mondial(gui.GeDialog):

    def __init__(self):
        self.HEADER= 999
        self.SIGNOUT_BUTTON= 1000

        self.AI_HEADER= 1001
        self.AI_PROMPT= 1002
        self.AI_BUTTTON= 1003
        self.AI_DOWNLOAD_BUTTON= 1004
        self.AI_LOAD= False
        self.AI_LABEL= []
        self.AI_LINK= ""
        
        self.MARKETPLACE= 1005
        self.MARKETPLACE_ACTIVATE= 1006
        self.MARKETPLACE_NEXT=1007
        self.MARKETPLACE_PREVIOUS=1008
        self.MARKETPLACE_SEARCH= 1009
        self.MARKETPLACE_SEARCH_SUBMIT= 1010
        self.PAGEID= 2
        self.user_areas = []
        self.marketplace_model_url=[]
        self.search_labels=[]
        self.search_label= ""

        self.PUBLISH_HEADER= 1011
        self.PUBLISH_SUBMIT= 1012

        self.MY_PROJECT_HEADER= 1013
        self.MY_PROJECT_ACTIVATE= 1014  
        self.my_project_area= []
        self.my_project_url=[]

    def CreateLayout(self):
        self.SetTitle("Mondial3d.com")
        self.GroupBorderSpace(10, 10, 10, 10)
        self.AddStaticText(998, flags=c4d.BFH_CENTER, name="Mondial3d.com", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.AddStaticText(998, flags=c4d.BFH_CENTER, name="")

        # Signout
        self.GroupBegin(id=10000, flags=c4d.BFH_SCALEFIT, cols=2, rows=1)
        self.AddStaticText(self.HEADER, flags=c4d.BFH_CENTER, name=user_email)
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

        # Marketplace
        self.AddStaticText(self.MARKETPLACE, flags=c4d.BFH_CENTER, name="Marketplace", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.GroupBegin(id=10003, flags=c4d.BFH_SCALEFIT, cols=1, rows=1)
        self.AddButton(self.MARKETPLACE_ACTIVATE, flags=c4d.BFH_SCALEFIT, name="Activate Marketplace")
        self.GroupEnd()
        self.AddSeparatorH(c4d.BFH_SCALEFIT)

        # Publish to Server
        self.AddStaticText(self.PUBLISH_HEADER, flags=c4d.BFH_CENTER, name="Publishment", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.AddButton(self.PUBLISH_SUBMIT, flags=c4d.BFH_SCALEFIT, name="Publish to server")
        self.AddSeparatorH(c4d.BFH_SCALEFIT)

        # Myproject
        self.AddStaticText(self.MY_PROJECT_HEADER, flags=c4d.BFH_CENTER, name="My Projects", borderstyle=c4d.BORDER_WITH_TITLE_BOLD)
        self.GroupBegin(id=10007, flags=c4d.BFH_SCALEFIT,cols=1, rows=1)
        self.AddButton(self.MY_PROJECT_ACTIVATE, flags=c4d.BFH_SCALEFIT, name="Load My projects")
        self.GroupEnd()
        self.AddSeparatorH(c4d.BFH_SCALEFIT)

        self.GroupEnd()


        return True

    def AIPromptScene(self, prompt, auth_token):
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
            response = request.urlopen(link)
            save_path = os.path.join(temp_dir, "ai.glb")
            with open(save_path, 'wb') as f:
                f.write(response.read())
            save_path= str(save_path).replace("\\", "/")
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

    def GetSearchLabel(self):
        url="https://api.mondial3d.studio/api/Nft/all-labels"
        response= send_request(url)
        if isinstance(response, str) and (response.startswith("HTTP Error") or response.startswith("URL Error") or response.startswith("An error occurred")):
            c4d.gui.MessageDialog(response)
            return None
        else:
            self.search_labels=response
            return True
        
    def autocomplete_search(self, input):
        user_input = input
        exact_match = [word for word in self.search_labels if word.lower() == user_input.lower()]
        suggestions = [word for word in self.search_labels if word.lower().startswith(user_input.lower())]
        
        if len(exact_match) > 0:
            suggestions.remove(exact_match[0])
            suggestions.insert(0, exact_match[0])
        
        if len(suggestions) > 0:
            self.search_label = suggestions[0]
            
        return self.search_label
    
    def GetMarketplaceInfo(self, search_label):
        save_paths= []
        self.marketplace_model_url= []
        if not search_label == "":
            base_url=f"https://api.mondial3d.studio/api/Nft/blendernfts?pageid={self.PAGEID}&take=3&Labels={search_label}"
        else:
            base_url=f"https://api.mondial3d.studio/api/Nft/blendernfts?pageid={self.PAGEID}&take=3"
        headers = {}

        response= send_request(base_url, headers)
        if isinstance(response, str) and (response.startswith("HTTP Error") or response.startswith("URL Error") or response.startswith("An error occurred")):
            c4d.gui.MessageDialog(response)
            return None
        else:
            data= response["listNFTs"]
            image_base_url = "https://cdn.mondial3d.com/"

            for item in data:
                image_url = image_base_url + item["imageAdress"]
                save_path = os.path.join(temp_dir, item["imageAdress"])
                self.marketplace_model_url.append(item["url"])
                req = request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = request.urlopen(req)
                with open(save_path, 'wb') as f:
                    f.write(response.read())
                save_path= str(save_path).replace("\\", "/")
                save_paths.append(save_path)
            return save_paths

    def HandleMarketPlaceDraw(self, search_label= None):
        save_paths = self.GetMarketplaceInfo(search_label)
        self.user_areas=[]

        if save_paths:
            # Main group
            self.LayoutFlushGroup(10003)
            self.GroupBegin(id=10003, flags=c4d.BFH_SCALEFIT, cols=1, rows=2)

            # Searchbar
            self.GroupBegin(id=10004, flags=c4d.BFH_SCALEFIT, cols=2, rows=1) 
            self.GroupBorderSpace(10, 10, 10, 0)
            self.AddEditText(self.MARKETPLACE_SEARCH, flags= c4d.BFH_SCALEFIT, initw=200)
            self.AddButton(self.MARKETPLACE_SEARCH_SUBMIT, flags=c4d.BFH_RIGHT, name="Search")
            self.GroupEnd()

            # Navigation
            self.GroupBegin(id=10005, flags=c4d.BFH_SCALEFIT, cols=2, rows=1) 
            self.GroupBorderSpace(10, 10, 10, 10)
            if self.PAGEID == 1:
                self.AddButton(self.MARKETPLACE_NEXT, c4d.BFH_SCALEFIT, name="Next")
            else:
                self.AddButton(self.MARKETPLACE_PREVIOUS, c4d.BFH_SCALEFIT, name="Prev")
                self.AddButton(self.MARKETPLACE_NEXT, c4d.BFH_SCALEFIT, name="Next")
            self.GroupEnd()

            # Items
            self.GroupBegin(id=10006, flags=c4d.BFH_SCALEFIT, cols=3, rows=len(save_paths)//3 + len(save_paths)%3)
            if not self.user_areas:
                self.user_areas = [MyUserArea(path) for path in save_paths]
                for index, user_area in enumerate(self.user_areas):
                    self.GroupBegin(id=10007+index, flags=c4d.BFH_SCALEFIT, cols=1, rows=2) 
                    self.GroupBorderSpace(5, 5, 5, 5)
                    self.AddUserArea(200 + index, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
                    self.AttachUserArea(user_area, 200 + index)
                    user_area.Redraw()
                    self.AddButton(300 + index, c4d.BFH_SCALEFIT, name="Download and Load Model")
                    self.GroupEnd() 
            self.GroupEnd()
            # End main group
            self.GroupEnd()
            self.LayoutChanged(10003)

            return True
        return False
    
    def GetMarketPlaceModel(self, i):
        
        url= f"https://api.mondial3d.studio/api/Nft/Download3D?URL={self.marketplace_model_url[i]}"
        response = request.urlopen(url)
        download_url = response.read().decode('utf-8')
        response = request.urlopen(download_url)

        save_path = os.path.join(temp_dir, "{}.glb".format(self.marketplace_model_url[i]))
        with open(save_path, 'wb') as f:
            f.write(response.read())
        save_path= str(save_path).replace("\\", "/")

        if os.path.exists(save_path) and os.path.getsize(save_path) > 15:
            print(f"File has been downloaded and saved to path: {save_path}")
        else:
            print("File download failed or file is empty.")
            return None
        
        return save_path

    def PublishToServer(self):
        doc = documents.GetActiveDocument()
        objects = doc.GetObjects()
        for obj in objects:
            obj.SetBit(c4d.BIT_ACTIVE)
        
        FBX_EXPORTER_ID = 1026370
        save_path = os.path.join(temp_dir, "export.fbx")
        settings = c4d.BaseContainer()
        settings[c4d.FBXEXPORT_ASCII] = True

        if plugins.FindPlugin(FBX_EXPORTER_ID, c4d.PLUGINTYPE_SCENESAVER) is not None:
            if documents.SaveDocument(doc, save_path, c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST, FBX_EXPORTER_ID):
                print("FBX exported successfully.")
                save_path= str(save_path).replace("\\", "/")
                return save_path
            else:
                print("Failed to export FBX.")
                return False
        else:
            print("FBX Exporter plugin not found.")
            return False

    def CreateProjectCover(self, projectID):  
        outputPath = os.path.join(temp_dir, f"{projectID}.png")

        doc = c4d.documents.GetActiveDocument()
        rdata = doc.GetActiveRenderData()
        rdata[c4d.RDATA_XRES] = 800 
        rdata[c4d.RDATA_YRES] = 600
        bmp = c4d.bitmaps.BaseBitmap()
        bmp.Init(x=800, y=600)
        result = c4d.documents.RenderDocument(doc, rdata.GetData(), bmp, c4d.RENDERFLAGS_EXTERNAL)
        if result != c4d.RENDERRESULT_OK:
            return
        
        bmp.Save(outputPath, c4d.FILTER_PNG)
        outputPath= str(outputPath).replace("\\","/")
        return outputPath

    def ServerProject(self, model_path):
        global auth_token
        # Create New Project
        create_url = "https://api.mondial3d.studio/api/Nft/create-project"
        headers = {"Authorization": "Bearer " + auth_token}
        projectID= send_request(create_url, headers)
        # Update Project
        headers = {"Authorization": "Bearer " + auth_token, "projectid": projectID}
        update_url = "https://api.mondial3d.studio/api/Nft/update-project"
        cover_path= self.CreateProjectCover(projectID=projectID)

        # Define boundary
        boundary = 'wL36Yn8afVp8Ag7AmP8qZ0SA4n1v9T'

        with open(model_path, 'rb') as f, open(cover_path, 'rb') as img:
            encoded_string = base64.b64encode(img.read()).decode('utf-8')
            data = {"projectid": projectID,
                    "cover": f"data:image/jpeg;base64,{encoded_string}"}

            # Prepare payload
            body = bytearray()
            for key, value in data.items():
                body.extend('--{}\r\n'.format(boundary).encode())
                body.extend('Content-Disposition: form-data; name="{}"\r\n\r\n'.format(key).encode())
                body.extend('{}\r\n'.format(value).encode())

            body.extend('--{}\r\n'.format(boundary).encode())
            body.extend('Content-Disposition: form-data; name="file"; filename="{}"\r\n'.format(os.path.basename(model_path)).encode())
            body.extend('Content-Type: {}\r\n\r\n'.format(mimetypes.guess_type(model_path)[0] or 'application/octet-stream').encode())
            body.extend(f.read())
            body.extend('\r\n--{}--\r\n'.format(boundary).encode())

            headers['Content-Type'] = 'multipart/form-data; boundary={}'.format(boundary)
            req = Request(update_url, data=body, headers=headers)
            response = urlopen(req)

            if 200 <= response.getcode() < 300:
                c4d.gui.MessageDialog(f"Successfully publish your project. Project ID: {projectID}")
            else:
                c4d.gui.MessageDialog("Failed to publish to server, Check your internet conncetion...")

    def GetMyProjectInfo(self):
        save_paths= []
        self.my_project_url=[]
        global auth_token, temp_dir
        project_list_url="https://api.mondial3d.studio/api/Nft/Get-Project-List" 
        headers={"Authorization" : "Bearer "+ auth_token}
        responses= send_request(project_list_url, headers)
        for r in responses:
            save_path = os.path.join(temp_dir, str(r["id"])+".png" )
            req = request.Request(r["cover"], headers={'User-Agent': 'Mozilla/5.0'})
            try:
                response = request.urlopen(req)
                # If the status code is 404, skip this iteration
                if response.getcode() == 404:
                    print(f'Failed to download image {r["id"]}: 404 Not Found')
                    continue
                with open(save_path, 'wb') as out_file:
                    out_file.write(response.read())
                save_path= str(save_path).replace("\\", "/")
                self.my_project_url.append(str(r["id"]))
                save_paths.append(save_path)
            except Exception as e:
                print(f'Failed to save image {r["id"]}: {str(e)}')
        
        return save_paths

    def HandleMyProjectDraw(self):
        save_paths= self.GetMyProjectInfo()
        self.my_project_area=[]

        if save_paths:
            # Main group
            self.LayoutFlushGroup(10007)
            self.GroupBegin(id=10007, flags=c4d.BFH_SCALEFIT, cols=1, rows=2)

            # Items
            self.GroupBegin(id=10008, flags=c4d.BFH_SCALEFIT, cols=3, rows=len(save_paths)//3 + len(save_paths)%3)
            if not self.my_project_area:
                self.my_project_area = [MyUserArea(path) for path in save_paths]
                for index, project_area in enumerate(self.my_project_area):
                    self.GroupBegin(id=10007+index, flags=c4d.BFH_SCALEFIT, cols=1, rows=2) 
                    self.GroupBorderSpace(5, 5, 5, 5)
                    self.AddUserArea(400 + index, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT)
                    self.AttachUserArea(project_area, 400 + index)
                    project_area.Redraw()
                    self.AddButton(500 + int(self.my_project_url[index]), c4d.BFH_SCALEFIT, name="Download and Load Project")
                    self.GroupEnd() 
                    
            self.GroupEnd()
            # End main group
            self.GroupEnd()
            self.LayoutChanged(10007)

            return True
        return False
            
    def GetMyprojectModel(self, i):
        global auth_token, temp_dir
        try:
            request_url = f"https://api.mondial3d.studio/api/Nft/open-project?projectid={i}"
            headers = {"Authorization" : "Bearer " + auth_token}
            response = send_request(request_url, headers)
            model_url = response["jsonFile"]
            file = request.urlopen(model_url)
            save_path = os.path.join(temp_dir, f"{i}.glb")
            with open(save_path, 'wb') as f:
                f.write(file.read()) 
            save_path = str(save_path).replace("\\","/")
            return save_path
        except Exception as e:
            print("An error occurred:", e)
            return None

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
                response = self.AIPromptScene(prompt, auth_token)

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
            fbx_save_path= glb_save_path.replace(".glb", ".fbx")

            script_path = os.path.join(os.path.dirname(__file__), "ConvertGLBtoFBX.py")
            # script_path = os.path.join(os.getcwd(), "ConvertGLBtoFBX.py")
            script_path= script_path.replace("\\", "/")

            blender_path= self.FindBlenderPath()

            cmd = [blender_path, '--background', '--python', script_path, '--', glb_save_path]

            try:
                result = subprocess.run(cmd, check=True, capture_output=True)
                print(result.stdout.decode('utf-8'))
                print(f"Loading FBX document from path: {fbx_save_path}")
                loaded_doc = c4d.documents.LoadDocument(fbx_save_path, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS)
                if not loaded_doc:
                    print("Failed to load FBX document:", fbx_save_path)
                    return False

                print("FBX document loaded successfully.")
                
                active_doc = c4d.documents.GetActiveDocument()  # Get the currently active document
                c4d.documents.MergeDocument(active_doc, fbx_save_path, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS)

                c4d.EventAdd()

            except subprocess.CalledProcessError as e:
                print(f"An error occurred while converting .glb to .fbx: {str(e)}")
                print(e.stderr.decode('utf-8'))
                return False
        
        elif id == self.MARKETPLACE_ACTIVATE:
            self.GetSearchLabel()
            return self.HandleMarketPlaceDraw(self.search_label)

        elif id >= 300 and id <= 303:
            glb_save_path=self.GetMarketPlaceModel((id-300))
            fbx_save_path= glb_save_path.replace(".glb", ".fbx")

            
            # script_path = os.path.join(os.getcwd(), "ConvertGLBtoFBX.py")
            script_path = os.path.join(os.path.dirname(__file__), "ConvertGLBtoFBX.py")
            script_path= script_path.replace("\\", "/")

            blender_path= self.FindBlenderPath()

            cmd = [blender_path, '--background', '--python', script_path, '--', glb_save_path]

            try:
                result = subprocess.run(cmd, check=True, capture_output=True)
                print(result.stdout.decode('utf-8'))
                print(f"Loading FBX document from path: {fbx_save_path}")
                loaded_doc = c4d.documents.LoadDocument(fbx_save_path, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS)
                if not loaded_doc:
                    print("Failed to load FBX document:", fbx_save_path)
                    return False

                print("FBX document loaded successfully.")
                
                active_doc = c4d.documents.GetActiveDocument()  # Get the currently active document
                c4d.documents.MergeDocument(active_doc, fbx_save_path, c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS)

                c4d.EventAdd()

            except subprocess.CalledProcessError as e:
                print(f"An error occurred while converting .glb to .fbx: {str(e)}")
                print(e.stderr.decode('utf-8'))
                return False

        elif id == self.MARKETPLACE_PREVIOUS:
            if self.PAGEID > 1:
                self.PAGEID -= 1
                return self.HandleMarketPlaceDraw(self.search_label)
        
        elif id == self.MARKETPLACE_NEXT:
            self.PAGEID += 1
            return self.HandleMarketPlaceDraw(self.search_label)
            
        elif id == self.MARKETPLACE_SEARCH_SUBMIT:
            prompt= self.GetString(self.MARKETPLACE_SEARCH)
            if prompt== "":
                c4d.gui.MessageDialog("Please write your search keyword")
                return False
            else:
                label= self.autocomplete_search(prompt)
                return self.HandleMarketPlaceDraw(label)

        elif id == self.PUBLISH_SUBMIT:
            response= self.PublishToServer()
            if not response == False:
                fbx_save_path= response
                glb_save_path= fbx_save_path.replace(".fbx", ".glb")

                script_path = os.path.join(os.path.dirname(__file__), "ConvertFBXtoGLB.py")
                # script_path = os.path.join(os.getcwd(), "ConvertFBXtoGLB.py")
                script_path= script_path.replace("\\", "/")
                blender_path= self.FindBlenderPath()
                cmd = [blender_path, '--background', '--python', script_path, '--', fbx_save_path]
                try:
                    result = subprocess.run(cmd, check=True, capture_output=True)
                    self.ServerProject(glb_save_path)
                except subprocess.CalledProcessError as e:
                    print(f"An error occurred while converting .glb to .fbx: {str(e)}")
                    print(e.stderr.decode('utf-8'))
                    return False

        elif id == self.MY_PROJECT_ACTIVATE:
            return self.HandleMyProjectDraw()

        elif str(id-500) in self.my_project_url:
            glb_save_path= self.GetMyprojectModel((id-500))
            fbx_save_path= glb_save_path.replace(".glb", ".fbx")

            script_path = os.path.join(os.path.dirname(__file__), "ConvertGLBtoFBX.py")

            script_path= script_path.replace("\\", "/")

            blender_path= self.FindBlenderPath()

            cmd = [blender_path, '--background', '--python', script_path, '--', glb_save_path]

            try:
                result = subprocess.run(cmd, check=True, capture_output=True)
                print(result.stdout.decode('utf-8'))
                c4d.documents.LoadFile(fbx_save_path)

            except subprocess.CalledProcessError as e:
                print(f"An error occurred while converting .glb to .fbx: {str(e)}")
                print(e.stderr.decode('utf-8'))
                return False

    def DestroyDialog(self):
        self.DestroyWindow()
        return True


if __name__ == '__main__':
    MyPlugin().Register()