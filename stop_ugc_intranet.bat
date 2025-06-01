@echo off
setlocal
for /f %%i in (ugeeapp.pid) do taskkill /PID %%i /F
endlocal
