:PROMPT
SET /P AREYOUSURE=Install package dependencies (Y/[N])?
IF /I "%AREYOUSURE%" NEQ "Y" GOTO install
pip install -r requirements.txt
:install
