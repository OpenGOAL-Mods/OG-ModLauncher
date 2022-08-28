
set mypath=%~dp0
pyinstaller --onefile openGOALModLauncher.py --icon resources\appicon.ico 
move "%mypath%dist\openGOALModLauncher.exe" "%mypath%/"
RENAME "%mypath%\openGOALModLauncher.exe" "openGOALModLauncher.exe"
@RD /S /Q "%mypath%/build"
@RD /S /Q "%mypath%/dist"
DEL /S /Q "%mypath%/openGOALModLauncher.spec"
