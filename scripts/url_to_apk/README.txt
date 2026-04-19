================================================================
          URL to APK Converter v2.0.0
          Professional Desktop Application for Windows 11
================================================================

DESCRIPTION
-----------
This application converts any website URL into an Android APK 
project. It generates a complete Android Studio project that 
wraps your website in a native WebView container.


NEW IN v2.0
-----------
- Auto-install missing dependencies on first run
- Clear and detailed error messages (Arabic/English)
- Professional animated progress indicator
- Improved error handling and recovery
- Better UI with status indicators
- Enhanced validation for all inputs


FEATURES
--------
- Modern dark-themed professional UI
- Website analysis (extracts title, description, colors)
- PWA detection
- Customizable app name, package name, and version
- Screen orientation options (Portrait/Landscape/Auto)
- Fullscreen mode option
- Complete Android project generation with:
  * WebView with full JavaScript support
  * File download support
  * Camera and microphone permissions
  * Pull-to-refresh
  * Progress indicator
  * Back button navigation
  * Mixed content support
  * File upload support


SYSTEM REQUIREMENTS
-------------------
- Windows 10/11 (64-bit)
- Python 3.10 or higher
- Internet connection (for website analysis)


INSTALLATION
------------
Method 1: Double-click install_and_run.bat
         (Recommended - installs dependencies automatically)

Method 2: Manual installation
  1. Open Command Prompt
  2. Navigate to this folder
  3. Run: pip install -r requirements.txt
  4. Run: python main.py


USAGE
-----
1. Enter the website URL you want to convert
2. Click "Analyze" to fetch website information
3. Customize app name, package name, and version
4. Choose screen orientation and fullscreen settings
5. Select output directory
6. Click "Generate APK Project"
7. Open the generated project in Android Studio
8. Build the APK using Android Studio


BUILDING THE APK
----------------
After generating the project:

1. Install Android Studio from:
   https://developer.android.com/studio

2. Open the generated project folder

3. Wait for Gradle sync to complete

4. Click Build > Build Bundle(s) / APK(s) > Build APK(s)

5. Find your APK at:
   app/build/outputs/apk/debug/app-debug.apk


TROUBLESHOOTING
---------------
Q: "Python is not installed" error
A: Download Python from https://www.python.org/downloads/
   Check "Add Python to PATH" during installation

Q: Package installation fails
A: Check your internet connection
   Try: pip install --upgrade pip
   Then reinstall requirements

Q: Website analysis fails
A: Check if the URL is accessible
   Some websites block automated requests

Q: Generated project won't build
A: Ensure Android Studio is updated
   Check SDK version 34 is installed


CUSTOMIZING THE APK
-------------------
After generating the project, you can:

1. Change App Icon:
   - Replace images in app/src/main/res/mipmap-* folders
   - Use Android Studio's Image Asset Studio

2. Change Colors:
   - Edit app/src/main/res/values/colors.xml

3. Change Splash Screen:
   - Add drawable resources
   - Modify the theme in styles.xml

4. Add More Permissions:
   - Edit app/src/main/AndroidManifest.xml


TECHNICAL DETAILS
-----------------
- Target SDK: 34 (Android 14)
- Minimum SDK: 24 (Android 7.0)
- WebView: AndroidX WebView with hardware acceleration
- Build System: Gradle 8.4
- Java Version: 17


LEGAL NOTICE
------------
Ensure you have permission to convert websites you don't own.
This tool is for personal and educational use.
Do not use for phishing or malicious purposes.


SUPPORT
-------
For issues or questions, check the troubleshooting section
or consult Android Studio documentation.

================================================================
