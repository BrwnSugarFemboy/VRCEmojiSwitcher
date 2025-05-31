#imports
#for VRChat Authentication
import vrchatapi
from vrchatapi.api import authentication_api
from vrchatapi.api import files_api
from vrchatapi.api import economy_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from urllib.parse import quote as urllib_parse_quote
#for tokens
from http.cookiejar import Cookie
#for directory/file manipulation
import os
#for manual delay
import time
#for getting all PNGs in a location
import glob
#for opening the web browser
from webbrowser import open_new as webbrowser_opennew
#for graceful quitting
from sys import exit as sys_exit
#for opening a folder during OOBE
from subprocess import Popen as subprocess_Popen
#for image verification and manipulation
from PIL import Image
#for logging
import datetime
#GUI time
import tkinter
import tkinter.ttk
import tkinter.messagebox
import base64
#threading
import threading

def make_cookie(name, value):
	return Cookie(0, name, value, None, False,"api.vrchat.cloud", True, False, "/", False, False, 173106866300, False, None, None, {})

def ImageSquareFix(pil_img, background_color):
	LogWriter("ImageSquareFix called for " + pil_img)
	pil_img = Image.open(pil_img)
	width, height = pil_img.size
	if width == height:
		return pil_img
	elif width > height:
		result = Image.new(pil_img.mode, (width, width), background_color)
		result.paste(pil_img, (0, (width - height) // 2))
		return result
	else:
		result = Image.new(pil_img.mode, (height, height), background_color)
		result.paste(pil_img, ((height - width) // 2, 0))
		return result

def ImageSizeValidation(pil_img):
	LogWriter("ImageSizeValidation called for: " + pil_img)
	image = Image.open(pil_img)
	width, height = image.size
	if (width > 4000) or (height > 4000):
		LogWriter("ImageSizeValidation returned False")
		return False
	else:
		LogWriter("ImageSizeValidation returned True")
		return True

def OOBE():
	global EULA_Agreed
	#Creates Folder
	if((os.path.exists(VRCEmojiSwitcherPath) is False)):
		print("VRCEmojiSwitcherPath not found, creating...")
		os.mkdir(VRCEmojiSwitcherPath)
		os.mkdir(VRCEmojiSwitcherPath + "\\Backup")
		os.mkdir(VRCEmojiSwitcherPath + "\\Emojis")
		os.mkdir(VRCEmojiSwitcherPath + "\\Emojis\\1")
		os.mkdir(VRCEmojiSwitcherPath + "\\Emojis\\2")
	
	LogWriter("OOBE was called.")
	if(os.path.exists(VRCEmojiSwitcherPath + "\\EULA_Agreed.txt")):
		LogWriter("Logfile Exists")
		file = open((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt"), 'r')
		if(((file.read().splitlines())[-1] == "True")):
			LogWriter("EULA was previously agreed to. Continuing.")
			EULA_Agreed = True
	else:
		LogWriter("Creating EULA_Agreed.txt")
		file = open((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt"), 'w+')
	while(EULA_Agreed == False):
		if os.path.getsize((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt")) == 0 :
			file.write("VRCEmojiSwitcher is not endorsed by VRChat. The developer of this application does not have any affiliation with VRChat Inc.\nBy utilizing this program, you are utilizing the VRChat API which, while not against TOS to utilize, can put your account at risk if abused. Modification of this code makes support from the VRCEmojiSwitcher development team impossible. Play at your own risk.")
			file.close()
	file = open((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt"), 'r')
	if(((file.read().splitlines())[-1] != "True") and (EULA_Agreed == True)):
		file.close()
		file = open((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt"), 'a+')
		file.write("\nTrue")
		LogWriter("EULA was agreed to.")
	file.close()

#GUI Stuffs
def GUI_AcceptEULA():
	global EULA_Agreed
	EULA_Agreed = True

def GUI_OpenAppdata():
	subprocess_Popen(r'explorer /select,' + (VRCEmojiSwitcherPath + "\\Emojis\\"))

def GUI_Quit():
	LogWriter("GUI_Quit was called by clicking the Quit button.")
	global quit
	quit = True

def WindowClose(WindowRoot):
	if tkinter.messagebox.askokcancel("Quit", "Do you really wish to quit?"):
		WindowRoot.destroy()

def GUI_RequestMFAEmail():
	threadRequestMFA = threading.Thread(target=RequestMFAEmail)
	threadRequestMFA.start()

def RequestMFAEmail():
	global UsernameEntryVariable
	global PasswordEntryVariable
	global MFASent
	global MFASentLabel
	MFASent = True
	configuration = vrchatapi.Configuration(
		username = urllib_parse_quote(UsernameEntryVariable.get()),
		password = urllib_parse_quote(PasswordEntryVariable.get()),
	)
	with vrchatapi.ApiClient(configuration) as api_client:
		api_client.user_agent = "VRChatEmojiSwitcher / 0.2.0 femboy@bussy.wtf"
		auth_api = authentication_api.AuthenticationApi(api_client)
		try:
			current_user = auth_api.get_current_user()
		except UnauthorizedException as e:
			if e.status == 200:
				print("getting 2FA")
				if "Email 2 Factor Authentication" in e.reason:
					auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(MFAEntryVariable.get()))
					MFASentLabel = "MFA Sent to email."
				elif "2 Factor Authentication" in e.reason:
					MFASentLabel = "MFA error.\nTOTP is enabled."
				current_user = auth_api.get_current_user()
			else:
				LogWriter("Exception when calling API:\n" + str(e))
				MFASentLabel = "API Error."
		except vrchatapi.ApiException as e:
			LogWriter("Exception when calling API:\n" + str(e))
			MFASentLabel = "API Error."

def GUI_Login(LogInFrame, CycleFrame):
	global AttemptLogin
	global LoggedIn
	
	LogWriter("Called GUI_Login")
	
	if LoggedIn==True :
		LogWriter("GUI - Already logged in.")
	
	
	AttemptLogin = True
	time.sleep(15)
	
	if LoggedIn==True :
		LogWriter("GUI - Logged in successfully.")
		LogInFrame.grid_remove()
		CycleFrame.grid()
	else: 
		tkinter.ttk.Label(LogInFrame, text="Login Failed").grid(column=3, row=2)
		LogWriter("GUI - Failed Login")

def GUI_Cycle(CycleFrame):
	global ProceedToCycle
	global WaitForGUI
	global EmojisCycledLabel
	EmojisCycledLabel = tkinter.ttk.Label(CycleFrame, text="Cycling Emojis...")
	EmojisCycledLabel.grid(column=0,row=2)
	
	ProceedToCycle = True
	WaitForGUI = False

def GUIInit():
	global EULA_Agreed
	global LoginSuccessLabel
	global LoggedIn
	global UsernameEntryVariable
	global PasswordEntryVariable
	global MFAEntryVariable
	global MFASent
	global MFASentLabel
	global quit
	global WindowRoot
	
	UsernameEntryPrompt = "Enter username: "
	PasswordEntryPrompt = "Enter password: "
	MFAEntryPrompt = "2FA Code (Email or TOTP): "
	#Initialize Main App Window
	WindowRoot = tkinter.Tk()
	
	#icon
	if(os.path.exists(VRCEmojiSwitcherPath + "\\icon.ico")):
		LogWriter("Icon found")
		WindowRoot.wm_iconbitmap((VRCEmojiSwitcherPath + "\\icon.ico"))
	else:
		LogWriter("Creating Icon")
		icondata = base64.b64decode(icon)
		file = open((VRCEmojiSwitcherPath + "\\icon.ico"), 'wb')
		file.write(icondata)
		WindowRoot.wm_iconbitmap((VRCEmojiSwitcherPath + "\\icon.ico"))
	
	WindowRoot.title("VRC Emoji Switcher")
	WindowRoot.columnconfigure(0, weight=1)
	WindowRoot.rowconfigure(0, weight=1)
	
	#OOBE
	#Content Frame
	EULAFrame = tkinter.ttk.Frame(WindowRoot, padding ="3 3 12 12")
	EULAFrame.grid(column=0, row=0)
	#Static buttons:
	tkinter.ttk.Button(EULAFrame, text="Quit", command=lambda:[GUI_Quit(),WindowClose(WindowRoot)]).grid(column=0,row=0)
	tkinter.ttk.Button(EULAFrame, text="Open AppData Folder", command=GUI_OpenAppdata).grid(column=3,row=0)
	#EULA Stuff
	tkinter.ttk.Label(EULAFrame, text="VRCEmojiSwitcher is not endorsed by VRChat. \nThe developer of this application does not have any affiliation with VRChat Inc.\nBy utilizing this program, you are utilizing the VRChat API which, while not against TOS to utilize, can put your account at risk if abused.\nModification of this code makes support from the VRCEmojiSwitcher development team impossible.\nPlay at your own risk.").grid(column=1,row=1)
	tkinter.ttk.Button(EULAFrame, text="Agree", command=lambda:[GUI_AcceptEULA(),EULAFrame.grid_remove(), LogInFrame.grid()]).grid(column=1,row=3)
	
	#Login
	#Content Frame
	LogInFrame = tkinter.ttk.Frame(WindowRoot, padding ="3 3 12 12")
	LogInFrame.grid(column=0, row=0)
	#Static buttons:
	tkinter.ttk.Button(LogInFrame, text="Quit", command=lambda:[GUI_Quit(),WindowClose(WindowRoot)]).grid(column=0,row=0)
	tkinter.ttk.Button(LogInFrame, text="Open AppData Folder", command=GUI_OpenAppdata).grid(column=3,row=0)
	#Create Text Entry Field for Login
	UsernameEntryVariable = tkinter.StringVar()
	tkinter.ttk.Entry(LogInFrame, width=30, textvariable=UsernameEntryVariable).grid(column=2,row=1)
	PasswordEntryVariable = tkinter.StringVar()
	tkinter.ttk.Entry(LogInFrame, width=30, textvariable=PasswordEntryVariable, show="\u2022").grid(column=2,row=2)
	MFAEntryVariable = tkinter.StringVar()
	tkinter.ttk.Entry(LogInFrame, width=15, textvariable=MFAEntryVariable).grid(column=2,row=3)
	#Create label for the Entry Fields for Login
	tkinter.ttk.Label(LogInFrame, text=UsernameEntryPrompt).grid(column=1, row=1)
	tkinter.ttk.Label(LogInFrame, text=PasswordEntryPrompt).grid(column=1, row=2)
	tkinter.ttk.Label(LogInFrame, text=MFAEntryPrompt).grid(column=1, row=3)
	if(MFASent):
		tkinter.ttk.Label(LogInFrame, text=MFASentLabel).grid(column=3, row=1)
	#Create Request 2FA Email button:
	tkinter.ttk.Button(LogInFrame, text="Request 2FA Email Code", command=GUI_RequestMFAEmail).grid(column=3,row=2)
	#Create login button
	threadLogin = threading.Thread(target=lambda:[GUI_Login(LogInFrame, CycleFrame)])
	tkinter.ttk.Button(LogInFrame, text="Login", command=lambda:[threadLogin.start()]).grid(column=3,row=3)
	LogInFrame.grid_remove()
	
	#RunningState
	#Content Frame
	CycleFrame = tkinter.ttk.Frame(WindowRoot, padding ="3 3 12 12")
	CycleFrame.grid(column=0, row=0)
	#Static buttons:
	tkinter.ttk.Button(CycleFrame, text="Quit", command=lambda:[GUI_Quit(),WindowClose(WindowRoot)]).grid(column=0,row=0)
	tkinter.ttk.Button(CycleFrame, text="Open AppData Folder", command=GUI_OpenAppdata).grid(column=3,row=0)
	#Main GUI
	LoginSuccessLabel = tkinter.ttk.Label(CycleFrame, text="")
	LoginSuccessLabel.grid(column=0,row=1)
	#Create buttons
	tkinter.ttk.Button(CycleFrame, text="Cycle Emojis", command=lambda:[GUI_Cycle(CycleFrame)]).grid(column=3,row=3)
	
	CycleFrame.grid_remove()
	
	if(EULA_Agreed):
		EULAFrame.grid_remove()
		LogInFrame.grid()
	if(os.path.exists(VRCEmojiSwitcherPath + '\\cookie')):
		LogInFrame.grid_remove()
		CycleFrame.grid()
	
	WindowRoot.protocol("WM_DELETE_WINDOW", lambda:[GUI_Quit(), WindowClose(WindowRoot)])
	
	WindowRoot.mainloop()


#API Stuffs
def Authenticate():
	global LoginSuccessLabel
	global LoggedIn
	global UsernameEntryVariable
	global PasswordEntryVariable
	global MFAEntryVariable
	global AttemptLogin
	if(os.path.exists(VRCEmojiSwitcherPath + '\\cookie')):
		configuration = None
		LogWriter("Cookie Found")
		with vrchatapi.ApiClient(configuration) as api_client:
			api_client.user_agent = "VRChatEmojiSwitcher / 0.2.0 femboy@bussy.wtf"
			auth_api = authentication_api.AuthenticationApi(api_client)
			try:
				file = open(VRCEmojiSwitcherPath + '\\cookie','r')
				cookie = file.read().splitlines()
				file.close()
				#try signing in with the (hopefully) pulled cookie
				
				api_client.rest_client.cookie_jar.set_cookie(make_cookie("auth", cookie[0]))
				api_client.rest_client.cookie_jar.set_cookie(make_cookie("twoFactorAuth",cookie[1]))
				current_user = auth_api.get_current_user()
			except UnauthorizedException as e:
				if e.status == 200:
					LogWriter("Login invalid (200), clearing cookie.")
					os.remove(VRCEmojiSwitcherPath + '\\cookie')
				else:
					LogWriter("Exception when calling API:" + str(e))
					LogWriter("Clearing cookie")
					os.remove(VRCEmojiSwitcherPath + '\\cookie')
					return None, False
			except vrchatapi.ApiException as e:
				LogWriter("Exception when calling API:\n" + str(e))
				LogWriter("Clearing cookie")
				os.remove(VRCEmojiSwitcherPath + '\\cookie')
				return None, False
			LoggedIn = True
			LoginSuccessLabel.config(text=("Logged in as: " + str(current_user.display_name)))
			LogWriter("Logged in as: " + str(current_user.display_name))
			return api_client, True
	else:
		LogWriter("Attempting Login with credentials.")
		while True:
			while AttemptLogin == True:
				configuration = vrchatapi.Configuration(
						username = urllib_parse_quote(UsernameEntryVariable.get()),
						password = urllib_parse_quote(PasswordEntryVariable.get()),
				)
				with vrchatapi.ApiClient(configuration) as api_client:
					api_client.user_agent = "VRChatEmojiSwitcher / 0.2.0 femboy@bussy.wtf"
					auth_api = authentication_api.AuthenticationApi(api_client)
					try:
						current_user = auth_api.get_current_user()
					except UnauthorizedException as e:
						if e.status == 200:
							print("getting 2FA")
							if "Email 2 Factor Authentication" in e.reason:
								auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(MFAEntryVariable.get()))
							elif "2 Factor Authentication" in e.reason:
								auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(MFAEntryVariable.get()))
							current_user = auth_api.get_current_user()
						else:
							LogWriter("Exception when calling API:" + str(e))
							return None, False
					except vrchatapi.ApiException as e:
						LogWriter("Exception when calling API:\n"+ str(e))
						return None, False
					LoggedIn = True
					LoginSuccessLabel.config(text=("Logged in as: " + str(current_user.display_name)))
					LogWriter("Logged in as: " + str(current_user.display_name))
					cookie_jar = api_client.rest_client.cookie_jar._cookies["api.vrchat.cloud"]["/"]
					file = open(VRCEmojiSwitcherPath + '\\cookie', 'w+')
					file.write(cookie_jar["auth"].value + "\n")
					file.write(cookie_jar["twoFactorAuth"].value)
					LogWriter("Cookie written.")
					file.close()
					return api_client, True

def SubscriptionCheck(api_client=None):
	global quit
	global WindowRoot
	LogWriter("Subscription Check was called.")
	if api_client is None:
		LogWriter("SubscriptionCheck() was called without an api_client passed")
		sys_exit()
	
	economy_api = vrchatapi.api.economy_api.EconomyApi(api_client)
	CurrentSub = economy_api.get_current_subscriptions()
	if CurrentSub == []:
		webbrowser_opennew("https://vrchat.com/home/group/grp_ca3034e1-cf2d-4cec-8e0b-1fac32bfbad0")
		LogWriter("Subscription is not active. Pay VRC.")
		quit = True
		WindowRoot.destroy()
		sys_exit()
	if CurrentSub[0].status == "active":
		LogWriter("Active Subscription Found.")
		return True
	else:
		webbrowser_opennew("https://vrchat.com/home/group/grp_ca3034e1-cf2d-4cec-8e0b-1fac32bfbad0")
		LogWriter("Subscription is not active. Pay VRC.")
		quit = True
		WindowRoot.destroy()
		sys_exit()
	
def EmojiBackup(api_client=None):
	LogWriter("EmojiBackup was called.")
	if api_client is None:
		LogWriter("EmojiBackup() was called without an api_client passed")
		sys_exit()
	
	os.mkdir(VRCEmojiSwitcherPath + "\\Backup\\originalEmojiBackup")
	LogWriter("Backing up emojis...")
	files_api = vrchatapi.api.files_api.FilesApi(api_client)
	currentEmojis = files_api.get_files(tag="emoji", n=9)
	for i in currentEmojis:
		LogWriter("Downloading image " + str(currentEmojis.index(i)))
		thread = files_api.download_file_version(i.id, 1, async_req=True)
		image = thread.get()
		sourceFile = open(image, "rb")
		file = open(VRCEmojiSwitcherPath + '\\Backup\\originalEmojiBackup\\image' + str(currentEmojis.index(i)) + '.png', 'wb')
		file.write(sourceFile.read())
		sourceFile.close()
		file.close()
		LogWriter("Image Downloaded... waiting for manual delay (5s).")
		time.sleep(5)
	LogWriter("All Emojis Downloaded")

def RemoveAllEmojis(api_client=None):
	LogWriter("RemoveAllEmojis was called.")
	if api_client is None:
		LogWriter("SubscriptionCheck() was called without an api_client passed")
		sys_exit()
	files_api = vrchatapi.api.files_api.FilesApi(api_client)
	currentEmojis = files_api.get_files(tag="emoji", n=9)
	for i in currentEmojis:
		LogWriter("Removing emoji number " + str((int(currentEmojis.index(i)) + 1)))
		files_api.delete_file(i.id)
		LogWriter("Emoji removed. Manual delay of 5s.")
		time.sleep(5)
	LogWriter("All Emojis Removed.")

def DirectoryTracker(currentDir=None):
	LogWriter("DirectoryTracker was called.")
	
	allDirs = (os.listdir(VRCEmojiSwitcherPath + "\\Emojis\\"))
	if allDirs is None:
		LogWriter("Error pulling directories")
	else:
		LogWriter("-----\nAll Files and Folders in Emoji Path (non-recursive): ")
	for item in allDirs:
		if os.path.isdir((os.path.join((VRCEmojiSwitcherPath)+"\\Emojis\\",item))):
			LogWriter(item)
		else:
			LogWriter("Found a file:" + item)
			allDirs.remove(item)
	LogWriter("-----")
	
	if currentDir is None:
		currentDir = allDirs[0]
		nextDir = allDirs[0]
		LogWriter("Set currentDir/nextDir to " + allDirs[0] + " because currentDir was None")
	else:
		if(currentDir is not allDirs[-1]):
			nextDir = allDirs[int(allDirs.index(currentDir))+1]
		else:
			nextDir = allDirs[0]
	LogWriter("CurrentDirectory: " + currentDir)
	LogWriter("NextDirectory: " + nextDir)
	LogWriter("Ending DirectoryTracker function")
	return currentDir, nextDir

def UploadNextEmojis(api_client=None, nextDir=None):
	LogWriter("UploadNextEmojis was called.")
	LogWriter("NextDir is set to: " + nextDir)
	if api_client is None:
		LogWriter("UploadNextEmojis() was called without an api_client passed")
		sys_exit()
	
	allNewEmojis = glob.glob((VRCEmojiSwitcherPath + "\\Emojis\\" + nextDir +  "\\*.png"), recursive=False)
	if(len(allNewEmojis) == 0):
		LogWriter("No Emojis found in " + VRCEmojiSwitcherPath + "\\Emojis\\" + nextDir)
		return
	if(len(allNewEmojis) > 9):
		LogWriter("Too many Emojis found in " + VRCEmojiSwitcherPath + "\\Emojis\\" + nextDir)
		return
	#File Squaring:
	for i in allNewEmojis:
		ImageSquareFix(i, "#00000000").save(i, quality=100)
	#ToDo File Validation
	#Upload the Emojis
	LogWriter("Uploading emojis")
	files_api = vrchatapi.api.files_api.FilesApi(api_client)
	for i in allNewEmojis:
		if(ImageSizeValidation(i)):
			EmojiSplitName = (os.path.split(i)[1]).split("_")
			if((len(EmojiSplitName) == 3) and (str(EmojiSplitName[1]).lower() == 'static') and (int(EmojiSplitName[0]) == allNewEmojis.index(i))):
				LogWriter("Discovered Static Emoji")
				LogWriter("Uploading Emoji number: " + str(allNewEmojis.index(i)) + " with filename: " + i)
				files_api.upload_image((i), tag="emoji", animation_style=str(os.path.splitext(EmojiSplitName[2])[0]).lower())
				time.sleep(5)
			elif ((len(EmojiSplitName) == 5) and (str(EmojiSplitName[1]).lower() == 'anim') and (int(EmojiSplitName[0]) == allNewEmojis.index(i)) ):
				LogWriter("Uploading Animated Emoji Emoji number: " + str(allNewEmojis.index(i)) + " with filename:" + i)
				files_api.upload_image((i), tag="emojianimated", frames=int(EmojiSplitName[2]), frames_over_time=int(EmojiSplitName[3]), animation_style=str(os.path.splitext(EmojiSplitName[4])[0]).lower())
				time.sleep(5)
			else:
				LogWriter("Discovered Nonstandard Emoji")
				LogWriter("Uploading Emoji number: " + str(allNewEmojis.index(i)) + " with filename:" + i + " with the default \"bounce\" animation. Bounce on it.")
				files_api.upload_image((i), tag="emoji", animation_style=str("bounce"))
				time.sleep(5)
		else:
			LogWriter("Error, image \"" + i + "\" is larger than 4000 in either height or width. Please resize this image")
	LogWriter("Emojis uploaded from :\n" + VRCEmojiSwitcherPath + "\\Emojis\\" + nextDir)

#Logging Stuffs
def LogWriter(LogString=None):
	#print LogString to console
	print(str(datetime.datetime.now()) + "    " + LogString)
	#Actual Logging below
	LogPath = VRCEmojiSwitcherPath + "\\VRCEmojiSwitcherLog.log"
	if(os.path.exists(LogPath) is False):
		file = open(LogPath,'w')
		file.close()
	#Rename when it reaches 10MB
	AllLogs = glob.glob(VRCEmojiSwitcherPath + "\\VRCEmojiSwitcherLog*.log")
	if os.path.getsize(LogPath) > 10000000:
		if len(AllLogs) >= 6:
			os.remove(VRCEmojiSwitcherPath + AllLogs[-1])
		else:
			for i in AllLogs:
				os.rename(i, VRCEmojiSwitcherPath + "\\VRCEmojiSwitcherLog." + str(int(AllLogs.index(i)) + 1) + ".log")
	#Write to LogFile
	if LogString is None:
		print("then why the fuck did you call me bitch")
	else:
		file = open(LogPath, 'a+')
		file.write(str(datetime.datetime.now()) + "    " + LogString + "\n")
		file.close()


def main():
	global EULA_Agreed
	global LoggedIn
	global quit
	global AttemptLogin
	global ProceedToCycle
	global WaitForGUI
	global EmojisCycledLabel
	currentDir = None
	if os.path.exists(VRCEmojiSwitcherPath):
		LogWriter("Initializing program.")
	else:
		print(str(datetime.datetime.now()) + "    Initializing Program")
	while(not quit):
		
		#OOBE
		while(EULA_Agreed == False) and not quit:
			OOBE()
		#Authenticate user
		while(LoggedIn == False) and (not quit):
			if(os.path.exists(VRCEmojiSwitcherPath + '\\cookie')):
				LogWriter("Attempting Cookie Login")
				time.sleep(3)
				api_client, LoggedIn = Authenticate()
			if(AttemptLogin):
				LogWriter("Waiting for Login Attempt")
				api_client, LoggedIn = Authenticate()
				AttemptLogin = False
		
		WaitForGUI = True
		while(WaitForGUI) and not quit:
			time.sleep(0.01)
		
		#Subscription Check
		if(LoggedIn) and not quit:
			SubscriptionCheck(api_client)
		
			#Backup Current Emojis if not done already
			if (os.path.exists(VRCEmojiSwitcherPath + "\\Backup\\originalEmojiBackup") is False):
				EmojiBackup(api_client)
		
		#DirectoryTracker()
		currentDir, nextDir = DirectoryTracker(currentDir)
		
		#Pauses script, and awaits next user manual call
		while(ProceedToCycle) and (LoggedIn) and not quit:
			#Remove All Current Emojis
			RemoveAllEmojis(api_client)
			
			#Upload Next Emojis
			UploadNextEmojis(api_client, nextDir)
			
			#Proceeds through directory cycle
			currentDir = nextDir
			#Resets
			ProceedToCycle = False
			EmojisCycledLabel.config(text="Emojis Cycled.")
			time.sleep(5)
			EmojisCycledLabel.config(text="")
			
	sys_exit()

#Global Variables
LoggedIn = False
EULA_Agreed = False
quit = False
UsernameEntryVariable = None
PasswordEntryVariable = None
MFAEntryVariable = None
AttemptLogin = False
MFASent = False
ProceedToCycle = False
WaitForGUI = True
VRCEmojiSwitcherPath = (os.getenv('APPDATA')) + "\\VRCEmojiSwitcher"

icon = \
"""
AAABAAQAAAAQAAEABADIDAAARgAAAAAAAAABAAgAPB0AAA4NAAAAAAAAAQAYAA8mAABKKgAAAAAA
AAEAIABgJgAAWVAAAIlQTkcNChoKAAAADUlIRFIAAAEAAAABAAgGAAAAXHKoZgAADI9JREFUeNrt
3Qt227YWBVBzZPHMTM/MGZka2XWiKCLFDz4XwD5rta+vTRSZ4tkEIH6mF2kpl19/TXf/fAnwvqYn
71GCZiq884pIoH5OSi8yLgiT0ouMC8Gk+CLjQjApvsi4EEyKLzIuBJPyi4yLwKT8IuMiMCm/yLgI
TMovMi4Ek/KLACBE+S+XP3/UNE2L/02kmfZN0+q+vvTfSyEwlSq/AoukwSMlAlPu8iu+SBgIpmIA
KL5ISAimLQAov0ifCDwFQPlF+oZgSg6A4os0g8AiAIdbDACR9hBIAoDy/52fP3/+9f9//Phho0if
AIxe/vuyrwUEEg2BydE/T9khIA0gcA6AEcqfovQQEAAMXnoISEAEjgPQW/lLlB4AEm0UMI189C9Z
+tvCX/9cAEizALRe/tpHewBIFASGAqB08U0BBABKDwABgOIDQAAwfPEBIAAYvPwAEAAMWnwACAAG
Lj4ABACDlx8AAoBBiw8BAUCH5f/4+Hj479/e5oWf5QMAAoDWir+36Ms/EwAEAE2U/1Hp9xYeAAKA
xsp/X/yzpQeAAKCB8t8WP2XpASAAaKD4uUoPAAFAwPKXLD4ABABByl+j+AAQAAQp/5Hiv7/PL2/z
1+97//9/j7wOAAQAFcp/tPiPnqL4DcB3Xl9ff5X6FQACgG7Kv7A978t/my1/BgAkAgLVACh/Y87X
A1tyf/m3IgAAGRaA3su/BQEAyJAAlL0X/+uJrXgegDUEACDDAdB6+QEgAGgAgFPlB4AMUv6iADRT
/sQALCEAABkGgKbKvzb/f7kr8gwAAUBf5V8A4H2t7TMABABVAEha/AUA3rcc6mcASHsIZAWgyfLf
AfC+dZy/gMDRRcBHH2IPj2QXAMQu/xkAHiCwF4DrNrteU7D48vP86zXf7OUCgLxb8UD5HyCwF4Ct
H57RgDQBwPUCnLUjWsjyfx/9p2MAvH0LcFnbNv8CsHcBBwRypvzZAfgs0ft7UgBKlf+7pB+vH8nL
nxKAa67IWlCUsABckwKBkuU/OhL4BGDD5rkH4Lqd5gMnGRkNSGgAUiFQq/x/fob5+ff9l+0FzgHA
5/KDRUIARAPgLAJny/99G6/3z3LMIT6olFMA0wIJD8AZBA4DcPt13onbd7UIgGkBAMIBcASCIyW9
vXHnEgC/h+2VRgRnvwY0GpBmAfgqwM8s5b8/8q+VvyYCa2cC5kDAaAAAoQDYAkGqW3m1BsD3KCnF
ouB9LBICIBQASxAcfmjHAQBqILD1YqBcowHTAgiEAuAWgqNP5X009//899fv7+Y2ATAtkKEAuB0C
7y3pw8W/jTfxiA7AqKOB+5/ZFGYQAJZGA0/LOi0U/wkCLQAw0mjg2RqIKcwAAByCYAsAdwicWWe4
XV/Y8zpnbwjy7LLhliHYugND4PzBoQkAdk0L9lzGOx8AYOXkomu2nmCU6o5APU4L9vxM1jAGAmAr
BFsv3tl64c6j8i8BsBWU1LcE62VasPfrTwAMCMAWCJ4hsLv8OwDYgkCOewLmQqDkwpt7IgDgNAS/
EVi6gm/Of35BzYeDtjwaAEDZbdgFAF+FOn7+wKGj/5OvFyM8HbhFCI6cAQkAAGxeHziLwNavF6M8
HrzFRcK97xkAANg8LSgBQI1FwJ5GA3vfq68DAVAMglSLizUeDNLKBUbWAQAQGoJFBObtr1vzyUDR
RwMAKAvAZZSNfb9QeHo08D4ffp0IjwaLDIF1gDLbbSgAckFw7D3EmLdGXSQEgBFAc+sDLQIQdTSw
9/24StAaQBIISt0sNOLTgSNdYGQdAABVIcg9Goj8ePAI0wInBAGg6/WByABEmRZYBwBACAjyIHDp
bmdKPRpwQlAZAIZdBKwLweXw+/mep0e/Su/svmQdAAAdrw9cdpU9ymdSEgLrAADoFIJLlnK1jsCj
Ibx1AACEhuAYApds5+WX/GxKjAasAwCgaQiupwvnKHqUzyb3uQPWAQAQPrcLhSXLHumzyTUaaGkb
AGDAo3/twkf7bCJAAAAAdH+Ui/zZ1N5OAADAcMWP+NnU2m6jXxgEAOUPk5yLhEe2xXXa1jsOABgQ
gOifSenteL89/r30+80+C4D1RFzka/3zKAXB9zZ5dJdoAACg2aN/D/PbEtv1uo8ulR8AAGgCgN7P
asu9fefVJze92aYvLgcOA8DIK9c5n2m4lK87P/0YfnsCoNLO6WSql99z9FzrLM9e1ygAAADopOwA
sAbQ5DSg120ZYQH1q//jTQMA0NiO3Pr8P+rXpc8A6HUUAICEKXkmWyvbtdbZfamnAL0iAICGh7PR
RwMtnRq9d1TSCwQWATvY6SOeA9DKmZFHyt8TBADo6Kjn6r6y5X+U1hYLAdDZjh9hWtDC0X/Lol+q
9DJNA0BDR7+a2z3qdRG1ExECAAQowHXnzLGD1hoNRLzLz9rFPiNDAIAgBTh6V9stqbFIGO2ciEgA
REHAxUDBAMhdntafA3Dm/UcDIAICAMiUFI+pyrWQ1sozAlOPWiIC0BoCAMi48y9tp9ZHA1vef4kp
CgCMAEJv3Gcl6GFacD0tuNZ35AAwAmhqHaAkAr3fYCRq+VsbBQCgMgA9jQZGLz0AOs+Rq+D2bKse
FglHL35tAKwBBNvAR7ZVT+cOKL8RwNAAnDn6jj4taLH8AABA0u016iJhq+UHQOdJcUKQ0UC/5a8N
gDWATtYBRoagdQBqY2AEEAyA1ItvPS8S9lT+WggAoLN1gJFGAz0CUBoBAHS6DpDqvWxJrUXCXgEo
hYA1gAHWAXoeDfQMQAkEADAoAL1A0DsA0RAAQGcA5ESgxLQAAAAAwMCjgSMArBXqLCg5Xjv3bcYB
ELBgtbZZa4uEe0q158/fW9acr517FACAYABE2F6tjAa2lulIgSK8dm4ALAIGO8JG21bRIdhSpDPl
efb6OV8bAAONBiJvo8iLhGcAuP251s5qXPsztrz20mcLAOl2DSPn/pGiOEs/y54Hijx67T2vGwEB
AMiuHLnLUar9JNXi2dpO/2gkkAKAvbiUhMAioIQZDewpYA4AHu2vWwF4//W6884epP7ZACBdTQty
fC/fCwCpEACAhEQgxfkIPU4BUiMAAAkLwVkEHpVjbR0j1yLg0jceqU5lPoMAACQsBLlGAffvs87X
gNdfMyfbVkcQ8C2AhEYgJwBbEuVEIADIkBCkui6h9VOBASBDIpDywqSWLwbakiNXDQJAQkOQ48rE
1i4HzjkKAICEhSBH+XsPAKQLBJQfADIgBF+9V34AyJAZ4R5/ABABAABEAAAAkWIALBXken3Ax8fr
y/n1h/nzr1pfBwJAIJCoHC0iBwABwNrxeZ6r7Y/T9/0CMn3F6VRgAcAGAP7887U0effN+5uE5Dy/
AQACgecCLM7yU+2na6UCgEigUcCWX7t0kc3eG6RGKz8ABAKFEm3uDwABQEkAAh79iwEAARkZgajl
B4AMj8DaoqDyLwNgGiD9IJChqDnn/CnKXxwACEhkAFKOBnJPLWo8Eej3bwGAdI3A/8fvvR3OfcQP
UP7zAEBA2oLgpt7zn8uE5r//ViyVy/8PAEYBMhAC9VLzacDJAYCAgKDN8v/+GwQkUr6u5f9Q/Hzl
Tw8ABMSIoEzxUx39lwCAgMDgRI480afgkT8vABCQUTEocYeilOVfA+A0AiCQEdYNSt6WLHX5swMA
AekJhlr3IEz1aPa9ACRDAAYi1Uq/2vUtf4rWyiLo1x0V7NVKfar8WwGAgBj9tVf6TR3f8+4gIBBo
C4Dp9C+AgECgr2H/GQAgIBCID8CU/BdCQCDQBABTtl8MAoFAWACmYr8JAgKBUABMxX8jCAQE1QGY
qr8ACAQCxQGYwr0QDAQAWQGILQkYBALJAcjez8kuJ9GA7wmBI/fqL/r+7KsSEYJeEACAQGBgBAAg
MjACABAZGAEAiAyKwNHn9QFAANABAgAQGRgBAIgMjAAARCAAAJHUCAAAAAIBAABATAWsAQBAIAAA
AAgEAAAAsR5g/g8AgQAAACAQAAAAxHoAAAAgEAAAAAQCAACAWA8AgAgEACBiKgAAEQgAQAQCABCB
AABEOkAAAAAQCAAAAGIqAAAACAQAIAIBAIhYDwCACAQAIGIqAAARCABABAIAEIEAAES6RQAAIhAA
gIipAABEIAAAEQgAQAQCABAZCQEAiEAAACKmAgAQgQAARCAAABEIAEAEAofLDwCR1gBYQgAAIgMh
0GofASASBwEAiAyKwDTMHyoCAQCIQKByDwEgAgARqQRB1Q4CQKQeAtX7BwCROgiE6B4ARMpDEKZ3
ABAph0C4vgFAJD8EYXv2H6AMPQg/78AJAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAAQAA
AAEACAYAAABccqhmAAAdA0lEQVR42u2dCZwU1Z3H/6/6HmYYMIIQiSKHmoDG1SSImhhhzGfXM6tk
PQcPTBRdWTEK5jAxZiGBqPGIMSYDicQj2YCRRTFGYOM5oPEIl0TGCxAGBphx7rNq61V39VR3V3VV
d1dVV3f9fp+PMt3T01X9un7f93//996/GEGlJEn+j6X9LHngvJjJOUIeFXP54oUgyEP+ZDA9BPkX
CAymhyD/goDB+BDkXxAwGB+C/AsCBuNDkH9BwGB+CPIvBBjMD0H+hQCD+SHIvxBgMD8E+RcEDOaH
IADAE+aXpMFDMcYMfwdBJeM+xrJe60a/dwsCzC3zw8AQZA887IQAc9r8MD4EeQYEzDUAwPgQ5EkQ
MCsAgPkhqDwhYAoAmB+CyhsEzHYAwPgQVDIQMARA3i4GACCo9CBgCwBg/sF26NnxBvXvqifqaiYh
EiBRGEqxL15DgXAMDQSVHwD8bP6+1iZq3bCUAmI3BQNMMXxKC4eDKY+jX5rn1sIPCBCw9qfo/a2r
beNq6t/zWgKfTDE9l2p8reHDAUEDgkEwsMO+Kv93Iq5ayAsQKAwA5W7+vq4Oan35FySIXUnTcxkZ
38j0yeeCiec+OweRAAQAeDWsb3npF3GjB1lOxk83fdLwWoUTr51wI65aqNgQyB8A5WT+gd4uannh
fhJ7Ow1NrzV+RG623lBAt8dPMX1YMG55AADyQBTA/Nr78/M/uGaxYvr03l5r+nTjK49DjMRA0JLx
WSigD53RV2FmACpNAJSy+Xv376QDr/xaNrxg2fha81M0pDvOzxUAVHEa0YjjcdVCRYWAbwDQ8cFb
1LrxyfyNb9DzG4731bG+DgCkvgGiqlMxGwABAE7rk3deos53/1qw8blU85tGACbjf0UAAAQAOKfG
5+4hqbs5aXzV/OnGNzN9unKCQLaGH3EGhgAQAGC3Dr61mnp21CcML6QYX/nZIKuva/y+tF48JOpC
QA8GZhJG1wAAEABgl/j8/f7/uz/D+Hrhvl6vn9X4RkoAIZu0sBAG+gfbcMzZJBwOAEAAQMHas/J2
TZgv5BTuWzW+1NOn35MP9CSMHhl8bcQcIOyocwAACAAoaJy/9lfU/8kuCsgmt9rr64b7FoyvGl15
rn/AvGFN8gHipG8AABAAkG+4v3fNfYrxrfb6uRg/3fRJw/fHn2eaUD4p/hqLSUBJHhaw4/6D6Kgv
4oqFAIBctHv1YhK7W1PMr9frZw33czF+uum1vX9/X24nHxxcRCR99nRiky/EFQsBAFaP+fGf42N9
s5A/317f1Pgaw0v9aVFAf79+Aw8Riaolkqo6iIbJP3f1UVdXP4WOuF7+7zxcsRAAYCY+tdf5wat5
hfz5GD+jt08YXzG9gdEpJL92XMLk2QQAQACAde168vvJXj+b+Q2Nb2B+U+ObmX6k/LdHdeX+gQAA
CADIPeS3Mt630utrx/lGxk+G9+nGP6aVqFJ+Lijk/8EAAAgAyC6+Y2/fiw/rjvcLCfkNe/1sPT7v
6T/TEf+5EOMDABAAYC6+eaftnedsNb9IA8R6xMxeP5vxj/uEKKzJ+Fswv+HWX7Xd+C5AAAACAPSl
TvGZmT+fXj8j3O/uzjS+trfXysT8ZsZPOZ/WbgAAAgDSpSb7HDe/dpxvZnwT8+difAAAAgBcMr9Z
yK+an8/RS8e2GJ+YjvnZugiJbwZJaIkRVcjtcIxA0oVNlmEAAEAAgIPmT0n0yWG+Ya9/fBNRNtNq
zd8vEvuvKEnBoGz0oLKiT4pEiQXjO/2kxBJgdq48fPmXZgAAAgByMX/ec/wG5s8a8nPjc1k0P7tJ
jhI6Q0SxSNz80TBJgYhifsX4/DkhrUzY3K3GbceTgK09AADkCQgUDQBO9fyG5j9EHuOPah38AyMA
aHv+mX2y4aPx8D4WTen5VfOzaHwbsBQIpzbsnLcBAAgA0NPHq/6bpL5u98z/uT2pJ2Ch92e/kd/v
JYFY1RAl9JekGEkyDIQYbyz5fxE5CohK8s/yc1VBZYdfslHl4/NzYbduGnzfngEAAAIAml55nHr2
bs0I/Z0wPwU6SRp/IPMkzHp/ecxPVw8ovb/E5B4+Ekv8y+KGjzEFABKLEYuI8SghSsoQQWIBYtJA
fJpxZDvRZQ0pEAAAIN8CYP9rf6buXW+Yml8FQCHmF0c2ERvWbd38WgDMTCwOilUrhucGVx5HYonG
4oaXo4NYogoQ/zcSjj+XKBOWhMDctwEACADo3PkOHXz9McvmV3v/vML+o3can4gFAEi18dfwHp5i
YRLFirjJk+ZPvD4aUxKAjJ9vLERC9eB7C8G+OABq3yU6tHPwvFu6AQDIE+Z3DQBGG3vMxv15TfVl
M7+V8D8BAG5+kff+kWiylxe75R4+Gk40GO/xmdLrayHAIurn6ImfV7iD6IbtAADkXwDsfvyHJEYH
kgDIKemXbYWf1vxSF4mH71ZMWUjvTy0CiXMq4uZXTiZKIkvcw4+lZvrjYX9id2JFOA4B/nNMjWT4
+fUS3fZPAADyJwB2L19M1Du4zDbIe81I/O9DfAhgR9JP6CTx0F3xD1QoADoZidcNUQAgUSSe/NNM
8UlCKLUBA2ISBGo0IETii414gpCRDIEfNAAAkP8AwF+359E7ZQOJSfOrCoQDFAiJCgAKMb84VA75
o13m5rcY/nP1zzw0aX5JCigVfsX+sH4DhqUUCCjnH03UHIiKJExuI7q0EQCAPAkBRwFw8OWV1P1B
IgsumyQdAFESSEoMDTKy/jqhP+tsTxn3a83vJACUef9sjaiBQNz4vUo0ILAuEhZ+LD8/kDMA9L7E
Ur8lO+QzAOz+/Y8GH8gGiYQ0t9SKqUNsKQUAVnp/1iObvuIAiZWpc/x2AUCcdzj177Vm/nQIsIh6
LqSE/8FfpiYlzQCwYsUKmjFjhuFx7r//frrxxhtxlUPeB8CeugUkRQaLbESiqUaLxhLTbnIUUMEE
5Y46AuncTjs99Bc6SBz+UeaHKXT8r1HvFeNyAkA6BBTzX3aA2PROywAY6O2iYKTC9jwMBAAUZwjw
t6eo//0t8bA61E9hFoyvnON+ZHFDBhIRQEj2YCAWTAwBjAHAxBZd89sNAK6emRPzAgBJvcr4P7Q0
c0oyGwByTeAABFAh5nccAGoUEEj4S0jk0bQQ0AJA8WJESmba+T/pvb/0KeOddnYCgG8AktYPp+77
Pm35swrB3sT7DVDkcX1IGQGgo72dKquq8vrS1zz/PE2vqcHVD3kTAEpPrwMBbRQQSvMgjwaYmFrB
V6r+R/YPYzMAlHzADjkSmD/JOgCymD8bAL73ve/RwoULC/ryEQ1AngMAf23jkoW6EOAeYyGmLKAR
WD+JUpAigdRS3DwiYD2dpuZ3CgCqun94NEnvhrIeP/aEPNyJZDlOlr0As2bNoqVLlxZ8ASxatIjm
zZsHJwAA3gAAF7+Z5/7/+XVWCKiRAIcAh0HKsKD6VWsfRgcAUrdEwguVRFvl8HqUPLy4oCVe2z9H
AOiLf4je7Ka3CIB8cwBGamjYTuPHT4AjAIDiA0AvEtACIG44fQhUiC1Zx/1GAOjbyyj8s4rMQh6J
TT3sXw+SdOw+QwBYhkAkh8KgLgIAwwIAwFMASI8G9CIBLQhURSvqE50to2BswBIA2Eq5p18Xi5fx
isUU8xOv3MMhkCjbxSv48HX60nX/KAwAVkDQo1kIZLId2AkIrFq1is455xy4AwAoPgBUtb7yHHX/
8+9ZISBIr8sfSCQhyqMG0RQEHAB9zQKFbhOVSj5ioEqp4sMhwAt4cAiwRDEP5fV8H8HIdpLO3mwP
BKy0nQkAeNsKguDIxYFoAADwDABUNT3yM5LknljQLLVPgkB8TX5eUCCgAEEFgQEElAjgWlIKeIis
Ol7RJ1HEQw4llAIerFo+kAyEZOGOrg6SrlrvHgAsVgWura2lRx991PYL5Lvf/S4tWLAATgEAvAEA
VfuWLkiJBljXG8omPBaQFAAEEktsTaOBOXLIX1GdUsRDrejDC3goEBimqd7T20Ns1H6SvrbNFQjk
Whb8uOOOo82bN9ve3vw9J02aBMf4HAKeujUYf9+m3y4kQfyAxO5m2fTx42QFQThRYISDoD5A0h+q
k4U8lH38LKwszdUW8FBKefEKPuHeRIP1EH3zddvvAmQHALhyWSKMYQFUsgBQ1b/3fTr4p1uTj7Ug
EIKJwiI6IAg8FSZx/fCUffza/fspe/crwsq+fXXPPs1J9LIOQ6CQG4OccsopVF9fb3t7L1++nC68
8EJPXswjR46kpqam5GN+nvx8oTIGgKq25+6jru0vpoAgazTQHiS2+FC55x+qmF9vD7/AIwVNAQ9G
PRQYKkcAN20zBUChELDj7sB+SRJOnz6d1q1bhyGMnwGQBMGqRdT10WsZ0YAKAjVRqIDgjs/IQ4CK
rJt4+KYdoUJMFvcMzN1GbETf4AvMIHBDOL6+gNcHjAxJri2gW97NCgg7bw++ZcsWmjx5clmCwOoF
jD0QhZm/ZACgan/dNUpuQG9YoEIg/PMjaKAnZgoAdduuEO2mwMLtmS8ygsC3Asn1BTSkUjG/cncg
dbbhqx8Sfe5Aqum1sgkAqpxKEq5fv56mTJni+YsYOQwfAUA9dtODMwyHBRwEgUXHm76PMhSQeil8
bwNR2GCBUToEZvYp9wpQbhSiXV8wrHrwxiB9/URXZ1m6bDMAuMopSZjrpqhPDh6gocMPgfP9AgBV
vft3UssfbtIdFvDcgBkE+M690ILtqaF/Ngh0MpKuFZQpRnV9QfymIYNTi0JV4oYgQ/eTdP5W1wBg
ddycr+rq6pTNSl68gPkwaNOmTXC+3wCgqq9xOzUvv013WNDTVkGVdUdn/E34yg9JmJoI0y0m9aRf
hkj6e4zEyLCM6UVhWCBlalGZVpz9husAUDVx4kRqaGiw/X0b9+ymw0aN9tQFjGFAYW1Y8gBQ1fn6
U9S+4feGwwIhHJ8GZCEZDvLz6gIixkP48ID5Z763igY2xpIzDCnTixXBlKlFIdJJdLNOBMDvOdg3
4DgAuAopMFLM7/+BBx6gOXPmAAAAQH46sOwGGmht1B0WcBiwkKCAQK1ElAQBX0acLYPfFKL++aMM
Zxh4ToFVR5SS4IFYB9F33h80fUrI4g4AVJVikjDXKAAAAAAyzk9NFHIQhALy+D0sZkwZqtGACgIz
CPTOmkCiVKnfkJqpxeAdW42jCpcBwFVqScJcAeDlhUwAQDHzA61N1LzsOt1oQOm1dYYFypCA9eqD
YGM1dd97lCEAlMii2mBasYgAUOVUktDuUuXIAwAA9oKgq4Oal8w0BYGlYUF7kLrn6C/AUZKLX2nJ
3nZt/dQtDRT1zkBODQs++uA9OmLsOACgxAAg+aWx2zaupq4XlySHBaIMAe0iopyGBTIIBh4ZSYGD
8u+uPEj0mQ5rbecBAHB5OUm448P36cijxgMALsDTVwBQpU0UWhkWKA1lcbYgeygyoNQo9AIAnI4G
Cl2mm+uF3N/TKX+XMRAAEYD1z7D/4Utlk/dkDAuMZguy5gdMjJ88rscAoLaF1zYY5QqAs846i555
5hm4HzmA3NX0q0sUEFgdFiTzA/kYwoMAULVhwwY6+eSTPQEC5AEAAFelTRSaLSJKyQ+UEQCcHhbk
UqqcLwbii4IAAADAVXVsXkvd9Q9mDAu0+QHd2YIyAoAKxHBFZdGigXyGJQAAAGCbeDGS3h0vGNYd
yHdYoAIgdsJSYpWf9nw7nHTSSfTmm2/a/r5WSpXnOgwo5hbmUgaAL5OAVtW68vvUt2+r5WGBGQiS
ADj12bzGuY899hhdfvnlys9uVvh1aoNRtu28yAMAAJ7Rgd9ckDEs0M4WWM0PqACoOO0vpsfMJSnn
xnfS2nyQqg/5lGvDgm9/+9t0zz334NoEALwzLm59tDYJgvTZAuX5LPkBbn7luQk/JnbYiRnmOqPm
zILCbbe+F7dKlSMPAAB4EwSN26l11XzjuoTp5cpTvpwoiV94lC66tJZWrFhh63lNnTqVXn31VVfa
wK0NRsgDAACelfjxRmpefYfxbIEMgg939tApt75IB9p6XDknt78bDrEZM2Y49lmQBwAAPK+OpxdQ
95436IDYTlfc/Xdav725aOdSrO/GqdmCUmoDAMBH4m0wc+ZMR+7fV6oXv5NJQlyfAEDRLyqn1suX
28XvVJIQ1ycAUBQ5dUuucr74nUwSmokXJ+FFSgAAAMDVxoT5M7V2zRqqOfNMT7QFf+6B6y+lOQ89
gWsWACgvALS3tdGQykrPnp/bSULtNcpzEw/N/kbK7+f/YS2uWQAgu5yqoWenRowYQfv27SuJ9nSy
CpHRNbro4um6vwcAAICS7P2nTZtGf3326ZKufuNGkpDXJ3zitm8a/h4AAAA8DwA+xXjZZZeVbfs6
tcFI1U8vmuY7APju1mClfIFqxXf4LVu2rKSSjnZob+MeGjX6064D4MR/v5LOvKgWEQAAYCynimJM
mDCBtm58m0KxIeRn8alCJ/ZEWAEAogAAoKjDAFEUfdfbL168mObPn+/a8QAA5AA8nQcYM2YM7dy5
s+zajE+7nfqV04u6GpDruukn0thDh/luGAAAlAgAVLlZ2afUwngnAVCuUQAAYKO0JbicVqm0az53
7imGzIYA5QoBAKAEowBVXr/BRSnlLawCgGvslBq6aO53fAkAIiQBPXfRe7GyDS/84cVQv1Dzp+uW
ZaW90AoAKJNez2tJwlLp/Qsxv56+MusWmnrmvwEAAEBxdPPNN9Pdd99d1HM4++yzafXq1Z7+nm47
9xQaVhF1/Dgjjj6Brr7zbgDAL3JytVqptLvXen9eAPWK0z5PLTveLS6cf/u/nlvQBQB4wAC81861
pr0V8c1Aa9eu9RUA+MrJl9c+T4cdMTbleaOdfsWQl2YSAAAPGGDy5Mm0adMmx/bBu50kdKveH6/m
c99991lqby8BwCsQwGYgD/WAajs5VU/Q7VoAdkcBPIz/yzNPG94arNQA4AUIAAAOyY7bVDk1jeZm
Dbx8IcBhVV//quXbg5cqAKpGjaXr712CIUC5yc7bVDk1nnbre7Fy/muef56m19Q4eh5eBECxowBE
AB5q3GwFPZzaauzm2gG+D2Db9vdp7JFHFqUeIQCACKBk8gBGcipJuGjRIpo3b15Zfg98L0K2cl/F
1jFnnE9fv3YOAAAAWG8rJ4YFpVQw1Ex6lX29qnDlcJpbtxwAKDdt2bJFmd5zqq1qa2sdudXY1Vdf
TUuWLCnZdvdqqG+kYiYCkQPwWAP3drbnvFLMqaq5/D0nTZoE8zus2Q/9Ke+pTUQAZQaAfLf3OnVr
rVKqQlSK5udCEhAAsK29nLov4Z133km33347zA8AAAC5KJ9dcXa0V6mvHfCL+Yu9EAg5AIdl54Kg
XOXkrkQvfaelDACtirVtGBGAxyhr98adck4Slov5izkkAAA8BgAn5uOdShIWe+1AOQLAbQgAAA4r
n009TrWZU3cwLlap8nIFgFsQQA7ABeXT+zrdZuWSJCxnALgBAQDAo8OA9rY2xzfMOFW0w61hQUd7
O/3imvPL/trxEgQAgDICgCqnNhjV1dXRrFmzHDtvPsvxu5suBwAAgPIDQDHarNQ2GPE2WnxJja2G
WlX3IG1d82Re52M2p5/vcMXpMuMAgAcNVqw2c6qct1OlynMx1X/WrbQcVeVq1lx66XxA4GQUAAC4
JKuhthfay6m1Ax998B4dMXac6wDIx0BeeG+nAYAkoMviY+KlS5eWRFvxJFtlVZWnhwVWjHTl4iUZ
JcLtev9CjJkLBACAMlP6fHzjnt102KjRnjxXp6IBXpiUFyjNV7xM2j1XnZe3eb40fnDb9U8eXmlY
k9DIqMeefg6dP3tuxvN82nfqZw9NPn7tvQ4AAPJXDsPJaCAX48x7Yk3GefPrccoE/VyAnlmNjqdn
yqlHH0IDAz0Zz696pUEX8FY/i1ObhgAAKCe9914DTZgw0ZH3NrtO7EqeaXv+dC1fuykjR2EVANnA
kitc3IwGkASEPDMsaGjYnnEvgEJW++UKAD2jLvvRrbTnnTdN33vaF46m9uaPHQeA3SAAAKC8x+BO
lCrXXjOFLvW1AwCP3HELNW57y3MAsAsCAABUkJxaSfjTi6YV/B7lOASwGwIAAOR6KGlFQyIhuv3r
X7bdHDyPccnXPl+wSXOBy/W33UVXfnO2IwAoFAIAAGSb7K5C5FQUkG5Wr08DmmnslBq6aO53HIc2
AABZkl1JQjsAUA4LgZyKAgAAyNPDAjsAkK85vLQUGACASlaFlCq3CwC5GsRrm4GsKJ9dgwAA5Jom
TpxIDQ0Nll//qaoI3XrWqa72lCsf+jlte+HpvN43NnwkzXnoCdeNX0gUAABAriqXJKGdvb9fBABA
JSGzJCHMDwBAPlD6BXjnBV+mcCiEhgEAID+q3Kv8AgAQBAAAABAEAAAAEOQaAMKVw2lu3XLd63Pt
Hx+hDU88SMHY0IKO0dvXR5POOI9OPW+G7upDq1WMAADIl3LyZh+5VAUuVcgBABCigCxa8fp6qn9n
PwXCMVc/094dH9K5Z0yiiYeNoeOPGOPIMfTKnwEAEACQBgBVo488nlauq3f0s0w7YTy1tzUmH1/4
xZM90/sDAJDvIPDK9gZqbNmv/7vN+ygUG1LQ+/OtwKdNPly3MKiTADBbhgwAQACAThSQTX19nXTV
tT+gsy+upXHjxqeYhYf0L/1tHd1xxSyqGGftzs9e6/0BAAgQcElOjv0LqXcAAEC+BMBTb75lGKY7
IS/2/q4BABCA/BwFeNX8AADkewg8t3Eztfe0w/w5AgDDAMg1tTYfpIdmf8PRY9gdDYw5ZARNGT/e
s+Z3HQCAAFSI/vjzn9CHG9Y4eoyNO3bR9r27PN3r22X+PAHAAACoaHp43mxq2fGu48fh6/lXvf1G
Tn/jZJbfI+YvHACAAFSo+EKbu2ae4+oxORC27dlL7+9vUh6Prh5Kx4w+nIZVRF09jyKbPwMAiAKg
oslP24aLeTdg2wEACEB2iV9Hiy+pgfldMn/yf4AA5CW9t2UTLf/xTTC+c+a3HwCAAIShgTvGt6v3
NwIAIABheFCATvp6LdVcfKUXje88AAAByA09csct1LjtLd/09k6YPxsACoYAQAC5qfrnn6UXl9zl
6jE/V3MBnXvNDa4dz27zOw4AQAAqtlbVPUhb1zxZ8PvwAqTfuvd3RalBaIPx8wKAbRAADCCoaKbP
6nUrR4FrIUOg8wsVYC+aqQsyv1UAAAIQor/SM70lj+dydoAABAiUFgBYwS8ABCBAoLzC/kIAAAhA
gID3AcBsfyEgAAECJQEA5tiLAQIIEPAsAJhrfwQIQICApwDAXP9DgAACCIoOAFb0NwAIIEDAdQAw
z70RYAABAI4CwNskARggQMB2ADjuT4ZLDvIa4MsJAvnU6nf1/HCtQl4EQblAAACAAAEfQwAAgCAf
QwAAgCAfQwAAgCCfQiDf+/UBABAAUAYQAAAgyMcQAAAgyMcQAAAgCBAAACDIbggAAAAABAgAAAAA
hKEAcgAAAAQIAAAAAAQIAAAAAIR8AMb/AAAECAAAAAAECAAAAACEfAAAAABAgAAAAABAgAAAAABA
yAcAABAECAAAEIShAAAAQYAAAABBgAAAAEGAAAAAQWUAAQAAAIAAAQAAAIAwFAAAAAAIEAAAIAgQ
AAAgCPkAAACCAAEAAIIwFAAAIAgQAAAgCBAAACAIEAAAIKhsIQAAQBAgAABAEIYCAAAEAQIAAAQB
AgAABAECAAAE+QkCAAAEAQIAAARhKAAAQBAgAABAECAAAEAQIAAAQBAgkLf5AQAIKjUAGEEAAIAg
H0GgVP0IAECQdyAAAECQTyHAfHNQCAIEAAAIAgSK7EMAAIIAAAiCigSConoQAICg4kGg6P4DACCo
OBDwhPcAAAhyHwSe8R0AAEHuQcBzfgMAIMh5EHjWZ/8P8W/iYhnZ3V8AAAAASUVORK5CYIKJUE5H
DQoaCgAAAA1JSERSAAABAAAAAQAIBgAAAFxyqGYAACXWSURBVHja7Z0JnBTVtcbPrV6mZ2WLoMgm
kIBKcA1o4oZoNPoQo1EMqKBRSVCEaJRoNAtqouCC+tCIUUSjRONzxSAuhMSIEhUUWUQQRRgEZpgB
ZoaZ6a3evbV19TbTPVNVXd39fT/LLrp7uqpv1/e/5566CyMonyTzjSXsyy44L9bOOUIuFXP44oUg
yEX+ZDA9BBUvEBhMD0HFCwIG40NQ8YKAwfgQVLwgYDA+BBUvCBjMD0HFCwEG80NQ8UKAwfwQVLwQ
YDA/BBUvCBjMD0EAgCvML8uxQzHG0r4GQXnjPsbavNbTve4UBJhT5oeBIcgaeFgJAWa3+WF8CHIN
CJhjAIDxIciVIGCZAADmh6DChEC7AID5IaiwQcAsBwCMD0F5A4G0AOiwiwEACMo/CFgCAJhfL4go
tXy9kkLbVhAF64kkRh5fBQWOvYIkfznKByo8ABSz+cN7d1LDhwtIirYQ8zBiksQ3XqgSUzb+66j7
6i9FgWN+SZwIuGoh10CAofbPXA2r/0Gh7f9VSk3i/5M8Ykfij5JhegUAHt38klrCYp+puJV6jebb
kbhqITdAoHMAKHTzR1uaqP6d/yWKNJNaoau1uTC6ML3k1Wt9zfweKVbr810y1f56wKXA49BpCUUP
QQCAKxTiYf2edx+K1fK68fVHzfzKo1dSTa6YP9YEEP9TSlaSFOMzAwCxVhcbMhVXLZRrCHQcAIVk
fjkcpNql9xEL7zfMrphfiq/1hbklj0cL87nJ9X2JqSDwxEJ+5Y8lfZ8l33cZeA2uWCjnUQAr1tpf
jkao5o3ZxHh4r1TQImNv1PaxGt8cAYgaX6/tSTE/M2CgmFwzu/ZHhvkNEOhFLkeJ+vyMyBvAVQvl
HwDy2fytu7fRnuXzeAVtMrmk1vjMXOubjc9MIb4n1u4nTyzbn2x6Lez3mJ4Xmyi7KN+qTiLqPgxX
LZRTCBQNAJq+XEUNa15UvanV1uZ9Zuwn1/xMB4Ap26++QdIMT/Hm19v/ibW/rP1PAKDyeKKex+CK
hQAAO7V33TJq/uJttRYXiTvN1B4pucbX32PsmyEg6e16Sf1gLdlHUoLxmfa8AgHxnGl9TNkoQKKu
P+AAOBpXLAQA2KEdS+7l8X59zPRamJ9ofP21uFpf0vbN/aSMMF6KN7seCZhreqYZP/HH0NfyFeX3
rZM5ANAfAAIALFXdqteo9ev31XBeioX55qy+JMXX+BKLf54l1djavz16bx5mqullrRTl2P1+lvSr
JJfygaOJeh2BKxYCAKxQcO8uql32oFYhszjTS2bTGxFBCgikM75sKi29FldCe9lU25uKVL8VSAlR
gLnY+pxJdBAAAAEAnVb1S7fGEnomwyeF+wnNASPx157xxWMkot6+E5v+JDM9GuG/qVTjfgyDHOo/
B44l6j0cVywEAHS4nf/2nynSsE01tlHjx9f6ZsObmwV6+79N44tsfTQSM39EA0A0qkUAeinKyWZn
5hJmyUV+2IVEBwMAEADQoXB/19IHTMYnY99c6xu3+ySWcPsvhfETa/uovkVjAIhqm74vykGmhIjA
HAmwFBDQkonfHUd0yPdwxUIAQDba/o9ZJAf3JdT4CbW+Oelnep+R4EtV4+vGj4Tjja/vG4+yZnzT
PunPyYm/RszwetJQu2sgDz2J2LDzccVCAECGB6VtvK3PTLW9UeuzhNpeShH+m2v9xFBfhPbC+Mpm
MrwBANkEATmWC5BNxpcTi1E7Ril/XxX/uy6tRJVBCreEKNgSJn+/KeTtdw6uWAgAaE91qxbT/q/e
jQv104X8iZFBylrfbHxh6rDZ/CbjR6IJtb+pCZAoL//Qwfu5yUNtzLUsU4ibP9QMAEAAQEba9uIt
ymO88cUteZYEAykBBHHZfbPx9fBemD4cju1HEkJ/czSQ+J17Bon6748vxbjQPx0AQhTaDwBAAEDb
x+Cmq375d6Y++mptr9b6FFfTszgImG7tpaz1hekTan1z7S9ei4Zj0YFZQxq1Gp4lGz9VwbMUAGgG
ACAAoE217q6mmn8/HN/eN93bN5J+SYnANtr6ou0eDiXU/PoWjYdB1BTi92wh6tccb/JUxs9omVUA
AAIA2tTe9e9Qw2dLDPN7TDW8h8Wb33iNpTG/UetrNb5uegECI/SPxGf/9VIZvkdt17M0Rs80CkgF
gKYQAAABAIna/o/ZFG3da4zWS5Xs83hSdPoxh/yJtb5e2yu1f0gN8RUghOLDf72277M/tdkzMX67
ay1zAOzXANCfA6AvAAABAIr0ZJ+55jebPynD70nR3jebXw/rdfMrhk9s/4e1kXmtRH2bUnTeacf8
6YzP0tBAAKApCABAAEA686eq+aVUWyrzJ4X8ofhHveYPa+F+gENiaH1CP36W3vzi85f6iVbxrZ5v
ZTz8GMKfO7+OyJemZM2KigiAA6ARAIAAgJQ1v9n06c2v9fJLZf5wQq0f1mr9iOnfxI0/vC7FIJ40
5g/znWnc4T5t83pjjx4PKbclRI+js/YSHVOXXMJyQgQAAEAAgPkePyVl880QYInPp0v2hUIJ5g+Z
Qn7tteG1cfP0x2bxSdOHfzqHRQuv7Uu44f380Sc2r/ro9WgQ8GrTf0lqk+KGDamLVAdAQxAAgFwB
gZwBIFXNrxs8Xc3vSezZp5tfbHrtHgqqbXsdBnoeoIq38fs2pDc6Y8nPXc4/y8uN7i/hm099VADg
U/8tQCCgYEQB2vmI24jXruXPRZMB0AgAQEUOgOpXbyc53JK6X39bAEhV86c0f1Cr+bXE36E742v6
9mp/8fhoK9FybuySUpIV0wdU8wvDe7UIwO9VNhbwqdGAHgEonYj4saetNpeamgMAAKBiBkDNu89Q
6651cbPzqBn9NjL/UpqEn9n84WAMArr5vc1EA3enrt3bqv1FmuCyIMl+bnq+yYr5S9SFPc05ABEB
iKYB35jfo2zk1ZKQQX78A3jEcdHnJmgJALRSaB8AABUhAGr/+yK1VH+ktfvTJfwoJQTSJvxCpva+
OQfQu4aoojW5ps+g9pcncYhEfSR7y5SwX/aUqE0Bpb3vU0N+ownAzS8gEBCPXqXzEGNRFUhBfvxp
H8c3ARoAAKgIAbB/63qq+/AZ5VBxg3r4/1KZ3wyA9OYPxif9Qtr+4G1th/ftZP6jE/i+x8+NX6oC
QOLmlwQQvGIZIDXcFysDGVEAbwaUiduCfv4yBwAPIRgT58IBcPEGoh7aoCE5ys0PAEDuML9jAFAG
9rzw+9g6Gp4UiT9Pcr9+8VzKQT1KiB9MaPdrzYBBWztkevNjdIJXMb0CAI+IAITxxXNe/eRVAIjF
QQUMAhwAIiIo5Y8+sYBIlH/XoAICKmkiunpjrAmwrwUAgIoLANXP/lbxrvCOMkGHV233eyRKmfDz
mAf2JJpfZNj1sN+IAETHHl7b9t/adqifzvTm5+oYRaaWKmG/EvpLJarxSQBAWfM7tj6AWClItPt9
/LFEywEIAPh4FOCJ8LeEOCT4ed3weawJICKAva0AAFQcANj+/CySQ02qbzwqBJTaXjx6TWY3uvZK
RnMgOeknm8xv7tjTTNRnW4K5Oxb+UzOvt6+s4mbnIT8rVUN/JgDgEY0XFQD6+wXQxHRESgJQ0jam
5gG8IgrgTYGSVmK/2UzGXQAAACoaAPD3bX9mpvLxzKMCQF1iW5hfUvrPKJtHSmr/p2z362G+OfHX
rZqH3vtN03GnAkAGUDCBIHRxD35IHtKzEhUEfF+W+UnLUlLpie+kvFXU/CV841Bjfh0AEZKO2Ec0
Yaf6/mgUAICKJwlY95+XqfnLT7gRZMP4+qNoBniF8XltqUQC3oQx/akG9yghv1778/0u27n5G03m
zqLWb+O50MU9+aH9qvEFBITD5fSFysSwYSX018J/ZVMjAM+dW9R5AeXsAJDqR8z3JdmhIgPA9gV3
COcqAFDNr66yK3lkoxkg6eb3aclAb4rQX5/MQze/AEFpDVHVbpOJLQIA/y94/YEk71SNL1MgFva3
VZC68cX5C/OLCMDDAfDw17E+CxkA4MUXX6Tzzjsv7XHmzp1LU6ZMwVUO5QEAnhAAiJoiANX0TE+k
C+N71ee82r6S+WcpQn+jh5+YkquBqPuWhNCdsk8AttEUaL34EH54EQWUZFYokgYAcRvQF1GSgN5x
e4mdsSduWfC2ABAOh8nn89mSiIUAAOebAMteouDmNWoCUNLzAFoCUAeCV48E9ORg/LLcSuhvHtwj
85C/2+YUxqbO3wGIGwEoUcukIWr4n1FJyurtP6Xm521/X5i8T2yLmd+4DZgeANkmcAACyN1JQK4d
j92hepEDgMxJQI8a7utRgbpJ/AvIyp0Apo2wZeZhvOKx+5rkxJ4dAOD7kQ+7UfC+PpmWCjd/RM38
80f/01tjRWtaaixdP4DGxkaqrKzs0I/+z3/+k0455RRc/ZD7APDNo7erbX89ClDyAGozQG/z61EA
01b2NToMCRhEwyoExNb1E/M3tR0ASiqi2kctNwzNLAIQ5vcHqeTpr1Pxoc2egDfddBPdeeednfrx
EQ1ArgOAHInQjsfvUmt2r7qUtjA7aZ3olAjAF7vvzwwQcENxw0giiRgJktRlVcKCnBYAIJPEoPY3
Lb/7Dsmf+9so+DAFntlISSkD89qB0fRjAS677DJ64oknOn0BCIjMmDEDTgAA3AEApTndUE+1Cx9W
ze9lRnhvhP5aVKDeKZCUwTSqdzkA5CB5u65SateEb5oZAHjgQEvLiNZXEPXi+2P3EnUJZdY1OM3r
ckjrpyCe90VjNwlYmmI1NwHaGA3YkRxAOm3atIkGDRoERwAAuQeA9kf0zbw/mYzP1NuDXoot4WX0
FRD2UgfVSNRInso1KiC8WUQAtfzD7uLGD2gTepSUxIbwioOcUUt0WG378wCm6mBErP2JQVNFAaIJ
0JB+PgArAYBmAQDgLgBoiuyrp5pnH9b6Bmihvw4EDQJMmfxDdJ6JkKdkhfq66G3nUYGhJBTbugvw
Kn99WSk3vzB+gKg0oAJAh4BHa2fw5gVN/iTzSUHTzg6cAQGM+QDanhDEDgi89tprdNZZZ8EdAEDu
AaBr37tLqOWzj2I1viTHIgHxnNLz/gNu+IjS0043vr4vgKCE3okA2Me3W/gLgQqSS8pUAJRoIAho
Q3bF+H1xIDFxRw/eJDhnXerQP10U0F7Nz9KUaLT9OQGj0Sjnk8eWiwPRAADgGgDoqlkwm1f0oVgE
oN0dYNTK3bBKNbu4v+7RIgCts40AgBoVUHxPwMkyyYFKkv1l2nReJepsPiXc+AoASoiV8seAhx+P
A6Clheiy9zKr7duq+Vk74b/q7oxnBR4/fjwtXLjQ8gvkN7/5Dd1+++1wCgDgDgDo2vX4n5TRgOpd
AG7i5g/VbsGixvdoNb94zRtVcgFMiwKM6EAM2BOjgsVQ3hJe+/vKlLH85BUTeXDz69N3cfOzygCx
Mp86XFcMI+5VQ3TmhvajADMQEk3PWNvhv5YHyXZa8COOOIJWr15teXmvW7eODj30UDimyCHgrrUB
5Sjtms9BEP6S5OAetWstD/u9/JEk0owfVWblIjGeQDO+eJ9yi3EFbzgs5LW/lwPAGyDZI27b+dQh
h2LyDjFsV8zeIyBQ7tUG7HAIEI8CJq9sfxWgdIZvd0kwEwCMhUGu5gAYk1GxtLa2UiAQQLMAKnAA
aArv3Ex1z92onqCk1/Ca4XlzQI0I1O7Dqvm1f79UQvJ7Vdz4ZSRLHABMDObx6r2K1LH7AgABiUcA
HrU54Y8ozQ32y9UZJPs6sCBorNA6vTbg8ccfT++//77l5f3cc8/RBRdc4MqLuWfPnlRTU2P8+9xz
z1UGTEEFDABdDUvup+bP31HOUjG9Uevrpo/BQXls5DX8Xb248csoKmbykX3xY/glZYg/3ySSAkzd
90VIKmvhAPgsffif7t9i2n8xaMkjJ4MhXRKwk6sDi7KXJMmW8nZTNDB69GhaunRp2tc//vhjpXkE
FTAAdO1dNItav/yvCgItCvAqs3RpIFBuE6qj8Ty/G8A9GeDeLE0Tm8uK8SVh/oBIJnIATN9ETCwQ
monpxVe/mh88IG4zBtRHsVaASFBct4nvR9MnAfUmwP5wp5cH//TTT2n48OEFCYJML+A33niDTj/9
dDi+EJKAmWj341dQpGmP2q3Yl9As0PICvnv7kRysVIbypv3SIpooESP2ohwaYfLO2pB5zX8l30q5
6cvK+VbGN62/gT6Md9TXRENr40N/MwBEBGABAHQNGzaM1q5da3lZr1y5ko466ijXX8TIYRQRANQw
OkK7HhqnRvQe0y1B7VGZtXvW4WrbP+235u/1h5UJO/z3cPP75czC/0uCJJd3IbmEm19sZQElCmDl
/LGihJhgTmuI6Ir3U0cBAgAt1gJAKBgMUklJiS3F7fRvLW5T/vGPf8z4/XV1ddStWzc4v2gAoClc
8zXV/e06teeg1ldA7y3oEU2B2Ue2UUiyMluv/w889O8ZSuhSnAYColvCZB/JgSqSfaXKikFK/4JS
bnzRt6BLGbFS0begVZ2p6NwUtbLoB9AS5lGAtQDQNWrUKFq2bJnlZT1//nyaNGmSKy/gww8/nNas
WQPnFxsAdIV2bKL6v//auE0oeWOJQk9jCUnzhsRn6sX0fRO/Ium4OvXWoehWTCw1BEwlFP1fL8kf
VlDUX6lNF+5Xby/6xG1FvlVyCJSLtQLE+IVmoikrUxWcYn4BATsAoGvo0KG0YcMGyz+3urqaevfu
7aoLGM2AzpVh3gNA1/4PXqLG9/+qJQVlpa+AeqtQNvUV0DoPaftMf4/PBIE0TYDwPeUkf1rBzV+h
TRjqVe8AKLMAe9TbiuVifQBxmzJI7MbVySWrNAHsB4BQQ0MDVVVV5V2z4MEHH6Rrr70WAAAAOqbd
C35BkYYao8uwmHfQfNvQ49f+Labu9rAYDPzqZCXpICDv9FDo130oysr49/dT3B0GkX8IMA4ApgKg
rJmkmzcapjeHH6GWiCMA0GVXknD58uVKvwQ3RAEAAACQFGrvmjuOGzqqNQu024TakGLF9Ho3YjGV
t3jdr/crYCnG96sgaL1sEEWpglLdXhS9CqVSNbnovf1zokAk4ZxMAGh1DgBKMykUIr/fnzfRQLYA
eP755+n888+H8wGAeEX21fCI4Oem5CAl9CA0PXo1KPhNg4wSSimyupKCcwanLkgOGxbg7f/yVvLN
+iJNwUW5+SPK5u/LAdDf2YVBzjjjDOXeudV64IEHaOrUqcgDAADuVLS5gWofm6TORqSNJTBA4FXB
QN7YCEMlJ+Aho5kQ991bvNRy9XdTFDqv1S/fStIP9rQZmSgACOYGALrsGmD01VdfUf/+/QGAPAOA
XCyF3bx6CTW+86jaHFCWJZONJKDRnVgfZqw3CzxqMyHuLoFQk0ThBQdStM5P3om1JPVrTAj3U5ac
KwCgnH5TE1VUVLiyWbBlyxYaMGAAAOAAPIsKALrq/notRRuqYxDw6bkBim8O6HAwPW8UW6blLJuJ
wAEQjLoCAHZHA2+99ZbSn9+pC1mMmLQrz4EIoBBpy79DzSPjeWGFlK7EHh8zmgNMv3Wo3TUgZQ4C
rXngVZsH2R2L4gEQcg8AlNxGJEJer9dV0UC2ADjzzDNp8eLFcD9yANmr9uFxSrdgpq1WHDfaUO83
YEQEZHQ/JpYtBIT5ZdcBQJcYamzXrb1srxnkAQAARxXdv4fqFlxhmN/cFNCbB3F5Am9sToI01X3K
qEMBQNidALC7WbBx40YaPHhwRu+dNm2acncBAAAAHFXL2qXU+J+HtGaBWuvrMxCJ3r/67UTS5ifU
+xjELSDcVhJQA4Cv71Ty9T/bteXQ3NxMZWK0Y46igY5MjgoAAACWqeGN+yn41b/VaMBc++tzD3gT
Hj16l+L07X8FAGGxRan0yMeJVfR2fTkcc8wxytBgq/XKK6/QmDFjLG0GrFixgkaMGAEAIAlonfa9
fAuFdq6P1fbm5oAnAQ5Gs0BOCwEFAJEolf3gH+oiCFnqmWeeoQkTJij7t956K82cOdORchCrDG3e
vNn6/EttLfXo0QN5AADA3dr9lwtJTDscm4mIku4aSNrMxWqnIjne33pX4IgGgBNeb/eY2STlnPhN
6uvrqXv37o41C371q1/RPffcg2sTAHCHoi2NVP/kRNMgo6gpAjCNNTCaBdpMRSYICABIg2aSp9ex
cZ+9Z88e5b55Z8Jtp34XuwYYiXH9Yny/+ftkO/8hAAAA2K7wjs9p7ys3ac0C06zEKSCg307Uo4Fw
1E/ysc/RJZdcQs8++6yl53XcccfRe++950gZODVVebbNABE1jRw5EgAAAOxXaOuntO/136nNAGNK
MjmWFOT7G79ppFHXv0u1e4OOnJPTv81LL71EP/7xj237LsgDAACuV8Oi2yi0cxXta2mlCQ+uoOUb
dufsXHL129h1tyCfygAAKKZ8QDRKl19+OS1YsMBV55XL32bv3r3UtWtXAAAAKDzZuSBHoV38diUJ
cX0CADmRXUtyFfLFb+dU5e1JdCOeM2cOAAAAOFuYMH+ylixZoozUc0NZiFGPc6+5hK59+BlcswBA
YQFAzAJs1wQfVsjpJKH5Gm3YU08P/fwnca/P+NvbuGYBgLYl1p0TE1u4WQcccADt2rUrL8qzsbGR
KisrHQXAXRelnpQEAAAA8rL2P+2002jRokU5a19bIbuGG5sl5if824zL074OAAAArgfAwoUL6aKL
LirY8rVrgJGuO8edWnQAKLqlweyUXUtspdL48ePpySefzHoMfL5r586ddOCBBzoOgKPPnUinX3Qp
IgAAIL3smhRjyJAh9PHHH9vWlz5fJMYTTJw40fIxEZkAAFEAAJDTZoDoSZhPtxit0KxZs2jGjBmO
HQ8AQA7A1XmAPn360NatWwuuzESX4JNOOsn2RF97umrUUTSwZ7e0r3/vJz+jU38yHgAAAHIDAF23
3HIL3XbbbXlZPmLdQZGofOGFF1x3bleffiz17V5VdFEAAGChnnrqKbr0UmeSRflSruIW2yGHHOL6
82yvCVCoEAAA8jAK0HXOOefQyy+/jLJwEABCA0aeRuN+eVNRAoAISUDXXfQfffQRHX300a4qBzHx
h5gApNDMn6jrn1pMXp8fAAAAclvruS1JmC+1/58uHGXpuZ44cTp9/0djAAAAIDe6/vrr6e67787p
OYwdO1aZy9/NmvE/36du5fb3regx8HC64o8PAADFIjt7q+VLubut9hcToE74/hHUVL0xp+cx7fFX
KWDTCkoAQB5HAddddx3de++9lp+HGAz05ptvFhUABg4cSP/617+UJpFZ6Ub65ST6cNGdBADABQYY
Pnw4ffLJJ7aNg1++fLltK/mmkljBRww9tltTp06l+++/P6PydhMA3AIBDAZyUQ2ol1NHFrrMRE7P
BWB1FHDiiSfSq6++Sl26dOnQ37sNAG6AAABg1w87Y4bSl70z5XTBBRfQ888/b/m5TZkyhebOnetq
CAhYiagl0+XB8xUAlQcOoClzHkMToNBk5TJVdrWnnfpdMjn/pUuX0qhRo2w9DzcCINdRACIAFxXu
008/rYzzTyW7hho72XdAzPwrJvTo27cvlZeXO/57AACIAPImD5BOdiUJZ8+erayuW4ja/tVmeurX
V7r2/IaMGkvnTr4WAAAAMi8rO5oF+TRhaHvas7uWHrl6XF6cq7+8C/3ysRcAgELT+vXr6bDDDrOt
XT5p0iRblhoTnzt//vy8LXe3hvrpVH5AH7rmwQWuNz8A4EAB79+/n0pLS7P6G7tmzRUAE/Mcwvz2
6ucPPUdduvdABAAAkLIqzuLFi7M+jl1La+XTLET5aH4hJAEBAMvK64QTTqB3333X8u8xc+ZMuvXW
W2F+AAAAyEY/+tGP6PXXXyenyyvf+w5ko1kTziA5Es7L6yPXHYGQA7BZVnYIylYio9+rV6+CB0E+
1/5mHfDtI+jy2+51NQQAAAcoK5YWHzlypGXHtytJKAYviUFMudTdl55NkWBLQV0vTjcJAACXAcCO
+/FiNl6/3/ppq3Ldd6BQav9cQgAAsFkdGdRjV5mNHj1a6XdvtW6++Wa64447AIA8gwByAA6oI7Wv
3WVWKEnCQgaAExAAAFzaDNi3bx9VVlbaek719fXUvXv3vG0WNDc10gM/G1vw146bIAAAOASApqYm
W0b/pZJdA4weeeQRuuqqq2w77907vqG/TL+4syGL+HHsOUGLPhsAKEIA5KLM8m2AkSijWT89zVJD
LXr0AVr7dscWWul28CF01T1/Sd9cEWsPdKCMR115I40YfQYAUEwQyFWZjRkzhhYtWmT5506fPp3u
u+++nOYArpn3ApVXdbH8c7OtpTuSt7AzCgAAHFKmobYbymvYsGG0du1ayz93y5Yt1K9fP8cB0BED
3X3JWRQJtdry2XYCxs6oDwDopCZPnkzz5s3Li7JqbGy0JRFpZbMgEyNNmvUY9eo3wJbP74wxs4EA
AFBgEvPfLVu2zPj39u3b6aCDDnLludrVk3DOnDk0bdq0Dv99sKWF7pt0dofNM2JQhbE/+9EX6eRT
T8/KqENPGUNjfz49+byCQTrh0Njdlf9+0dipnADzeOnGp5cAAFD+5DDsjAZm/fR0fk1FM6s5F76V
ZDIx7fpx365K+f5UZk0HgFRgOe47PSgaSW42LFq+iXr2OrDDUYBdg4YAACgriUk9Bw0aZMtnt3ed
WJU8M9f8ifr7259S/wGHZFRTJ362gNLIwVVpPzsbuDjZHEASEMpadiUJN27cmLQWQGeG+2YLAFkO
0Qeb42vwJ/9wA32zfmW7nz362O9QQ/122wFgNQgAAKhDsmuqcvM109muvlYAYMHvf0U7PlvV7mef
euwQaqyvdgwAVkEAAIA6pREjRtAHH3xg+efeKULvTsrRJkCUNwG+XeUoAKyAAAAAOR5KZqLyEh/d
eu6Jlpvjq82b6MLTj+y0SbOBy5Rfz6ZJV/7CFgB0FgIAAGSZqqurk5bldmMUoJq13Lik73rk/2jU
aam726a9DXjy2TT2F9clPR8Oh+n7Q7q2CRU1shjFDy9ZUk4DRoymcdfdbDu0AQAoI1nVd8AKABRC
RyC7ogAAAHJ1s8AKAHTUHJlON+ZEV2AAAMpbdWaqcqsAkK1B3DYYKBOdcvn1NPKHZwEAkDslVhna
sGFDxu/vXlFKN559vKM15St/vo/WL+vYaMjy7j3pmocWOm78zkQBAADkqGpqaqhnz56O1/5tXJ2m
y9rqj7ZxshEAAMpntdeT0BnzF54AACivlHgBzjz/ZPJ7PSgYAAAqRhX6LL8AAAQBAAAABAEAAAAE
OQaAQFV3mjbv7ymvz7efXUArFs4lb2lVp44RCTbT0FPPo5N+fCF96+DkuQ9bm/fTnMvGAAAQlEp2
LvZx7V9eptKKioKGHAAAIQpoQ//3wQr6z7pa8pcEHP1OO7dtoTEnH06DevamI/v3teUYNy58K3tD
AwBQsQFA10H9v0svL33P1u9y6pGDqLFhp/Hv87830rZjYSwABAi0o/98vol27t2d4hWJ3lmzg0pK
OzfDUTjYSicM651yYlBhm/O/d5w9+Y2uPWnanxcCABAAkE0U0JZCoSa6bPJv6ZwLJ1C/QYNJkmJj
92uqt9K/3n6Tfj/xZ1Q2sDyjz3Nb7Q8AQICAQxpwwEF0zIB+tnz2pNnzqVfffgAAVFjKZv7/bPXK
ypUUioQc+y5urP0dAwAgABVzFOBW8wMAUNFDYMnqNdTY2gTzZwkANAMgx7Rndy09cvU4W49hdTTQ
u9u36PjBg1xrfscBAAhAndFzc+6kL99/09ZjrKv+htZv/7qTn2LfrT4rzd9BADAAAMqZHr1pKtV9
uc7247SGw7Ro1UdZ/c2hvfvRYQfbv7pzDs3feQAAAlBnFeHmvPviMxw9ZigSoc+276Avdu1Q/n1Q
167c8AdTVamz3YlzbP4kACAKgHKmYho2nMvVgC0HACAAWSVxHc366WkF+/0kr59u+Oti15jf+B8g
ALlJX6z9lJ6/bTpqffvMbz0AAAEITQNnjG9V7Z8OAIAA5DpFoxGaPf6HeXGuR429lH7404luNL79
AAAEICc0//c30K7PVrrmfBiT6MaFbzpwHOvM3xYAOg0BgAByUiveXEzLHrvb0WMeOvo8OufKqx2E
jLXmtx0AgACUa732xDxa8/qznf6ckqoedNU9j1FZZWUOogvLliPLCgCWQQAwgKCcmb5Nr2dyFLgW
Sgt0caEC7DkzdafMnykAAAEI0V/+mT4jj2dzdoAABAjkFwBYp98ACECAQGGF/Z0BACAAAQLuBwCz
/I2AAAQI5AUAmG1vBgggQMC1AGCO/REgAAECrgIAc/wPAQIIIMg5AFjOPwAggAABxwHAXPdBgAEE
ANgKAHeTBGCAAAHLAWC7PxkuOchtgC8kCHRkrn5Hzw/XKuRGEBQKBAAACBAoYggAABBUxBAAACCo
iCEAAEBQkUKgo+v1AQAQAFAAEAAAIKiIIQAAQFARQwAAgCBAAACAIKshAAAAABAgAAAAABCaAsgB
AAAQIAAAAAAQIAAAAAAQ8gFo/wMAECAAAAAAECAAAAAAEPIBAAAAAAECAAAAAAECAAAAACEfAABA
ECAAAEAQmgIAAAQBAgAABAECAAAEAQIAAAQVAAQAAAAAAgQAAAAAQlMAAAAAIEAAAIAgQAAAgCDk
AwAACAIEAAAIQlMAAIAgQAAAgCBAAACAIEAAAICggoUAAABBgAAAAEFoCgAAEAQIAAAQBAgAABAE
CAAAEFRMEAAAIAgQAAAgCE0BAACCAAEAAIIAAQAAggABAACCAIEOmx8AgKB8A0A6CAAAEFREEMhX
PwIAEOQeCAAAEFSkEGBFc1AIAgQAAAgCBHLsQwAAggAACIJyBIKcehAAgKDcQSDn/gMAICg3EHCF
9wAACHIeBK7xHQAAQc5BwHV+AwAgyH4QuNZn/w/qrgaAm2FqQAAAAABJRU5ErkJggolQTkcNChoK
AAAADUlIRFIAAAEAAAABAAgGAAAAXHKoZgAAJidJREFUeNrtnQt8FNXZ/5+ZvSYh4VaDIjeBFlSK
14LWeEG0Wv0jVqtYUEGr0qII1SrV6tu+qK2CF9QXrVhFtEq1vl6xiBdKXwWlKihyEUEUIQgkJEAS
kuxt/ufMbWdvyV5mZmd3f7+P4052w+7syfy+z3OeOeeMQFAh6X221cTtv++A46rp5Bghh0qw+eSF
ICg7sBYkAGB6CHIwEASYHoJKFwQCjA9BpQsCAcaHoNIFgQDjQ1DpgkCA+SGodCEgwPwQVLoQEGB+
CCpdCAgwPwSVLggEmB+CAABHmF+SpJP0AxOE5aleg6BCUfx5HH8+p3rdLggIdpkfBoYgc+BhJgQE
q80P40OQY0BQYxsAYHwIciQIatIBAMwPQcUJgU4BAPNDUHGDoMZ0AMD4EFQwEEgJgKyjPwAAQYUH
AVMAAPNrDRGhtm9XUXD7SqJAI5EokMvThfzHX0WitwLtAxUfAErZ/KF9u6jp4wUkRtpIcAkkiCLb
WKOKgryxv46yr/ylyH/cb4gRAWct5BgICIj+6atpzT8puOM/3MssuAskuviOyB5F3fQyAFya+UX5
d+V9QcGt2Gs0247GWQs5AQK5AaDYzR9pa6HG9/6HKNxKSkBXojk3Oje96Naivmp+lxiN+myXDNFf
3VHgcfg05TkIAgCcpSBL6/cufyQa5TXja4+q+eVHt6iYXDZ/tAvA/yf7WxRl4ws6AKK9LmHIVJy1
UL4hkD0Aisn8UihA9UsfICF0QDe7bH4xNupzc4sul5rmM5Nr+6KggMAVTfnlfyxq+0K8/4kGXocz
Fsp7FiCUavSXImGqe2s2CSy9lwM0r9jr0T4a8Y0ZAI/4WrQn2fyCDgPZ5KrZ1X+km18HgdbkUoSo
zy+J3H6ctVDhAaCQzd++ZzvtXTGPBWiDyUUl4gvGqG80vmBI8V3Rfj+5otX+RNOrab/L8DzfJIko
wraqU4h6DMNZC+UVAiUDgJavV1PT2pcVb6rR2rgv6PuJkV/QAGCo9iu/IKqGp1jza/3/+Ogvqf/j
AKg8kaj6OJyxEABgpfatX0atX72rRHFeuFNN7RITI772O/q+EQKi1q8XlTdWi30kxhlfUJ+XIcCf
k6LNLOkNSNSNNWH1sThjIQDACu1ccj/L9xujplfT/Hjja6/FRH1R3TeOk9LTeDHW7FomYIz0gmr8
+Et9ggoBDoDvncoAgPEAEABgqhpWv0Ht336opPNiNM03VvVFMTbii0Ls80JCxFZ/dmmjeQRDpJfU
VpSi1/uFhL9K7PtxHTyaqNdROGMhAMAMBfbtpvplD6sBWYgxvWg0vZ4RJIFAKuNLhtbSoric2kuG
aG9oUu1SIMVlAUYA9Dmb6BAAAAIAclbtK7dHC3oGwyek+3HdAb3w15nx+WM4rFy+45v2pGB41NN/
Q6vGdAF0cig/DhxL1Hs4zlgIAMi6n//uXyjctF0xth7xY6O+0fDGboHW/+/Q+LxaHwlHzR9WARCJ
qBmA1opSotkFYwsLiU1+xMVEhwIAEACQVbq/e+lDBuOTvm+M+vrlPlGIu/yXxPjx0T6ibZEoACLq
pu3zYp5EcRmBMRMQkkBALSb+cBzRYT/CGQsBAJloxz9nkRTYHxfx46K+sehn+D29wJcs4mvGD4di
ja/t64+SanzDPmnPSfF/jajhtaKhetVAGnoKCcMuxBkLAQBpfihtZ319wRDt9agvxEV7MUn6b4z6
8ak+T+258eXNYHgdAJIBAlK0FiAZjC8Z39DQtGXs96rYv+vaTlQZoFBbkAJtIfL2m0LufufhjIUA
gM7UsHoxHfhmeUyqnyrlj88MkkZ9o/G5qUNG8xuMH47ERX9DFyBebvamgw8wkwdTr7XMQBFk5g+2
AgAQAJCWtr98m/wYa3x+SV5IgIEYB4KY6r7R+Fp6z00fCkX3w3GpvzEbiE/vqwNE/Q/EtmJM6p8K
AEEKHgAAIACg489gpqt99Q+GMfpKtFeiPsVEeiEGAoZLe0mjPjd9XNQ3Rn/+WiQUzQ6MGtKsRngh
0fjJTC8kAUArAAABAB2qfU8t1f3fo7H9fcO1fb3ol1AI7KCvz/vuoWBc5Ne2SCwMIoYUv7qNqF9r
rMmTGV9Iq+EAAAgA6Ej7NrxHTV8s0c3vMkR4lxBrfv01IYX59aivRnzN9BwEeuofjq3+a60yfK/S
rxdSGD3dLCAZAFqCAAAEAMRrxz9nU6R9nz5bL1mxz+VKMujHmPLHR30t2svRP6ik+DIQgrHpvxbt
+xxIbvZ0jC9Q5wA4oAKgPwNAXwAAAgBkacU+Y+Q3mj+hwu9K0t83ml9L6zXzy4aP7/+H1Jl57UR9
W5IM3unE/KmML6SgAQdASwAAgACAVOZPFvnFZFsy8yek/MHYRy3yh9R0388gMbQxbhy/kNr8/P2X
eolWs62RbeUs/RjCnruwgciTomWNivAMgAGgGQCAAICkkd9o+tTmV0f5JTN/KC7qh9SoHzb8TMz4
wxuSTOJJYf4Q25nGHO5RN7c7+uhykXxZgo84Omcf0XENiS0sxWUAAAAEABiv8VNCNd8IASH++VTF
vmAwzvxBQ8qvvja8Pmad/ugqPinG8E9nsGhj0d7HDO9ljx6+uZVHt0uFgFtd/ktUuhQ3baTYUYFx
AGgKAACQIyCQNwAki/yawVNFflf8yD7N/HzTonswoPTtNRhodYAq1sfv25Ta6IKQ+NyV7L3czOhe
H9s8yqMMAI/yMwcBh4KeBajHwy8jXr+OPRdJBEAzAACVOABqX7+TpFBb8nH9HQEgWeRPav6AGvnV
wt/hu2IjfWfRnz8+3k60ghnbV0aSbHq/Yn5ueLeaAXjd8ib4PUo2oGUA8iAi9tnT1hhbTakBAABQ
KQOgbvlz1L57fczqPEpFv4PKv5ii4Gc0fygQhYBmfncr0cA9yaN7R9GflwmuCJDkZaZnmySb36fc
2NNYA+AZAO8asE3wuuSN3GoRMsA+/yCWcVzypQFaHADtFNwPAEAlCID6/7xMbbWfqP3+VAU/SgqB
lAW/oKG/b6wB9K4j6tKeGOnTiP7SJAaRiIckd7mc9ksun9IVkPv7HiXl17sAzPwcAn7+6JYHDwlC
RAFSgH3+tE9juwBNAABUggA4sG0DNXz8nBwKYyb1sP8lM78RAKnNH4gt+gXV/cHbO07vO6n8Ryaw
fZeXGb9MAYDIzC9yILj5bYCUdJ/fGUjPAlg3oJxfFvSylxkAWAohCPxYGAAu3UjUU500JEWY+QEA
yBnmtw0A8sSel/4YvY+GK0nhz5U4rp8/l3RSj5ziB+L6/Wo3YNC2rExvfIxMcMumlwHg4hkANz5/
zq0dvAIAfnNQDgM/AwDPCMrYo4ffQCTCvmtABgH5Woiu3RTtAuxvAwCg0gJA7fP/JXuXe0deoMOt
9PtdIiUt+LmME3vizc8r7Frar2cAfGAPi7b9t3Wc6qcyvfG5BoHCU8vktF9O/UWfYnziAJDv+R29
PwC/UxDv93vYo0+tAXAAeFgW4AqzXwkySLDjuunLaBeAZwD72gEAqDQAsOPFWSQFWxTfuBQIyNGe
P7oNZteH9op6dyCx6CcZzG8c2NNK1Gd7nLmzS/+plcXtq6uY2VnKL5Qpqb/AAeDinRcFANrvc6Dx
5YjkAqCoboJSB3DzLIB1BXztJPx+C+lXAQAAqGQAwAy747mZ8skvuBQAKLfY5uYX5fEz8uYSE/r/
Sfv9WppvLPx1r2Wp9wHDctzJAJAGFAwgCF7ak30kS+kFnwICti9J7KAlMaH1+HeSf5VHfh/bGNQE
rwaAMIlH7SeasEv5/UgEAIBKpwjY8P6r1Pr1Z8wIkm587ZF3A9zc+CxaypmAO25Of7LJPXLKr0V/
tt91BzN/s8HcGUT9Dp4LXlrNPtqrGJ9DgDtcSj3VT+DThuXUX03/5U3JAFx3b1XWBZQyA4CQZGqx
JEk4u6HCAcCOBXdx58oAUMyv3GVXdEl6N0DUzO9Ri4HuJKm/tpiHZn4OgrI6oqo9BhObBAD2X+DG
g0napRhfIn807e+oITXj8+Pn5ucZgIsB4NFvo2MW0gDAyy+/TBdccEHKz5k7dy5NmTIFZzlUAAB4
igMgYsgAFNMLWiGdG9+tPOdW9+XKv5Ak9ddH+PEluZqIemyNS90p8wJgB12B9ksPYx/PswBfeo0i
qgDglwE9YbkI6B63j4Sz9sbcFrwjAIRCIfJ4POn+DXCmQw7vAix7hQJb1ioFQFGrA6gFQA0Ibi0T
0IqDsbflllN/4+QeiaX83bckMTblfgUgZgagSG2Thijpf1otKSmX/+TIz/r+nhC5n9oeNb9+GTA1
AARByPiPDRBAzi0CMu184i7FiwwAZCwCupR0X8sKlE1kX0CSrwQI6gxbwTiNlz/2WJtY2LMCAGw/
/HF3CjzQJ91WYeYPK5V/9uh9dpv+vPFWY6nGATQ3N1NlZWVWf/R//etfdNppp+Hsh5wHgO8ev1Pp
+2tZgFwHULoBWp9fywIE9c6++oAhDoNISIEA37p9ZvymlgNALkXUeqjtpqHpZQDc/N4A+Z79Nhkf
OhwJeMstt9Ddd9+d0x8f2QDkOABI4TDtfPIeJbK7lVtpc7OTOohOzgA80ev+gg4CZihmGJEXEcMB
EruujrshpwkASKcwqP6btj/8gKQvvR00fIj8z22ihJKB8d6BkdRzAa644gp66qmncj4BOERmzJgB
JwAAzgCA3J1uaqT6hY8q5ncLenqvp/5qVqBcKRDlyTSKdxkApAC5u62Wo2vcN00PACxxoKXlRBu6
EPVi+2P3EXUNpjc0OMXrUlAdp8Cf90SiFwmE+GaVYiEQ6Xg2YDY1gFTavHkzDRo0CI4AAPIPAPUf
0Xfz/mwwvqBcHnRT9BZe+lgBbi9lUo1IzeSqXKsAwp1BBlDP3uweZny/uqCHzxedwss/5Kx6oiPq
O18HMNkAIxI6Xxg0WRbAuwBNqdcDMBMA6BYAAM4CgKrw/kaqe/5RdWyAmvprQFAhIMiLf/DBM2Fy
+VYqr/PRdi4FGHJBsaOrAK+z15eVMfNz4/uJyvwKADQIuNR+Bute0OTP0l8UNOXqwGkQQF8PoOMF
QayAwBtvvEHnnHMO3AEA5B8AmvYvX0JtX3wSjfiiFM0E+HPyyPuPmOHD8kg7zfjaPgeCnHrHA2A/
225jL/i7kOQrVwDgU0HgV6fs8vn7/IP4wh09WZfgvPXJU/9UWUBnkd+4EKhRkc7XBIxEIoxPLktO
DmQDAIBjAKCpbsFsFuiD0QxAvTogUDtzw2rF7Pz6ukvNANTBNhwASlZAsSMBJ0sk+StJ8pary3n5
lNV8fMz4MgB8JJSxR7+LfR4DQFsb0RUfpBftO4r8Qifpv+LutFcFHj9+PC1cuND0E+T3v/893Xnn
nXAKAOAMAGja/eSf5dmAylUAZuLWj5VhwTziu9TIz19zR+RagKBmAXp2wCfs8VnBfCqvj0V/T7k8
l5/cfCEPZn5t+S5mfqHST0K5R5muy6cR96ojOntj51mAEQjxpheEjtN/tQ6S6bLgRx11FK1Zs8b0
E2X9+vV0+OGHwzElDgFn3RtQitDu+QwEoa9JCuxVhtaytN/NHkkk1fgReVUu4vMJVOPz35MvMa5k
HYeFLPq7GQDcfpJc/LKdR5lyyBfv4NN2+eo9HAIVbnXCDoMAsSxg8qrO7wKUyvCd3hLMAAD9xiDX
MgCMSatZ2tvbye/3o1sAFTkAVIV2baGGF25WDlDUIrxqeNYdUDICZfiwYn7151d8JH1QxYxfTpLI
ACDwyTxubVSRMnefA8AvsgzApXQnvGG5uyH8Zk0axb4sbggabbSc7w144okn0ocffmh6e7/wwgt0
0UUXOfJkrq6uprq6Ov3n888/X54wBRUxADQ1LXmQWr98Tz5K2fR61NdMH4WD/NjMIvw9vZjxyynC
V/KRPLFz+EV5ij/bRBL9grLvCZNY3sYA8EXq9D/Vz3zZfz5pySUlgiFVETDHuwPziC2KoiXt7aRs
YPTo0bR06dKUr3/66ady9wgqYgBo2rdoFrV//R8FBGoW4JZX6VJBIF8mVGbjuf4wgHnSz7xZliI3
l2Tji9z8fl5MZACYvpkEfoPQdEzPPXIt+3A/v8zoVx75vQJ4geKGzWw/kroIqHUBDoRyvj34559/
TsOHDy9KEKR7KfStt96iM888E44vhiJgOtrz5FUUbtmrDCv2xHUL1LqA5/5+JAUq5am8Kb80zyZ8
fMZehEEjRO5ZG9OP/FezrYyZvryCbeVsU8cbaNN4R31LNLQ+NvU3AoBnACYAQNOwYcNo3bp1prf1
qlWr6JhjjnE0AFDDKDEAKGl0mHY/Mk7J6F2GS4Lqo7xq96wjlb5/ym/Nftcbkhfs8N7HzO+V0kv/
LwuQVNGVJB8zP9/K/XIWIFSwxy4+Ejhz2oNEV32YPAvgAGgzFwBcgUCAfD6fJc1tt8H4Zco//elP
af9+Q0MDde/eHc4vGQCoCtV9Sw1/v0EZOaiOFdBGC7p4V2D20R00kiSv1uv9b5b6VwfjhhSngAAf
ljDZQ5K/iiRPmXzHIHl8QRkzPh9b0LWchDI+tqBdWano/CRRmY8DaAuxLMBcAGgaNWoULVu2zPS2
nj9/Pk2aNMlx0Z/ryCOPpLVr18L5pQYATcGdm6nxH7/TLxOK7mih0NXsI3HekNhKPV++b+I3JJ7Q
oFw65MOKSUgOAUMLRf7HTdLHXSjirVSXC/cqlxc9/LIi2yoZBCr4vQL4/IVWoimrkjWcbH4OASsA
oGno0KG0ceNG09+3traWevfu7SgAoBuQGwQKHgCaDnz0CjV/+De1KCjJYwWUS4WSYayAOnhI3Re0
3/EYIJCiCxC6r4Kkz7sw83dRFwx1K1cA5FWAXcplxQp+fwB+mTJAws1rYtN/vQtgPQC4mpqaqKqq
quC6BQ8//DBdf/31AAAAkJ32LPg1hZvq9CHDfN1B42VDl1f9mS/d7RKiMPAqi5WkgoC0y0XB3/Wh
iFDOvr+XYq4w8PqDX2AAEBQAlLeSeOsm3fTG9CPYFrYFAJqsKhKuWLFCHpfghCwAAAAAElLt3XPH
MUNH1G6BeplQnVIsm14bRsyX8uave7VxBUKS+f0KCNqvGEQR6kLJLi/yUYVimVJcdN/5JZE/HHdM
BgC02wcAuZsUDJLX6y2YbCBTALz44ot04YUXwvkAQKzC++tYRvArQ3GQ4kYQGh7dKhS8hklGca0U
XlNJgTmDkzckg43gZ/3/inbyzPoqRcNFmPnD8ubtywDQ394bg5x11lnytXOz9dBDD9HUqVNRBwAA
nKlIaxPVPzFJWY1InUugg8CtgIHc0RmGck3ARXo3Iea7t7mp7dofJml0FtWv3EbiSXs7zExkAATy
AwBNVk0w+uabb6h///4AQIEB4P0sGvukQmyY1jVLqPm9x5XugHxbMkkvAurDibVpxlq3wKV0E2Ku
EnC1iBRacDBFGrzknlhPYr/muHQ/acs5AgDy4be0UJcuXRzZLdi6dSsNGDAAALDY/CUHAE0Nf7ue
Ik21UQh4tNoAxXYHNDgYntebLd0gJRmJwAAQiDgCAFZnA++88448nt+uLIDPmLSqzoEMoMgAoKXj
dY+NZ40VlIcSuzyC3h0QtEuH6lUDktcgULsHbqV7kNlnUSwAgs4BgFzbCIfJ7XY7KhvIFABnn302
LV68GO5HDSBz1T86Th4WLKh3K46ZbaiNG9AzAtKHH5OQKQS4+SXHAUATn2ps1aW9TEGAOgAAYKsi
B/ZSw4KrdPMbuwJa9yCmTuCOrkmQItwnzTpkAIScCQCruwWbNm2iwYMHp/W706ZNk68uAAAAgK1q
W7eUmt9/RO0WKFFfW4GIj/7VLieSuj6hNsYg5gbCHRUBVQB4+k4lT/9zHdsOra2tVM5nO+YpG8hm
cVQAAAAwTU1vPUiBb/5PyQaM0V9be8Ad9+jShhSn7v/LAAjxLUJlRz9JQpfejm+H4447Tp4abLZe
e+01GjNmjKndgJUrV9KIESMAABQBzdP+V2+j4K4N0Whv7A644uCgdwuklBCQARCOUPlJ/1RugpCh
nnvuOZowYYK8f/vtt9PMmTNtaQd+l6EtW7aYX3+pr6eePXuiDgAAOFt7/nox8WWHoysRUcJVA1Fd
uVgZVCTF+lsbChxWAVDzZqefmUlRzo4Tv7GxkXr06GFbt+C3v/0t3XfffQAAAOAMRdqaqfHpiYZJ
RhFDBmCYa6B3C9SVigwQ4AAQB80kV6/jY95779698nXzXNJtu05+qyYY8Xn9fH6/8ftkuv4hAAAA
WK7Qzi9p32u3qN0Cw6rESSCgXU7UsoFQxEvS8S/QZZddRs8//7ypx3XCCSfQBx98YEsb2LVUeabd
AJ41jRw5EgAAAKxXcNvntP/NPyjdAH1JMilaFGT7m75rplE3Lqf6fQFbjsnuCPjKK6/Qz372M8u+
C+oAAIDj1bToDgruWk3729ppwsMracXGPXk7lnyd/FZdLSikNgAASqkeEInQlVdeSQsWLHDUceXz
5N+3bx9169YNAAAAik9W3pCj2E5+q4qEAAAAkBdZdUuuYj75rVyqvDPxYcRz5swBAAAAUxqzoLIU
p2nJkiXyTD0ntAWf9Tj3usvo+kefAwAAgOICAF8F2KoFPsyQ3UVCIwCa9jbSI7/6eczrM/7+LgAA
AHQsft85vrCFk3XQQQfR7t27C6I9m5ubqbKy0lYA3HNJ8kVJAAAAoCCj/xlnnEGLFi3KW//aDFk1
3dgovj7h32dcmfJ1AAAAcDwAFi5cSJdccknRtq9VE4w03T3u9JIDQMndGsxKWXWLrWQaP348Pf30
0xnPgS907dq1iw4++GDbAXDs+RPpzEsuRwYAAKSWVYtiDBkyhD799FPLxtIXivh8gokTJ5o+JyId
ACALAADy2g3gIwkL6RKjGZo1axbNmDHDts8DAFADcHQdoE+fPrRt27aiazM+JPiUU06xvNDXma4Z
dQwNrO6e8vUf/fyXdPrPxwMAAEB+AKDptttuozvuuKMg24ffd5AXKl966SXHHdu1Zx5PfXtUlVwW
AACYqGeeeYYuv9yeYlGhjGHnl9gOO+wwxx9nZ12AYoUAAFCAWYCm8847j1599VW0hY0A4Bow8gwa
95tbShIARCgCOu6k/+STT+jYY491VDvwhT/4AiDFZv543fjMYnJ7vAAAAJDfqOe0ImGhRP8/XzzK
1GM9eeJ0+vFPxwAAAEB+dOONN9K9996b12MYO3asvJa/kzXj//2YuldYP7ai58Aj6ao/PQQAlIqs
HK2WYbsj+qviC6BO+PFR1FK7Ka/HMe3J18lv0R2UAIACzgJuuOEGuv/++00/Dj4Z6O233y4pAAwc
OJD+/e9/y10io1LN9MtL9uGgKwkAgAMMMHz4cPrss88smwe/YsUKy+7km0z8Dj586rHVmjp1Kj34
4INptbeTAOAUCGAykIMioJayZ3Ojy3Rk91oAZmcBJ598Mr3++uvUtWvXrP690wDgBAgAAFb9YWfM
kMey59Jnv+iii+jFF180/dimTJlCc+fOdTQEOKx41pLu7cELFQCVBw+gKXOeQBeg2GTmbaqs6k/b
VSRM5/iXLl1Ko0aNsvQ4nAiAfGcByAAcFP2effZZeZ5/Mlk11djOsQN85V++oEffvn2poqLC9r8H
AIAMoGDqAKlkVZFw9uzZ8t11i1E7vtlCz/zuasce35BRY+n8ydcDAABA+mm5Fd2CQlowtDPt3VNP
j107riCO1VvRlX7zxEsAQLFpw4YNdMQRR1jWL580aZIltxrj7zt//vyCbXenpvqpVHFQH7ru4QWO
Nz8AYEMWcODAASorK8vo31i1ai4HGF/nEOa3Vr965AXq2qMnMgAAgOS74ixevDjjz7Hq1lqFtApR
IZqfC0VAACDrbkC8ampqaPny5aZ/j5kzZ9Ltt98O8wMAAEAm+ulPf0pvvvmmbQDIBTx2HZvZmjXh
LJLCoYI8P/I9EAg1AItl5oCgTMUr+r169Sp6EBRy9DfqoO8fRVfecb+jIQAA2BCN+a3FR44cadrn
W1Uk5JOX+CSmfOrey8+lcKCtqM4Xu7sEAIDDAGDF9Xi+Gq/Xa/6yVfkeO1As0T+fEAAALFY2k3qs
SrFHjx4tj7s3W7feeivdddddAECBQQA1ABuUTfS1uo9dLEXCYgaAHRAAABzaDdi/fz9VVlZaekyN
jY3Uo0ePgu0WtLY000O/HFv0546TIAAA2ASAlpYWS2b/JZNVE4wee+wxuuaaayw77j07v6O/Tr80
15SF/3GsOUCT3hsAKEEA5OMyW6FNMOJtNOsXZ5hqqEWPP0Tr3s3uRivdDz2Mrrnvr6m7K/zeA1m0
8airb6YRo88CAEoJAvm6zj5mzBhatGiR6e87ffp0euCBB/JaA7hu3ktUUdXV9PfNNEpnU7ewMgsA
AGxSuqm2EwbZDBs2jNatW2f6+27dupX69etnOwCyMdC9l51D4WC7Je9tJWCsMj8AYIImT55M8+bN
c7T5NTU3N1tSiDSzW5COkSbNeoJ69RtgyfvnYsxMIAAAFJn4+nfLli3Tf96xYwcdcsghjjxWq0YS
zpkzh6ZNm5b1vw+0tdEDk87N2jwjBnXR92c//jKdevqZGRl16GljaOyvpiceVyBANYdHr67856vm
nGoCgstNNz+7BACACqeGYWU2MOsXZ7JzKpJe5Fz4ToLJ+LLrJ3y/KunvJzNrKgAkA8sJP+hJkXBi
t2HRis1U3evgrLMAqyYNAQBQRuKLeg4aNMiS9+6s+2NW8cwY+eP1j3c/p/4DDksrUse/N4fSyMFV
Kd87E7jY2R1AERDKWFYVCTdt2pRwL4BcpvtmCgBJCtJHW2Ij+NP/fRN9t2FVp+89+vgfUFPjDssB
YDYIAAAoK1m1VLkxG8h1qK8ZAFjwx9/Szi9Wd/repx8/hJoba20DgFkQAACgnDRixAj66KOPTH/f
u3nqnaNs7QJEWBfg+1W2AsAMCAAAkFmppKnvV+Hz0O3nn2y6Ob7ZspkuPvPonE2aCVym/G42Tbr6
15YAIFcIAACQaaqtrU24LbcTswDFrBX6KX3PY/9Lo85IPtw25WXAU8+lsb++IeH5UChEPx7SrUOo
KJnFKPbxointNGDEaBp3w62Wmh8AgNKWWWMHzABAMQwEsioLAAAgR3cLzABAtuZId7kxO4YCAwBQ
wSqXpcrNAkCmBnHaZKB0dNqVN9LIn5wDAEDOFL/L0MaNG9P+/R5dyujmc0+0NVK+9pcHaMOy7GZD
VvSopuseWWi78XPJAgAAyFbV1dVRdXW17dG/g7PTcFqb/dYWLjYCAECFrM5GEtpj/uITAAAVlOKL
hDMvPJW8bhcaBgCASlHFvsovAABBAAAAAEEAAAAAQbYBwF/Vg6bN+0ey85PefX4BrVw4l9xlVTl9
RjjQSkNPv4BO+dnF9L1DE9c+bG89QHOuGAMAQFAyWXmzj+v/+iqVdelS1JADACBkAR3ofz9aSe+v
ryevz2/rd9q1fSuNOfVIGlTdm47u39eSz7h54TsZD70GAKCSA4CmQ/r/kF5d+oGl3+X0owdRc9Mu
/ecLfzTSss/CXAAIEOhE73+5mXbt25PkFZHeW7uTfGW5rXAUCrRTzbDeSRcG5aMOL/zRCdbUN7pV
07S/LAQAIAAgkyygIwWDLXTF5P+i8y6eQP0GDSZRjM7dr6vdRv9+923648RfUvnAirTez2nRHwCA
AAGbNOCgQ+i4Af0see9Js+dTr779AACouJTJ+v+Z6rVVqygYDtr2XZwY/W0DACAAlXIW4FTzAwBQ
yUNgyZq11NzeAvNnCAB0AyDbtHdPPT127ThLP8PsbKB39+/RiYMHOdb8tgMAEIBy0Qtz7qavP3zb
0s9YX/sdbdjxbY7vYt2lPjPNnyUAagAAKG96/Jap1PD1ess/pz0UokWrP8no3xzeux8dcaj1d3fO
o/lzBwAgAOWqMDPnvZeeZetnBsNh+mLHTvpq907550O6dWOGP5SqyuwdTpxn8ycAAFkAlDeV0rTh
fN4N2HQAAAKQWeLTeGf94oyi/X6i20s3/W2xY8wv//skLwACUF711brP6cU7piPqW2d+8wEACEDo
GthjfLOifyoAAAKQ4xSJhGn2+J8UxLEeM/Zy+skvJjrR+NYDABCA7ND8P95Eu79Y5ZjjEQSRbl74
tg2fY575OwJAzhAACCA7tfLtxbTsiXtt/czDR19A5119rY2QMdf8lgMAEIDyrTeemkdr33w+5/fx
VfWka+57gsorK/OQXeRs/KwAYBoEAAMIypvpU5o/HQCYDgGoeMSBzk9UgD1vps7J/OkCABCAkP0V
nuk7NX8mAAAEIECg8ABQ0+nxZfiGgAAECBR42p8LAAABCBBwPgBq0j6+LD8AEIAAAWcCoCaj48vx
wwACCBBwBgBqsjo+Ez4YEIAAgfwCoCbr4zPxIAACCCCwFwA1OR+fBQcFEECAgLUAqDHt+Cz+/oAB
BAA4zPR2AgBggEoaAmas2mPp8eGUg5wG+GKCQDZr9dt6fDhXISeCoFggAABAgEAJQwAAgKAShgAA
AEElDAEAAIJKFALZ3q8PAIAAgCKAAAAAQSUMAQAAgkoYAgAABAECKAJCkNkQAAAAAAgQOAkAAAAg
dAVQAwAAIEAAAAAAIEAAAAAAINQD0P8HACBAAAAAACBAAAAAACDUAwAAAAACBAAAAAACBAAAnGMQ
6gEAAAQBAgAABKErAABAECAAAEAQIAAAQBAgAABAUOFDAAAAACBA4CQAAACA0BUAAHAeQYAAAABB
gAAAAEGoBwAAEAQIAAAQhK4AAABBgAAAAEGAAAAAQYAAAABBxQoBAACCAIGTAAAIQlcAAIAgQAAA
gCBAAACAIEAAAICgEoIAAABBgMBJAAAEoSsAAEAQIAAAQBAgAABAECAAAEAQIJCt+QEACCo0AKSC
AAAAQSUEAZMEAEBQCUMAAICgEoVATT4+FACAIGdAAACAoBKFQE2+vigAAEEAAARBeQJBTT6/IAAA
QfmDQE2+vxwAAEH5gUCNE74YAABB9oOgxilfCACAIPsgUOO0LwMAQJD1IKhx6pf4/78j0IvwqTMf
AAAAAElFTkSuQmCC
"""

#Thread for Main
threadMain = threading.Thread(target=main)
threadMain.setDaemon(True)
threadMain.start()
time.sleep(0.5)
GUIInit()