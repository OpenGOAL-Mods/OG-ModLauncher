:PROMPT
SET /P AREYOUSURE=Install pyinstaller (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO dotenv
pip install -U pyinstaller
:dotenv
SET /P AREYOUSURE=Install dotenv (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO ahk
pip install python-dotenv
:ahk
SET /P AREYOUSURE=Install ahk (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO asyncio
pip install ahk
:asyncio
SET /P AREYOUSURE=Install asyncio (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO requests
pip install asyncio
:requests
SET /P AREYOUSURE=Install requests (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO Pillow
pip install requests
:Pillow
SET /P AREYOUSURE=Install Pillow (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO progressbar
pip install Pillow
:progressbar
SET /P AREYOUSURE=Install progressbar (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO cloudscraper
pip install progressbar
:cloudscraper
SET /P AREYOUSURE=Install cloudscraper (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO install
pip install cloudscraper
:install