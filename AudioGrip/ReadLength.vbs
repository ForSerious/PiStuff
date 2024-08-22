Set inputPath = Wscript.Arguments(0)
Set dMC = CreateObject("dMCScripting.Converter")
Dim AudioProps
AudioProps = dMC.AudioProperties(Chr(34) + inputPath + Chr(34))
AudioProps = Replace(AudioProps, chr(13), vbNewLine)
AudioProps = Replace(AudioProps, "               ", "")
AudioProps = Replace(AudioProps, chr(9), "")
Wscript.Echo Mid(AudioProps, InStr(AudioProps, "Length :") + 8, 12)