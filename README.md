
# XboxL Unlocker

**Xbox Unlocker** is a tool designed to unlock Xbox achievements, even for games you do not own. This tool works exclusively for Xbox One and later versions and is not compatible with Xbox 360.

---

# Contents

- **Main Class**: The central class for the functionality of the tool.
- **Python Scripts**:
  - `unlock_all.py`: Unlocks all available achievements for the Xbox user.
  - `unlock_selected.py`: Allows the user to manually select and unlock individual achievements.
- **Windows Executables**:
  - `.exe for Windows`: Precompiled executables that can run directly without Python installed.
- **`games.json` File:**  
  A JSON file required for unlocking achievements for games you don't own.

  ```json
  [
      {
          "displayImage": "link to image (optional, can be None if empty)",
          "title_id": "game ID (required)",
          "name": "game name (optional, can be None if empty)"
      }
  ]
---

# Requirements

To properly use **XboxL Unlocker**, you need the following:

1. **Python 3.x** (if using Python scripts).
2. **Firefox browser installed**
---
# Description of Files

- **`unlock_all.py`:**  
  Unlocks all Xbox achievements for the user automatically. When executed, the program will unlock every available achievement.

- **`unlock_selected.py`:**  
  Allows the user to unlock one or more selected achievements manually. The user must choose which achievements to unlock.

- **`.exe`:**  
  Windows executables are provided, created using One-File, which allow you to run the tool without needing Python installed. Simply run the `.exe` file to begin the unlocking process.

---

# How to Use
1. **Download the Repository:**  
   - Download the repository as a ZIP file and extract it.  
   - Alternatively, use the following command to clone the repository:  
     ```bash
     git clone <repository-url>
     ```  

2. **Install Dependencies:**  
   - Run the following command to install all required dependencies:  
     ```bash
     pip install -r requirements.txt
     ```  

3. **Install Firefox:**  
   - Ensure that Firefox is installed on your system. If it is not installed, you can download it from the [official Firefox website](https://www.mozilla.org/firefox/).  

4. **Download `games.json` (Optional):**  
   - If you want to unlock achievements for games you don't own, download the `games.json` file from the repository or create/modify it as needed.  

5. **Run the desired script** 
	 - `unlock_all.py` or `unlock_selected.py` to unlock achievements.
	 
	 
## Using Executables:
 1. **Download the .exe file.**    
 2. **Install Firefox:**  
	   - Ensure that Firefox is installed on your system. If it is not installed, you 		can 		download it from the [official Firefox website](https://www.mozilla.org/firefox/).  
3. **Download `games.json` (Optional):**  
   - If you want to unlock achievements for games you don't own, download the `games.json` file from the repository or create/modify it as needed.  
4. **Run the .exe file.** 
# License

This project is licensed under the **Non-Commercial License**. You can freely use the tool for personal, educational, or non-commercial purposes. You are not allowed to use it for any commercial or profit-generating activities. Redistribution and modification of the tool are allowed, provided they are not used for commercial purposes.

## Warning

- **Responsible Use:** This tool is intended for educational and testing purposes. Using these scripts or executables to alter your Xbox profile could violate Microsoft’s Terms of Service.  
- **Compatibility:** This tool is designed for Xbox One and later versions. It is not compatible with Xbox 360.

---

This project is licensed under the **Non-Commercial License**. You may freely use, modify, and distribute the code for non-commercial purposes only. **Commercial use is strictly prohibited.**

