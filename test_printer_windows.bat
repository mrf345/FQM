@echo off
rem Script to test printing on windows


:head
setlocal enabledelayedexpansion
    rem setting up temporary files
    set /a limit=5
:temping
    rem recursing to create empty temp files
    set /a counter=counter+1
    if !counter! gtr !limit! ( goto :body )
    echo. > temp!counter!
goto :temping


:notify
rem to show message box
if %1 equ 1 (
    echo msgbox%2,64,%3 > temp.vbs
    temp.vbs
)else if %1 equ 2 (
    echo msgbox%2,48,%3 > temp.vbs
    temp.vbs
)
goto :eof


:input
rem to get user input using vbs input box
rem parameters: %1 main %2 title %3 placeholder
echo inputed=inputbox(%1, %2, %3) > temp.vbs
echo Set objFSO=CreateObject("Scripting.FileSystemObject") >> temp.vbs
echo Set objFile = objFSO.CreateTextFile("temp1",True) >> temp.vbs
echo objFile.Write inputed ^& vbCrLf >> temp.vbs
echo objFile.Close >> temp.vbs
temp.vbs
set /p INPUTED=<temp1
goto :eof


set /a second_counter=0
:spacer
rem %1 number of lines, %2 file name
if !second_counter! gtr %1 ( 
	set /a second_counter=0
	goto :eof
)
echo. >> %2
set /a second_counter=second_counter+1
goto :spacer


:body
rem getting the printer and test printing
call :input "Enter shared printer name:" "Testing printer" ""
rem lets check if inputed is in the list of printers
wmic printer get name | find "!INPUTED!" && (
    call :notify 1 "The entered printer name was found successfully" "Processing printer"
    rem lets check if the printer is shared printer with identical name
    wmic printer get sharename | find "!INPUTED!" && (
        call :notify 1 "The entered printer's shared with the correct name" "Processing printer"
        call :notify 1 "Now will attempt printing, fingers across" "Printing"
        rem attempting to print a template ticket
		call :spacer 6 temp4
		echo FQM is printing, Cheers... >> temp4
		call :spacer 6 temp4
        print /D:\\localhost\"!INPUTED!" temp4 > temp5
		set /p response=<temp5 
		call :notify 1 "!response!" "Printing test result"
		goto :end
    ) || (
        call :notify 2 "The entered printer either not shared on the local network or the share name is not identical to the printer's original name" "Failed to print"
        call :notify 2 "Make sure to enable sharing the printer on the local network and copy the original name of the printer to be the share name. Then try this again" "Failed to print"
        goto :end
    )
) || (
    call :notify 2 "The entered printer name was not found in the connected printers list" "Processing printer"
    call :notify 2 "Make sure of your printers USB connection and try this again" "Failed to print"
    goto :end
)
goto :end


:end
rem clean up and delete temp files
rem recursing to remove temp files
del /q /a temp!counter!
set /a counter=counter-1
if !counter! equ 0 (
    call :notify 1 "Cleanup is done. Press ok to exit ." "Clean up and exiting"
    del /q /a temp.vbs
	goto :eof
)
goto :end
exit