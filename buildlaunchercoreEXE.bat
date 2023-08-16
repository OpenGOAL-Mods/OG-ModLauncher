
set mypath=%~dp0
pyinstaller --onefile openGOALModLauncher.py --icon resources\appicon.ico --collect-data "pycdlib" --hidden-import=pycdlib datas=[(path.join(site_packages,"pycdlib")],
move "%mypath%dist\openGOALModLauncher.exe" "%mypath%/"
RENAME "%mypath%\openGOALModLauncher.exe" "openGOALModLauncher.exe"
REM @RD /S /Q "%mypath%/build"
REM @RD /S /Q "%mypath%/dist"
REM DEL /S /Q "%mypath%/openGOALModLauncher.spec"
