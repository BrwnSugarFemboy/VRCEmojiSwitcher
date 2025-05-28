# VRCEmojiSwitcher
This VRChat API program allows you to switch between profiles of emojis, effectively giving users the ability to expand beyond the limit of 9 emojis.

## How it works
VRCEmojiSwitcher swaps between "profiles" of emojis saved to your PC, using the API to make calls to remove existing emojis and upload the next set. Then it loops and awaits user input to await the next cycle of swapping profiles.
All user data is self-contained in the appdata folder.
All application data is contained within the executable file available on the Releases page.

## Demo
![Demo-GIF](https://github.com/user-attachments/assets/adf4dde7-1b4e-46c9-92e9-fc6678ae215b)

## Usage
Download the latest executable binary from the Releases page.
Either run the executable, or open a terminal (cmd, powershell, wt) and run the executable from there. The latter will provide more verbose logging if you run into issues.
This will require an accept of the EULA, and a login of the user to store a cookie for further usage.
It will then backup all of your emojis to `%appdata%/VRCEmojiSwitcher/Backup`
Afterwards, drop your emojis into `%appdata%/VRCEmojiSwitcher/Emojis` with each subfolder containing your 9 emojis.
- `%appdata%/VRCEmojiSwitcher/Emojis/1/` contains 9 **PNG** files.
- `%appdata%/VRCEmojiSwitcher/Emojis/2/` contains 9 more **PNG** files.

### Name formatting
Emoji filenames can either adhere to a number of two standards.
If an image does not adhere to either the static or animated standards, it will be uploaded with the default "bounce" emoji animation.
#### Static emojis
These are emojis that are not animated. They are a still image.
The naming scheme goes as follows: `<number>_static_<animationtype>`
1. The number is 0-8. 0 appears furthest down the emojij wheel; 8 appears nearest (moving clockwise from the return option).
2. The animationtype is a supported [emoji animation type](https://wiki.vrchat.com/wiki/Emojis#Custom_Emojis) from vrchat.
#### Animated Emojis
These are emojis that are tilesheets. GIF file format is not currently supported.
The naming scheme goes as follows: `<number>_anim_<framecount>_<framerate>_<animationtype>`
1. The number is 0-8. 0 appears furthest down the emojij wheel; 8 appears nearest (moving clockwise from the return option).
2. The framecount is the number of frames on your tilesheet. This can range from 1-64
3. The  framerate is how quickly your emoji is to be played. If you're not sure, you can modify it ingame in the VRC+ Menu later on.
4. The animationtype is a supported [emoji animation type](https://wiki.vrchat.com/wiki/Emojis#Custom_Emojis) from vrchat.

## Support
Need help? Want to reach out to the devs? Share emojis? Feel free to join the [Discord](https://emojiswitcherdiscord.bussy.wtf)!
