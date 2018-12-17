@echo off
rem Script to test printing on windows
rem Latest update 12/17/2018


:head
setlocal enabledelayedexpansion
    echo Setting up temporary files
    set /a limit=3
:temping
    rem recursing to create empty temp files
    set /a counter=counter+1
    if !counter! gtr !limit! ( goto :body )
    echo. > temp!counter!
goto :body

:run
rem to run vbscript
rem %1 vbscript file
CSCRIPT.EXE %1
goto :eof

:notify
rem to show message box
if %1 equ 1 (
    echo msgbox%2,64,%3 > temp.vbs
    temp.vbs
)else if %1 equ 2 (
    echo msgbox%2,48,%3 > temp.vbs
    temp.vbs
)
del /q /a temp.vbs
goto :eof

:input
rem to get user input using vbs input box
rem parameters: %1 main %2 title %3 placeholder
echo inputbox %1, %2, %3 > temp.vbs
for /f "tokens=*" %%return in ('temp.vbs') do (
  set PRINTER='%%return'
)
del /q /a temp.vbs
goto :eof


:body
rem getting the printer and test printing
setlocal
call :input "Enter shared printer name:" "Testing printer" "printer name"
echo !PRINTER!
goto :end


:end
rem clean up and delete temp files
call :notify 1 "All done, press ok to delete couple temprory files and exit ." "Clean up and exiting"
:clean
    rem recursing to remove temp files
    del /q /a temp!counter!
    set /a counter=!counter!-1
    if !counter! equ 0 (
        goto :eof
    )
goto :clean
set /p msg=Press enter to exit ...
exit 