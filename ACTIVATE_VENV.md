# How to Activate Virtual Environment in PowerShell

## The Problem
In PowerShell, you cannot directly run `activate` like in Command Prompt. You need to use the PowerShell activation script.

## Solution

### Method 1: Use Activate.ps1 (Recommended)
```powershell
.\myenv\Scripts\Activate.ps1
```

### Method 2: If you get Execution Policy Error
If you see an error about execution policy, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again:
```powershell
.\myenv\Scripts\Activate.ps1
```

### Method 3: Use activate.bat (Alternative)
```powershell
.\myenv\Scripts\activate.bat
```

### Method 4: Direct Python Path (No Activation Needed)
You can also use the virtual environment's Python directly without activating:
```powershell
.\myenv\Scripts\python.exe -m pip install -r requirements.txt
.\myenv\Scripts\python.exe init_db.py
.\myenv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Quick Test
After activation, you should see `(myenv)` at the beginning of your prompt:
```
(myenv) PS D:\Downloads\HR_automationPipeline_agentic_ai>
```

## If Virtual Environment is Incomplete
If activation scripts are missing, recreate the virtual environment:
```powershell
python -m venv myenv --clear
```

Then activate:
```powershell
.\myenv\Scripts\Activate.ps1
```
