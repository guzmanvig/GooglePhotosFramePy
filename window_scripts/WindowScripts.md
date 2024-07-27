# Window Scripts

These a 4 tasks that can be imported into Window's Task Scheduler that do the following:

- Wake up the computer at 8 57 am
- Sets the brightness of the screen to 80%
- Starts the python photo frame at 9 am
- Sets the brightness of the screen at 30% at 8 pm
- Kills the python photo frame at 11 pm
- Sends the computer to sleep

The reason behind this is that I don't want the computer on while sleeping, and I want to reduce the brightness of the screen at night. Wake up happens a few minutes earlier of the start of the program to give it time to connect to internet.

`nircmd.exe` is a third party software that allows chaning the birghtness of the screen programatically.
`SetBrigthness.ps1` is a powershell scripts that calls `nircmd` with brightness argument.
`KillProgramAndSleep.bat` is a windows bat scipt that kills all python instances and sends the computer to sleep. 

The XML files are Task Scheduler tasks that can be imported. To use them, open the Task Scheduler and import them. Review the parmeters and adjust them if you want.

Note: The path of the .bat and .ps1 files are the ones in my computer, you will definitely need to change them for the ones in yours.

You may need to run this command to be able to run scripts:

`Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser`