@echo off

@REM Update project and submodules
cmd /c "cd .. & git pull & git submodule update --init --recursive"

@REM Checkout pytube master
cmd /c "cd ../pytube & git checkout master"

@REM Create pytube binary file
cmd /c "cd ../pytube/scripts & pip install wheel & create_wheel"

@REM Install all requirements
cmd /c "cd .. & pip install -r requirements.txt --force-reinstall"

@REM Waiting for a user keypress
pause