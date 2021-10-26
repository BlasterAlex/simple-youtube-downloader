@echo off

cmd /c "cd .. & python -m pip install --user virtualenv & python -m venv env & .\env\Scripts\activate & pip install -r requirements.txt"