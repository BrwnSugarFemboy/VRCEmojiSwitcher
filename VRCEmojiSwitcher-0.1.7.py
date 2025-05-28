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
		file = open((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt"), 'r')
	else:
		file = open((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt"), 'w+')
	if os.path.getsize((VRCEmojiSwitcherPath + "\\EULA_Agreed.txt")) == 0 :
		#Generate EULA and prompt for an agreement
		file.write("VRCEmojiSwitcher is not endorsed by VRChat. The developer of this application does not have any affiliation with VRChat Inc.\nBy utilizing this program, you are utilizing the VRChat API which, while not against TOS to utilize, can put your account at risk if abused. Modification of this code makes support from the VRCEmojiSwitcher development team impossible. Play at your own risk.")
		print("VRCEmojiSwitcher is not endorsed by VRChat. The developer of this application does not have any affiliation with VRChat Inc.\nBy utilizing this program, you are utilizing the VRChat API which, while not against TOS to utilize, can put your account at risk if abused. Modification of this code makes support from the VRCEmojiSwitcher development team impossible. Play at your own risk.")
		input("Press enter to continue...")
		file.write("\nTrue")
		LogWriter("EULA was agreed to.")
		print("Enter your emojis into these folders. 9 per folder is the limit as that is VRChat's limitation")
		subprocess_Popen(r'explorer /select,' + (VRCEmojiSwitcherPath + "\\Emojis\\"))
	elif( (file.read().splitlines())[-1] == "True" ):
		LogWriter("EULA was previously agreed to. Continuing.")
	else:
		LogWriter("EULA was invalid. Terminating program")
		sys_exit()
	
def VRInit():
	#todo put something here
	print("how")

def GUI_Init():
	#todo put something here
	print("how")	

def Authenticate():
	if(os.path.exists(VRCEmojiSwitcherPath + '\\cookie')):
		configuration = None
		LogWriter("Cookie Found")
	else:
		configuration = vrchatapi.Configuration(
			username = urllib_parse_quote(str(input("Enter username: "))),
			password = urllib_parse_quote(str(input("Enter password: "))),
		)
		LogWriter("Authenticating with credentials.")
	with vrchatapi.ApiClient(configuration) as api_client:
		api_client.user_agent = "VRChatEmojiSwitcher / 0.1.6 femboy@bussy.wtf"
		auth_api = authentication_api.AuthenticationApi(api_client)
		try:
			#pull a cookie (maybe)
			if(os.path.exists(VRCEmojiSwitcherPath + '\\cookie')):
				file = open(VRCEmojiSwitcherPath + '\\cookie','r')
				cookie = file.read().splitlines()
				file.close()
				#try signing in with the (hopefully) pulled cookie
				
				api_client.rest_client.cookie_jar.set_cookie(make_cookie("auth", cookie[0]))
				api_client.rest_client.cookie_jar.set_cookie(make_cookie("twoFactorAuth",cookie[1]))
			current_user = auth_api.get_current_user()
		except UnauthorizedException as e:
			if e.status == 200:
				LogWriter("getting 2FA")
				if "Email 2 Factor Authentication" in e.reason:
					auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
				elif "2 Factor Authentication" in e.reason:
					auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
				current_user = auth_api.get_current_user()
			else:
				LogWriter("Exception when calling API: " + str(e))
		except vrchatapi.ApiException as e:
			LogWriter("Exception when calling API: " + str(e))
		
		cookie_jar = api_client.rest_client.cookie_jar._cookies["api.vrchat.cloud"]["/"]
		
		LogWriter("Logged in as:" + str(current_user.display_name))
		
		file = open(VRCEmojiSwitcherPath + '\\cookie', 'w+')
		file.write(cookie_jar["auth"].value + "\n")
		file.write(cookie_jar["twoFactorAuth"].value)
		LogWriter("Cookie written.")
		file.close()
		
		return api_client

def SubscriptionCheck(api_client=None):
	LogWriter("Subscription Check was called.")
	if api_client is None:
		LogWriter("SubscriptionCheck() was called without an api_client passed")
		sys_exit()
	
	economy_api = vrchatapi.api.economy_api.EconomyApi(api_client)
	CurrentSub = economy_api.get_current_subscriptions()
	if CurrentSub[0].status == "active":
		LogWriter("Active Subscription Found.")
		return True
	else:
		webbrowser_opennew("https://vrchat.com/home/group/grp_ca3034e1-cf2d-4cec-8e0b-1fac32bfbad0")
		LogWriter("Subscription is not active. Pay VRC.")
		sys_exit()
	
def EmojiBackup(api_client=None):
	LogWriter("EmojiBackup was called.")
	if api_client is None:
		LogWriter("EmojiBackup() was called without an api_client passed")
		sys_exit()
	
	LogWriter("Backing up emojis...")
	files_api = vrchatapi.api.files_api.FilesApi(api_client)
	currentEmojis = files_api.get_files(tag="emoji", n=9)
	if((os.path.exists(VRCEmojiSwitcherPath + "\\Backup\\originalEmojiBackup")) is False):
		os.mkdir(VRCEmojiSwitcherPath + "\\Backup\\originalEmojiBackup")
	else:
		LogWriter("Emoji Backup was already completed at some point. Skipping.")
		return
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
	LogWriter("DirectoryTracker was called. currentDir is " + str(currentDir))
	
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
		LogWriter("Set currentDir\/nextDir to " + allDirs[0] + " because currentDir was None")
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
				LogWriter("Discovered Animated Emoji. These are not currently supported. Skipping...")
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

def WaitForBinding(nextDir):
	LogWriter("WaitForBinding was called.")
	#For Testing
	input("Press enter to upload emojis from the following directory\n" + VRCEmojiSwitcherPath + "\\Emojis\\" + nextDir + "\nAwaiting input...")

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
	quit = False
	currentDir = None
	if os.path.exists(VRCEmojiSwitcherPath):
		LogWriter("Initializing program.")
	else:
		print(str(datetime.datetime.now()) + "    Initializing Program")
	while(not quit):
		#Initialize PyOpenVR Overlay
		#VRInit()
		
		#GUI Init
		#GUI_Init()
		
		#OOBE
		OOBE()
		
		#Authenticate user
		api_client = Authenticate()
		
		#Subscription Check
		SubscriptionCheck(api_client)			
		
		#Backup Current Emojis if not done already
		EmojiBackup(api_client)
		
		#DirectoryTracker()
		currentDir, nextDir = DirectoryTracker(currentDir)
		
		#Pauses script, and awaits next user manual call
		WaitForBinding(nextDir)
		
		#Remove All Current Emojis
		RemoveAllEmojis(api_client)
		
		#Upload Next Emojis
		UploadNextEmojis(api_client, nextDir)
		currentDir = nextDir

VRCEmojiSwitcherPath = (os.getenv('APPDATA')) + "\\VRCEmojiSwitcher"
main()