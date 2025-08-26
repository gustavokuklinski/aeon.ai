# Windows 11

## Requirements:
* Command line tool
* Python 3.11 or later
* Microsoft C++ Build Tools - Install: `Desktop development with C++` package

---

## Automated script
Run: `C:\aeon.ai\> python aeon.py`
It will create the environment, activate the `.venv` and download all `pip` requirements.  

---

## Running manually for troubleshoot
1. Open Command line to the directory: `C:\> dir C:\aeon.ai\`
2. Create a .venv with: `C:\aeon.ai\> python -m venv .venv`
3. Activate Python .venv: `C:\aeon.ai\> .\.venv\Scripts\activate.bat`
4. Install pip dependencies: `(.venv) C:\aeon.ai\> pip install -r requirements.txt`
5. Run `(.venv) C:\aeon.ai\> python src\aeon.py`

---

### Windows Specs
| OS | CPU | GPU | RAM | SSD |
|:---|:---|:---|:---|
| Windows 11 Home Edition | Intel i7 - 10510U | - | 8GB | 80GB |


