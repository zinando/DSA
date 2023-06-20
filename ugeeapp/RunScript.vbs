Set oShell = CreateObject ("Wscript.Shell")
Dim strArgs
strArgs = "cmd /c Runner.bat"
oShell.Run strArgs, 0, False