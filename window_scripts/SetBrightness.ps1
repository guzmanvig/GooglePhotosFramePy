param (
    [int]$brightness
)

$path = ".\nircmd.exe"
& $path setbrightness $brightness
