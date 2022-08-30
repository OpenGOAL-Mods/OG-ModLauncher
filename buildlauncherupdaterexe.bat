
set mypath=%~dp0
pyinstaller --onefile "Launcher with autoupdater.py" --icon resources\appicon.ico 
move "%mypath%dist\Launcher with autoupdater.exe" "%mypath%/"
@RD /S /Q "%mypath%/build"
@RD /S /Q "%mypath%/dist"

