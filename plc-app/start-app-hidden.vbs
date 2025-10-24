Set objShell = CreateObject("WScript.Shell")
objShell.CurrentDirectory = "C:\Users\axme_\Documents\tester_modbus_omnron-dev\tester_modbus_omnron-dev\plc-app"
objShell.Environment("Process")("ORIGIN") = "http://localhost:3000"
objShell.Run "cmd /c node build/index.js", 0, False
WScript.Sleep 5000
objShell.Run "chrome --kiosk http://localhost:3000", 1, False