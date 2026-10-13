Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
strCurrentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
Set oShortcut = WshShell.CreateShortcut(strDesktop & "\Sorufelek.lnk")
oShortcut.TargetPath = strCurrentDir & "\Sorufelek.exe"
oShortcut.WorkingDirectory = strCurrentDir
oShortcut.IconLocation = strCurrentDir & "\icon.ico, 0"
oShortcut.Description = "Sorufelek - Ders İçi Soru ve Kura Sistemi"
oShortcut.Save
MsgBox "Sorufelek masaüstü kısayolu başarıyla oluşturuldu!" & vbCrLf & vbCrLf & "Artık programı doğrudan masaüstünüzden çalıştırabilirsiniz.", 64, "Sorufelek - Kısayol Eklendi"
