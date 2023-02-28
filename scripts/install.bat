@echo off

@REM Get project dir
for %%a in (%~dp0\.) do set projectDir=%%~dpa

@REM Update project and submodules
cmd /c "cd %projectDir% & git pull & git submodule update --init --recursive" || goto :end

@REM Checkout pytube master
cmd /c "cd %projectDir%/pytube & git checkout master & git pull" || goto :end

@REM Create pytube binary file
cmd /c "cd %projectDir%/pytube/scripts & pip install wheel & create_wheel" || goto :end

@REM Install all requirements
cmd /c "cd %projectDir% & pip install -r requirements.txt --force-reinstall" || goto :end

@REM Do not track configuration file changes
cmd /c "cd %projectDir% & git update-index --assume-unchanged config/settings.yml" || goto :end

@REM Waiting for a user keypress
:end
pause