Set oShell = CreateObject ("Wscript.Shell")
Dim strArgs
strArgs = "cmd /c cd .. & python -m downloader"
oShell.Run strArgs, 0, false