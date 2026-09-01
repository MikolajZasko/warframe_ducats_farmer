$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Start-Process -FilePath "$projectDir\.venv\Scripts\python.exe" `
              -ArgumentList "`"$projectDir\scripts\simple_ui.py`"" `
              -WorkingDirectory $projectDir `
              -WindowStyle Minimized