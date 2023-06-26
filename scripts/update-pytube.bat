@echo off

@REM Get project dir
for %%a in (%~dp0\.) do set projectDir=%%~dpa

@REM Checkout pytube master
cmd /c "cd %projectDir%/pytube & git checkout master & git pull" || goto :end

@REM Update pytube from upstream
cmd /c "git fetch upstream & git rebase upstream/master" || goto :end

:end