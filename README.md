# Description
Telegram bot for searching YouTube playlists on request, with the output of brief general information about them, which you will not see even with a direct search on YouTube (for example, the total duration of all videos, the total number of likes, etc.)! The bot uses Telegram and YouTube APIs to search and present information.

# Requirements
*   Python 3.10 or greater
   
*   The pip package management tool
  
*   The Google APIs Client Library for Python:
    ```
    pip install --upgrade google-api-python-client
    ```
*   The google-auth, google-auth-oauthlib, and google-auth-httplib2 for user authorization:
    ```
    pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2
    ```
*  	The Telegram bots Library Aiogram: 
  	```
    pip install -U aiogram
    ```
# Start-up and operation
To run it, you need to open the directory and enter in the terminal:
		```
    python bot.py
    ```
		or
		```
    python3 bot.py
    ```.
		
To stop it just print 
		```
		stop
		```.

# Links
* Aiogram: https://docs.aiogram.dev/en/latest/
  
* Telegram Bot Token: https://core.telegram.org/bots

* YouTube Data API Overview: https://developers.google.com/youtube/v3/getting-started
	
