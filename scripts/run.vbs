Set oShell = CreateObject ("Wscript.Shell")
Dim strArgs
strArgs = "cmd /c cd .. & python simple-youtube-downloader"
oShell.Run strArgs, 0, false