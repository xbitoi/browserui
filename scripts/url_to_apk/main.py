"""
URL to APK Converter - Professional Desktop Application
Author: v0
Version: 2.0.0
Requirements: Python 3.10+, Windows 11
"""

import sys
import subprocess
import importlib.util
import os

# ============================================
# AUTO DEPENDENCY INSTALLER
# ============================================

class DependencyInstaller:
    """تثبيت المكتبات الناقصة تلقائياً مع رسائل واضحة"""
    
    REQUIRED_PACKAGES = {
        'customtkinter': 'customtkinter',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'PIL': 'Pillow'
    }
    
    @staticmethod
    def check_and_install():
        """فحص وتثبيت المكتبات المطلوبة"""
        missing = []
        
        for module_name, package_name in DependencyInstaller.REQUIRED_PACKAGES.items():
            if importlib.util.find_spec(module_name) is None:
                missing.append((module_name, package_name))
        
        if missing:
            print("\n" + "="*60)
            print("   URL to APK Converter - Dependency Installer")
            print("="*60)
            print(f"\n[INFO] Found {len(missing)} missing package(s):")
            for module, package in missing:
                print(f"       - {package}")
            print("\n[INFO] Installing dependencies automatically...")
            print("-"*60)
            
            for module_name, package_name in missing:
                try:
                    print(f"\n[INSTALLING] {package_name}...")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package_name, "-q"],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if result.returncode == 0:
                        print(f"[SUCCESS] {package_name} installed successfully!")
                    else:
                        print(f"[ERROR] Failed to install {package_name}")
                        print(f"        Error: {result.stderr}")
                        print(f"\n[TIP] Try running manually: pip install {package_name}")
                        sys.exit(1)
                except subprocess.TimeoutExpired:
                    print(f"[ERROR] Installation of {package_name} timed out")
                    print(f"[TIP] Check your internet connection and try again")
                    sys.exit(1)
                except Exception as e:
                    print(f"[ERROR] Unexpected error installing {package_name}: {str(e)}")
                    sys.exit(1)
            
            print("\n" + "-"*60)
            print("[SUCCESS] All dependencies installed successfully!")
            print("[INFO] Starting application...\n")

# Check dependencies before importing
DependencyInstaller.check_and_install()

# ============================================
# IMPORTS (after dependency check)
# ============================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import shutil
from pathlib import Path
import time
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import traceback

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# ============================================
# ERROR HANDLER
# ============================================

class ErrorHandler:
    """معالج الأخطاء مع رسائل واضحة ومفصلة"""
    
    ERROR_CODES = {
        'E001': 'URL_EMPTY',
        'E002': 'URL_INVALID',
        'E003': 'NETWORK_ERROR',
        'E004': 'TIMEOUT_ERROR',
        'E005': 'PARSE_ERROR',
        'E006': 'PERMISSION_ERROR',
        'E007': 'FILE_ERROR',
        'E008': 'VALIDATION_ERROR',
        'E009': 'GENERATION_ERROR',
        'E010': 'UNKNOWN_ERROR'
    }
    
    ERROR_MESSAGES = {
        'E001': {
            'ar': 'الرجاء إدخال رابط الموقع',
            'en': 'Please enter a website URL',
            'solution': 'Enter a valid URL like https://example.com'
        },
        'E002': {
            'ar': 'الرابط غير صالح',
            'en': 'Invalid URL format',
            'solution': 'Make sure the URL starts with http:// or https://'
        },
        'E003': {
            'ar': 'خطأ في الاتصال بالشبكة',
            'en': 'Network connection error',
            'solution': 'Check your internet connection and try again'
        },
        'E004': {
            'ar': 'انتهت مهلة الاتصال',
            'en': 'Connection timeout',
            'solution': 'The website is taking too long to respond. Try again later'
        },
        'E005': {
            'ar': 'خطأ في تحليل الموقع',
            'en': 'Failed to parse website',
            'solution': 'The website structure could not be analyzed'
        },
        'E006': {
            'ar': 'خطأ في الصلاحيات',
            'en': 'Permission denied',
            'solution': 'Run the application as administrator or choose a different folder'
        },
        'E007': {
            'ar': 'خطأ في إنشاء الملفات',
            'en': 'File creation error',
            'solution': 'Check if the output folder is writable'
        },
        'E008': {
            'ar': 'خطأ في التحقق من البيانات',
            'en': 'Validation error',
            'solution': 'Check your input values'
        },
        'E009': {
            'ar': 'خطأ في توليد المشروع',
            'en': 'Project generation failed',
            'solution': 'Check error details and try again'
        },
        'E010': {
            'ar': 'خطأ غير متوقع',
            'en': 'Unexpected error',
            'solution': 'Please report this issue'
        }
    }
    
    @staticmethod
    def get_error(code: str, details: str = "") -> Dict[str, str]:
        """الحصول على رسالة خطأ مفصلة"""
        error_info = ErrorHandler.ERROR_MESSAGES.get(code, ErrorHandler.ERROR_MESSAGES['E010'])
        return {
            'code': code,
            'type': ErrorHandler.ERROR_CODES.get(code, 'UNKNOWN'),
            'message_ar': error_info['ar'],
            'message_en': error_info['en'],
            'solution': error_info['solution'],
            'details': details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def format_error(error: Dict[str, str]) -> str:
        """تنسيق رسالة الخطأ للعرض"""
        return f"""
ERROR [{error['code']}]: {error['message_en']}

Details: {error['details'] if error['details'] else 'No additional details'}

Solution: {error['solution']}

Time: {error['timestamp']}
"""


# ============================================
# PROGRESS TRACKER
# ============================================

class ProgressTracker:
    """متتبع التقدم مع تحديثات مفصلة"""
    
    def __init__(self, callback: Callable[[float, str, str], None]):
        self.callback = callback
        self.current_step = 0
        self.total_steps = 0
        self.current_task = ""
        self.sub_task = ""
        self.start_time = None
        
    def start(self, total_steps: int, task_name: str):
        """بدء تتبع التقدم"""
        self.total_steps = total_steps
        self.current_step = 0
        self.current_task = task_name
        self.start_time = time.time()
        self._update()
        
    def step(self, sub_task: str = ""):
        """الانتقال للخطوة التالية"""
        self.current_step += 1
        self.sub_task = sub_task
        self._update()
        
    def set_sub_task(self, sub_task: str):
        """تحديث المهمة الفرعية"""
        self.sub_task = sub_task
        self._update()
        
    def complete(self, message: str = "Complete"):
        """إكمال التقدم"""
        self.current_step = self.total_steps
        self.sub_task = message
        elapsed = time.time() - self.start_time if self.start_time else 0
        self._update(elapsed)
        
    def _update(self, elapsed: float = 0):
        """تحديث واجهة التقدم"""
        progress = self.current_step / self.total_steps if self.total_steps > 0 else 0
        status = f"{self.current_task}"
        if self.sub_task:
            status += f" - {self.sub_task}"
        if elapsed > 0:
            status += f" ({elapsed:.1f}s)"
        self.callback(progress, status, self.sub_task)


# ============================================
# WEBSITE ANALYZER
# ============================================

class WebsiteAnalyzer:
    """محلل المواقع المتقدم"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        
    def analyze(self, url: str) -> Dict[str, Any]:
        """تحليل الموقع واستخراج المعلومات"""
        result = {
            'success': False,
            'url': url,
            'title': '',
            'description': '',
            'theme_color': '#1a1a2e',
            'icons': [],
            'is_pwa': False,
            'is_responsive': False,
            'manifest': None,
            'error': None
        }
        
        try:
            # Validate URL
            if not url:
                result['error'] = ErrorHandler.get_error('E001')
                return result
                
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                result['url'] = url
                
            parsed = urlparse(url)
            if not parsed.netloc:
                result['error'] = ErrorHandler.get_error('E002', f"Invalid URL: {url}")
                return result
            
            # Fetch page
            if self.progress_callback:
                self.progress_callback(0.2, "Connecting to website...")
                
            response = requests.get(url, headers=self.HEADERS, timeout=20, allow_redirects=True)
            response.raise_for_status()
            
            if self.progress_callback:
                self.progress_callback(0.4, "Parsing HTML content...")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            result['title'] = self._extract_title(soup, parsed.netloc)
            
            if self.progress_callback:
                self.progress_callback(0.5, "Extracting metadata...")
            
            # Extract description
            result['description'] = self._extract_description(soup)
            
            # Extract theme color
            result['theme_color'] = self._extract_theme_color(soup)
            
            # Extract icons
            result['icons'] = self._extract_icons(soup, url)
            
            if self.progress_callback:
                self.progress_callback(0.7, "Checking PWA support...")
            
            # Check for PWA
            manifest_link = soup.find('link', rel='manifest')
            if manifest_link:
                result['is_pwa'] = True
                manifest_url = manifest_link.get('href', '')
                if manifest_url:
                    result['manifest'] = self._fetch_manifest(manifest_url, url)
            
            # Check responsiveness
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            result['is_responsive'] = viewport is not None
            
            if self.progress_callback:
                self.progress_callback(1.0, "Analysis complete!")
            
            result['success'] = True
            return result
            
        except requests.exceptions.Timeout:
            result['error'] = ErrorHandler.get_error('E004', f"Timeout connecting to {url}")
            return result
        except requests.exceptions.ConnectionError as e:
            result['error'] = ErrorHandler.get_error('E003', str(e))
            return result
        except requests.exceptions.HTTPError as e:
            result['error'] = ErrorHandler.get_error('E003', f"HTTP Error: {e.response.status_code}")
            return result
        except Exception as e:
            result['error'] = ErrorHandler.get_error('E005', str(e))
            return result
    
    def _extract_title(self, soup: BeautifulSoup, fallback: str) -> str:
        """استخراج عنوان الصفحة"""
        # Try og:title first
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try regular title
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Try h1
        h1 = soup.find('h1')
        if h1 and h1.text:
            return h1.text.strip()[:100]
        
        return fallback
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """استخراج وصف الصفحة"""
        # Try meta description
        desc = soup.find('meta', attrs={'name': 'description'})
        if desc and desc.get('content'):
            return desc['content'].strip()[:300]
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()[:300]
        
        # Try first paragraph
        p = soup.find('p')
        if p and p.text:
            return p.text.strip()[:300]
        
        return "No description available"
    
    def _extract_theme_color(self, soup: BeautifulSoup) -> str:
        """استخراج لون الثيم"""
        theme = soup.find('meta', attrs={'name': 'theme-color'})
        if theme and theme.get('content'):
            return theme['content']
        
        # Try msapplication-TileColor
        tile = soup.find('meta', attrs={'name': 'msapplication-TileColor'})
        if tile and tile.get('content'):
            return tile['content']
        
        return '#1a1a2e'
    
    def _extract_icons(self, soup: BeautifulSoup, base_url: str) -> list:
        """استخراج الأيقونات"""
        icons = []
        
        # Apple touch icons
        for link in soup.find_all('link', rel=lambda x: x and 'icon' in x.lower()):
            href = link.get('href', '')
            if href:
                if not href.startswith('http'):
                    href = f"{base_url.rstrip('/')}/{href.lstrip('/')}"
                sizes = link.get('sizes', '')
                icons.append({'url': href, 'sizes': sizes})
        
        return icons
    
    def _fetch_manifest(self, manifest_url: str, base_url: str) -> Optional[Dict]:
        """جلب ملف manifest"""
        try:
            if not manifest_url.startswith('http'):
                manifest_url = f"{base_url.rstrip('/')}/{manifest_url.lstrip('/')}"
            
            response = requests.get(manifest_url, headers=self.HEADERS, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None


# ============================================
# PROJECT GENERATOR
# ============================================

class AndroidProjectGenerator:
    """مولد مشاريع Android"""
    
    def __init__(self, progress_tracker: Optional[ProgressTracker] = None):
        self.progress = progress_tracker
        
    def generate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """توليد مشروع Android كامل"""
        result = {
            'success': False,
            'project_path': None,
            'error': None,
            'files_created': 0
        }
        
        try:
            # Validate config
            validation = self._validate_config(config)
            if not validation['valid']:
                result['error'] = ErrorHandler.get_error('E008', validation['message'])
                return result
            
            if self.progress:
                self.progress.start(10, "Generating Android Project")
            
            # Create project directory
            project_name = re.sub(r'[^a-zA-Z0-9]', '_', config['app_name'])
            project_dir = Path(config['output_path']) / f"{project_name}_Android"
            
            if project_dir.exists():
                shutil.rmtree(project_dir)
            
            if self.progress:
                self.progress.step("Creating directory structure")
            
            # Create directories
            self._create_directories(project_dir, config['package_name'])
            result['files_created'] += 1
            
            if self.progress:
                self.progress.step("Writing Gradle files")
            
            # Create Gradle files
            self._create_gradle_files(project_dir, config)
            result['files_created'] += 4
            
            if self.progress:
                self.progress.step("Writing Android Manifest")
            
            # Create AndroidManifest.xml
            self._create_manifest(project_dir, config)
            result['files_created'] += 1
            
            if self.progress:
                self.progress.step("Writing XML resources")
            
            # Create XML resources
            self._create_xml_resources(project_dir, config)
            result['files_created'] += 3
            
            if self.progress:
                self.progress.step("Writing Java source code")
            
            # Create MainActivity.java
            self._create_main_activity(project_dir, config)
            result['files_created'] += 1
            
            if self.progress:
                self.progress.step("Writing layout files")
            
            # Create layouts
            self._create_layouts(project_dir, config)
            result['files_created'] += 2
            
            if self.progress:
                self.progress.step("Writing resource files")
            
            # Create resources
            self._create_resources(project_dir, config)
            result['files_created'] += 3
            
            if self.progress:
                self.progress.step("Generating app icons")
            
            # Create icons
            self._create_icons(project_dir, config)
            result['files_created'] += 5
            
            if self.progress:
                self.progress.step("Writing build instructions")
            
            # Create instructions
            self._create_instructions(project_dir, config)
            result['files_created'] += 1
            
            if self.progress:
                self.progress.complete(f"Created {result['files_created']} files")
            
            result['success'] = True
            result['project_path'] = str(project_dir)
            return result
            
        except PermissionError as e:
            result['error'] = ErrorHandler.get_error('E006', str(e))
            return result
        except OSError as e:
            result['error'] = ErrorHandler.get_error('E007', str(e))
            return result
        except Exception as e:
            result['error'] = ErrorHandler.get_error('E009', f"{str(e)}\n{traceback.format_exc()}")
            return result
    
    def _validate_config(self, config: Dict) -> Dict[str, Any]:
        """التحقق من صحة الإعدادات"""
        if not config.get('url'):
            return {'valid': False, 'message': 'URL is required'}
        
        if not config.get('app_name'):
            return {'valid': False, 'message': 'App name is required'}
        
        if not config.get('package_name'):
            return {'valid': False, 'message': 'Package name is required'}
        
        package = config['package_name']
        if not re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', package):
            return {
                'valid': False, 
                'message': f'Invalid package name: {package}\nUse format: com.example.app (lowercase, min 2 parts)'
            }
        
        if not config.get('output_path'):
            return {'valid': False, 'message': 'Output path is required'}
        
        output = Path(config['output_path'])
        if not output.exists():
            return {'valid': False, 'message': f'Output directory does not exist: {output}'}
        
        return {'valid': True, 'message': 'OK'}
    
    def _create_directories(self, project_dir: Path, package_name: str):
        """إنشاء هيكل المجلدات"""
        package_path = package_name.replace('.', '/')
        
        directories = [
            f'app/src/main/java/{package_path}',
            'app/src/main/res/layout',
            'app/src/main/res/values',
            'app/src/main/res/values-ar',
            'app/src/main/res/drawable',
            'app/src/main/res/xml',
            'app/src/main/res/mipmap-hdpi',
            'app/src/main/res/mipmap-mdpi',
            'app/src/main/res/mipmap-xhdpi',
            'app/src/main/res/mipmap-xxhdpi',
            'app/src/main/res/mipmap-xxxhdpi',
            'gradle/wrapper'
        ]
        
        for d in directories:
            (project_dir / d).mkdir(parents=True, exist_ok=True)
    
    def _create_gradle_files(self, project_dir: Path, config: Dict):
        """إنشاء ملفات Gradle"""
        # Project level build.gradle
        project_gradle = '''// Top-level build file
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.2'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

tasks.register('clean', Delete) {
    delete rootProject.layout.buildDirectory
}
'''
        (project_dir / 'build.gradle').write_text(project_gradle, encoding='utf-8')
        
        # Parse version
        version = config.get('version', '1.0.0')
        version_parts = version.split('.')
        version_code = (
            int(version_parts[0]) * 10000 + 
            int(version_parts[1] if len(version_parts) > 1 else 0) * 100 + 
            int(version_parts[2] if len(version_parts) > 2 else 0)
        )
        
        # App level build.gradle
        app_gradle = f'''plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{config["package_name"]}'
    compileSdk 34

    defaultConfig {{
        applicationId "{config["package_name"]}"
        minSdk 24
        targetSdk 34
        versionCode {version_code}
        versionName "{version}"
    }}

    buildTypes {{
        release {{
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
        debug {{
            minifyEnabled false
            debuggable true
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
    
    buildFeatures {{
        viewBinding true
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.webkit:webkit:1.10.0'
    implementation 'androidx.swiperefreshlayout:swiperefreshlayout:1.1.0'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.core:core-splashscreen:1.0.1'
}}
'''
        (project_dir / 'app/build.gradle').write_text(app_gradle, encoding='utf-8')
        
        # settings.gradle
        app_name_safe = re.sub(r'[^a-zA-Z0-9]', '', config['app_name'])
        settings_gradle = f'''pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

dependencyResolutionManagement {{
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {{
        google()
        mavenCentral()
    }}
}}

rootProject.name = "{app_name_safe}"
include ':app'
'''
        (project_dir / 'settings.gradle').write_text(settings_gradle, encoding='utf-8')
        
        # gradle.properties
        gradle_properties = '''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
'''
        (project_dir / 'gradle.properties').write_text(gradle_properties, encoding='utf-8')
        
        # gradle wrapper properties
        wrapper_props = '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.5-bin.zip
networkTimeout=10000
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''
        (project_dir / 'gradle/wrapper/gradle-wrapper.properties').write_text(wrapper_props, encoding='utf-8')
        
        # proguard-rules.pro
        proguard = '''-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.webkit.WebViewClient
-keep public class * extends android.webkit.WebChromeClient
-dontwarn android.webkit.**
-keep class * implements android.os.Parcelable {
    public static final android.os.Parcelable$Creator *;
}
'''
        (project_dir / 'app/proguard-rules.pro').write_text(proguard, encoding='utf-8')
    
    def _create_manifest(self, project_dir: Path, config: Dict):
        """إنشاء AndroidManifest.xml"""
        orientation = config.get('orientation', 'portrait')
        
        manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" 
        android:maxSdkVersion="28"
        tools:ignore="ScopedStorage" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />
    <uses-feature android:name="android.hardware.microphone" android:required="false" />
    <uses-feature android:name="android.hardware.location" android:required="false" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.App.Starting"
        android:usesCleartextTraffic="true"
        android:networkSecurityConfig="@xml/network_security_config"
        android:hardwareAccelerated="true"
        android:largeHeap="true"
        tools:targetApi="34">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="{orientation}"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden|keyboard|navigation|uiMode"
            android:launchMode="singleTask"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${{applicationId}}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
        
    </application>
</manifest>
'''
        (project_dir / 'app/src/main/AndroidManifest.xml').write_text(manifest, encoding='utf-8')
    
    def _create_xml_resources(self, project_dir: Path, config: Dict):
        """إنشاء موارد XML"""
        xml_dir = project_dir / 'app/src/main/res/xml'
        
        # Network security config
        network_config = '''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
'''
        (xml_dir / 'network_security_config.xml').write_text(network_config, encoding='utf-8')
        
        # File paths
        file_paths = '''<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-path name="external" path="." />
    <external-files-path name="external_files" path="." />
    <cache-path name="cache" path="." />
    <files-path name="files" path="." />
</paths>
'''
        (xml_dir / 'file_paths.xml').write_text(file_paths, encoding='utf-8')
    
    def _create_main_activity(self, project_dir: Path, config: Dict):
        """إنشاء MainActivity.java"""
        package_path = config['package_name'].replace('.', '/')
        url = config['url']
        fullscreen = config.get('fullscreen', True)
        
        fullscreen_code = '''
        // Fullscreen mode
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            getWindow().setDecorFitsSystemWindows(false);
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                controller.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
        } else {
            getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            );
        }
''' if fullscreen else ''
        
        main_activity = f'''package {config["package_name"]};

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.webkit.*;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.splashscreen.SplashScreen;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {{

    // Constants
    private static final String TARGET_URL = "{url}";
    private static final int PERMISSION_REQUEST_CODE = 1001;
    private static final int FILE_CHOOSER_REQUEST = 1002;
    private static final int CAMERA_REQUEST = 1003;

    // Views
    private WebView webView;
    private ProgressBar progressBar;
    private ProgressBar loadingSpinner;
    private SwipeRefreshLayout swipeRefresh;
    private View errorLayout;
    private TextView errorMessage;
    private TextView progressText;

    // State
    private ValueCallback<Uri[]> filePathCallback;
    private String cameraPhotoPath;
    private boolean isLoading = true;
    private long lastBackPressTime = 0;
    private static final long BACK_PRESS_INTERVAL = 2000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        // Install splash screen
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        splashScreen.setKeepOnScreenCondition(() -> isLoading);
        
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        {fullscreen_code}
        // Initialize views
        initViews();
        
        // Check internet and load
        if (isNetworkAvailable()) {{
            setupWebView();
            webView.loadUrl(TARGET_URL);
        }} else {{
            showError("No Internet Connection", 
                "Please check your internet connection and try again.");
        }}
    }}

    private void initViews() {{
        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        loadingSpinner = findViewById(R.id.loadingSpinner);
        swipeRefresh = findViewById(R.id.swipeRefresh);
        errorLayout = findViewById(R.id.errorLayout);
        errorMessage = findViewById(R.id.errorMessage);
        progressText = findViewById(R.id.progressText);
        
        // Setup swipe refresh
        swipeRefresh.setOnRefreshListener(() -> {{
            if (isNetworkAvailable()) {{
                hideError();
                webView.reload();
            }} else {{
                swipeRefresh.setRefreshing(false);
                showError("No Internet", "Check your connection");
            }}
        }});
        swipeRefresh.setColorSchemeResources(
            android.R.color.holo_blue_bright,
            android.R.color.holo_green_light,
            android.R.color.holo_orange_light
        );
        
        // Retry button
        findViewById(R.id.retryButton).setOnClickListener(v -> {{
            if (isNetworkAvailable()) {{
                hideError();
                webView.reload();
            }} else {{
                Toast.makeText(this, "Still no internet connection", Toast.LENGTH_SHORT).show();
            }}
        }});
    }}

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {{
        WebSettings settings = webView.getSettings();
        
        // JavaScript
        settings.setJavaScriptEnabled(true);
        settings.setJavaScriptCanOpenWindowsAutomatically(true);
        
        // DOM Storage
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        
        // Cache
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setAppCacheEnabled(true);
        
        // File Access
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        
        // Zoom
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        
        // Viewport
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        
        // Media
        settings.setMediaPlaybackRequiresUserGesture(false);
        
        // Mixed content
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        
        // User agent
        String userAgent = settings.getUserAgentString();
        settings.setUserAgentString(userAgent + " AndroidApp");
        
        // WebViewClient
        webView.setWebViewClient(new CustomWebViewClient());
        
        // WebChromeClient
        webView.setWebChromeClient(new CustomWebChromeClient());
        
        // Download listener
        webView.setDownloadListener(this::handleDownload);
    }}

    private class CustomWebViewClient extends WebViewClient {{
        @Override
        public void onPageStarted(WebView view, String url, Bitmap favicon) {{
            super.onPageStarted(view, url, favicon);
            progressBar.setVisibility(View.VISIBLE);
            loadingSpinner.setVisibility(View.VISIBLE);
            progressText.setVisibility(View.VISIBLE);
            progressText.setText("Loading...");
        }}

        @Override
        public void onPageFinished(WebView view, String url) {{
            super.onPageFinished(view, url);
            progressBar.setVisibility(View.GONE);
            loadingSpinner.setVisibility(View.GONE);
            progressText.setVisibility(View.GONE);
            swipeRefresh.setRefreshing(false);
            isLoading = false;
        }}

        @Override
        public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {{
            super.onReceivedError(view, request, error);
            if (request.isForMainFrame()) {{
                String errorDesc = "Error loading page";
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {{
                    errorDesc = error.getDescription().toString();
                }}
                showError("Loading Error", errorDesc);
            }}
        }}

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {{
            String url = request.getUrl().toString();
            
            // Handle external links
            if (url.startsWith("tel:") || url.startsWith("mailto:") || 
                url.startsWith("whatsapp:") || url.startsWith("intent:") ||
                url.startsWith("sms:") || url.startsWith("geo:")) {{
                try {{
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                }} catch (Exception e) {{
                    Toast.makeText(MainActivity.this, "Cannot open: " + url, Toast.LENGTH_SHORT).show();
                }}
                return true;
            }}
            
            // Handle external URLs (optional - open in browser)
            // Uncomment if you want external links to open in browser
            /*
            if (!url.contains(TARGET_URL)) {{
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                startActivity(intent);
                return true;
            }}
            */
            
            return false;
        }}
    }}

    private class CustomWebChromeClient extends WebChromeClient {{
        @Override
        public void onProgressChanged(WebView view, int newProgress) {{
            progressBar.setProgress(newProgress);
            progressText.setText("Loading... " + newProgress + "%");
        }}

        @Override
        public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                        FileChooserParams fileChooserParams) {{
            MainActivity.this.filePathCallback = filePathCallback;
            
            // Check for camera permission if image capture
            String[] acceptTypes = fileChooserParams.getAcceptTypes();
            boolean needsCamera = false;
            for (String type : acceptTypes) {{
                if (type.contains("image")) {{
                    needsCamera = true;
                    break;
                }}
            }}
            
            if (needsCamera && !hasCameraPermission()) {{
                requestCameraPermission();
                return true;
            }}
            
            Intent intent = fileChooserParams.createIntent();
            try {{
                startActivityForResult(intent, FILE_CHOOSER_REQUEST);
            }} catch (Exception e) {{
                Toast.makeText(MainActivity.this, "Cannot open file chooser", Toast.LENGTH_SHORT).show();
                filePathCallback.onReceiveValue(null);
                return false;
            }}
            return true;
        }}

        @Override
        public void onPermissionRequest(final PermissionRequest request) {{
            runOnUiThread(() -> {{
                String[] resources = request.getResources();
                List<String> neededPermissions = new ArrayList<>();
                
                for (String resource : resources) {{
                    if (resource.equals(PermissionRequest.RESOURCE_VIDEO_CAPTURE)) {{
                        if (!hasCameraPermission()) {{
                            neededPermissions.add(Manifest.permission.CAMERA);
                        }}
                    }} else if (resource.equals(PermissionRequest.RESOURCE_AUDIO_CAPTURE)) {{
                        if (!hasAudioPermission()) {{
                            neededPermissions.add(Manifest.permission.RECORD_AUDIO);
                        }}
                    }}
                }}
                
                if (neededPermissions.isEmpty()) {{
                    request.grant(resources);
                }} else {{
                    // Request permissions
                    ActivityCompat.requestPermissions(MainActivity.this,
                        neededPermissions.toArray(new String[0]),
                        PERMISSION_REQUEST_CODE);
                    // Grant anyway (will be denied by system if not permitted)
                    request.grant(resources);
                }}
            }});
        }}

        @Override
        public void onGeolocationPermissionsShowPrompt(String origin, 
                GeolocationPermissions.Callback callback) {{
            if (hasLocationPermission()) {{
                callback.invoke(origin, true, false);
            }} else {{
                requestLocationPermission();
                callback.invoke(origin, false, false);
            }}
        }}
        
        @Override
        public boolean onJsAlert(WebView view, String url, String message, JsResult result) {{
            new AlertDialog.Builder(MainActivity.this)
                .setTitle("Alert")
                .setMessage(message)
                .setPositiveButton("OK", (dialog, which) -> result.confirm())
                .setCancelable(false)
                .show();
            return true;
        }}
        
        @Override
        public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {{
            new AlertDialog.Builder(MainActivity.this)
                .setTitle("Confirm")
                .setMessage(message)
                .setPositiveButton("OK", (dialog, which) -> result.confirm())
                .setNegativeButton("Cancel", (dialog, which) -> result.cancel())
                .setCancelable(false)
                .show();
            return true;
        }}
    }}

    private void handleDownload(String url, String userAgent, String contentDisposition, 
                               String mimeType, long contentLength) {{
        if (checkStoragePermission()) {{
            downloadFile(url, contentDisposition, mimeType);
        }}
    }}

    private void downloadFile(String url, String contentDisposition, String mimeType) {{
        try {{
            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
            String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
            
            request.setTitle(fileName);
            request.setDescription("Downloading...");
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);
            request.setMimeType(mimeType);
            request.allowScanningByMediaScanner();

            DownloadManager dm = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
            dm.enqueue(request);
            
            Toast.makeText(this, "Downloading: " + fileName, Toast.LENGTH_SHORT).show();
        }} catch (Exception e) {{
            Toast.makeText(this, "Download failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }}
    }}

    // Permission helpers
    private boolean hasCameraPermission() {{
        return ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) 
            == PackageManager.PERMISSION_GRANTED;
    }}
    
    private boolean hasAudioPermission() {{
        return ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) 
            == PackageManager.PERMISSION_GRANTED;
    }}
    
    private boolean hasLocationPermission() {{
        return ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) 
            == PackageManager.PERMISSION_GRANTED;
    }}
    
    private boolean checkStoragePermission() {{
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {{
            return true;
        }}
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE)
                != PackageManager.PERMISSION_GRANTED) {{
            ActivityCompat.requestPermissions(this,
                new String[]{{Manifest.permission.WRITE_EXTERNAL_STORAGE}},
                PERMISSION_REQUEST_CODE);
            return false;
        }}
        return true;
    }}
    
    private void requestCameraPermission() {{
        ActivityCompat.requestPermissions(this, 
            new String[]{{Manifest.permission.CAMERA}}, CAMERA_REQUEST);
    }}
    
    private void requestLocationPermission() {{
        ActivityCompat.requestPermissions(this, 
            new String[]{{Manifest.permission.ACCESS_FINE_LOCATION, 
                         Manifest.permission.ACCESS_COARSE_LOCATION}}, 
            PERMISSION_REQUEST_CODE);
    }}

    // Network check
    private boolean isNetworkAvailable() {{
        ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        if (cm == null) return false;
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {{
            NetworkCapabilities caps = cm.getNetworkCapabilities(cm.getActiveNetwork());
            return caps != null && (
                caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ||
                caps.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET)
            );
        }} else {{
            android.net.NetworkInfo activeNetwork = cm.getActiveNetworkInfo();
            return activeNetwork != null && activeNetwork.isConnected();
        }}
    }}

    // Error handling
    private void showError(String title, String message) {{
        runOnUiThread(() -> {{
            errorLayout.setVisibility(View.VISIBLE);
            webView.setVisibility(View.GONE);
            progressBar.setVisibility(View.GONE);
            loadingSpinner.setVisibility(View.GONE);
            progressText.setVisibility(View.GONE);
            swipeRefresh.setRefreshing(false);
            errorMessage.setText(title + "\\n\\n" + message);
            isLoading = false;
        }});
    }}
    
    private void hideError() {{
        errorLayout.setVisibility(View.GONE);
        webView.setVisibility(View.VISIBLE);
    }}

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {{
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == FILE_CHOOSER_REQUEST) {{
            if (filePathCallback != null) {{
                Uri[] results = null;
                if (resultCode == Activity.RESULT_OK && data != null) {{
                    String dataString = data.getDataString();
                    if (dataString != null) {{
                        results = new Uri[]{{Uri.parse(dataString)}};
                    }}
                }}
                filePathCallback.onReceiveValue(results);
                filePathCallback = null;
            }}
        }}
    }}

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                          @NonNull int[] grantResults) {{
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {{
            Toast.makeText(this, "Permission granted", Toast.LENGTH_SHORT).show();
        }}
    }}

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {{
        if (keyCode == KeyEvent.KEYCODE_BACK) {{
            if (webView.canGoBack()) {{
                webView.goBack();
                return true;
            }} else {{
                // Double tap to exit
                if (System.currentTimeMillis() - lastBackPressTime < BACK_PRESS_INTERVAL) {{
                    finish();
                }} else {{
                    lastBackPressTime = System.currentTimeMillis();
                    Toast.makeText(this, "Press back again to exit", Toast.LENGTH_SHORT).show();
                }}
                return true;
            }}
        }}
        return super.onKeyDown(keyCode, event);
    }}

    @Override
    protected void onResume() {{
        super.onResume();
        if (webView != null) {{
            webView.onResume();
            webView.resumeTimers();
        }}
    }}

    @Override
    protected void onPause() {{
        super.onPause();
        if (webView != null) {{
            webView.onPause();
            webView.pauseTimers();
        }}
    }}

    @Override
    protected void onDestroy() {{
        if (webView != null) {{
            webView.stopLoading();
            webView.clearHistory();
            webView.clearCache(true);
            webView.loadUrl("about:blank");
            webView.removeAllViews();
            webView.destroy();
            webView = null;
        }}
        super.onDestroy();
    }}
}}
'''
        java_dir = project_dir / f'app/src/main/java/{package_path}'
        (java_dir / 'MainActivity.java').write_text(main_activity, encoding='utf-8')
    
    def _create_layouts(self, project_dir: Path, config: Dict):
        """إنشاء ملفات Layout"""
        layout_dir = project_dir / 'app/src/main/res/layout'
        
        # activity_main.xml
        activity_main = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.coordinatorlayout.widget.CoordinatorLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@color/background">

    <androidx.swiperefreshlayout.widget.SwipeRefreshLayout
        android:id="@+id/swipeRefresh"
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <FrameLayout
            android:layout_width="match_parent"
            android:layout_height="match_parent">

            <WebView
                android:id="@+id/webView"
                android:layout_width="match_parent"
                android:layout_height="match_parent" />

            <!-- Loading Overlay -->
            <LinearLayout
                android:id="@+id/loadingOverlay"
                android:layout_width="match_parent"
                android:layout_height="match_parent"
                android:orientation="vertical"
                android:gravity="center"
                android:background="@color/background"
                android:visibility="gone">

                <ProgressBar
                    android:id="@+id/loadingSpinner"
                    android:layout_width="64dp"
                    android:layout_height="64dp"
                    android:indeterminate="true"
                    android:indeterminateTint="@color/primary" />

                <TextView
                    android:id="@+id/progressText"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="16dp"
                    android:text="Loading..."
                    android:textColor="@color/textSecondary"
                    android:textSize="14sp" />
            </LinearLayout>

            <!-- Error Layout -->
            <LinearLayout
                android:id="@+id/errorLayout"
                android:layout_width="match_parent"
                android:layout_height="match_parent"
                android:orientation="vertical"
                android:gravity="center"
                android:padding="32dp"
                android:background="@color/background"
                android:visibility="gone">

                <ImageView
                    android:layout_width="120dp"
                    android:layout_height="120dp"
                    android:src="@drawable/ic_error"
                    android:contentDescription="Error"
                    app:tint="@color/error" />

                <TextView
                    android:id="@+id/errorMessage"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="24dp"
                    android:text="Something went wrong"
                    android:textColor="@color/textPrimary"
                    android:textSize="16sp"
                    android:textAlignment="center"
                    android:gravity="center" />

                <com.google.android.material.button.MaterialButton
                    android:id="@+id/retryButton"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:layout_marginTop="24dp"
                    android:text="Try Again"
                    android:textColor="@color/white"
                    app:backgroundTint="@color/primary"
                    app:cornerRadius="24dp"
                    android:paddingStart="32dp"
                    android:paddingEnd="32dp" />

            </LinearLayout>

        </FrameLayout>

    </androidx.swiperefreshlayout.widget.SwipeRefreshLayout>

    <!-- Top Progress Bar -->
    <ProgressBar
        android:id="@+id/progressBar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="3dp"
        android:layout_gravity="top"
        android:indeterminate="false"
        android:max="100"
        android:progress="0"
        android:progressTint="@color/primary"
        android:progressBackgroundTint="@android:color/transparent"
        android:visibility="gone" />

</androidx.coordinatorlayout.widget.CoordinatorLayout>
'''
        (layout_dir / 'activity_main.xml').write_text(activity_main, encoding='utf-8')
    
    def _create_resources(self, project_dir: Path, config: Dict):
        """إنشاء ملفات الموارد"""
        values_dir = project_dir / 'app/src/main/res/values'
        values_ar_dir = project_dir / 'app/src/main/res/values-ar'
        
        # colors.xml
        theme_color = config.get('theme_color', '#2196F3')
        colors = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary">{theme_color}</color>
    <color name="primaryDark">#1976D2</color>
    <color name="accent">#FF4081</color>
    <color name="background">#FFFFFF</color>
    <color name="backgroundDark">#121212</color>
    <color name="surface">#FFFFFF</color>
    <color name="error">#B00020</color>
    <color name="textPrimary">#212121</color>
    <color name="textSecondary">#757575</color>
    <color name="white">#FFFFFF</color>
    <color name="black">#000000</color>
    <color name="splash_background">{theme_color}</color>
</resources>
'''
        (values_dir / 'colors.xml').write_text(colors, encoding='utf-8')
        
        # strings.xml
        strings = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{config["app_name"]}</string>
    <string name="loading">Loading...</string>
    <string name="no_internet">No Internet Connection</string>
    <string name="retry">Try Again</string>
    <string name="error_loading">Error loading page</string>
    <string name="download_started">Download started</string>
    <string name="download_failed">Download failed</string>
    <string name="permission_granted">Permission granted</string>
    <string name="press_back_again">Press back again to exit</string>
</resources>
'''
        (values_dir / 'strings.xml').write_text(strings, encoding='utf-8')
        
        # strings-ar.xml (Arabic)
        strings_ar = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{config["app_name"]}</string>
    <string name="loading">جاري التحميل...</string>
    <string name="no_internet">لا يوجد اتصال بالإنترنت</string>
    <string name="retry">حاول مجدداً</string>
    <string name="error_loading">خطأ في تحميل الصفحة</string>
    <string name="download_started">بدأ التحميل</string>
    <string name="download_failed">فشل التحميل</string>
    <string name="permission_granted">تم منح الصلاحية</string>
    <string name="press_back_again">اضغط مرة أخرى للخروج</string>
</resources>
'''
        (values_ar_dir / 'strings.xml').write_text(strings_ar, encoding='utf-8')
        
        # themes.xml
        fullscreen = config.get('fullscreen', True)
        fullscreen_items = '''
        <item name="android:windowFullscreen">true</item>
        <item name="android:windowContentOverlay">@null</item>''' if fullscreen else ''
        
        themes = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Base theme -->
    <style name="Theme.App" parent="Theme.MaterialComponents.Light.NoActionBar">
        <item name="colorPrimary">@color/primary</item>
        <item name="colorPrimaryDark">@color/primaryDark</item>
        <item name="colorAccent">@color/accent</item>
        <item name="android:windowBackground">@color/background</item>
        <item name="android:statusBarColor">@color/primary</item>
        <item name="android:navigationBarColor">@color/primary</item>{fullscreen_items}
    </style>

    <!-- Splash screen theme -->
    <style name="Theme.App.Starting" parent="Theme.SplashScreen">
        <item name="windowSplashScreenBackground">@color/splash_background</item>
        <item name="windowSplashScreenAnimatedIcon">@mipmap/ic_launcher</item>
        <item name="postSplashScreenTheme">@style/Theme.App</item>
    </style>
</resources>
'''
        (values_dir / 'themes.xml').write_text(themes, encoding='utf-8')
    
    def _create_icons(self, project_dir: Path, config: Dict):
        """إنشاء أيقونات التطبيق"""
        drawable_dir = project_dir / 'app/src/main/res/drawable'
        
        # Error icon
        error_icon = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#B00020"
        android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM13,17h-2v-2h2v2zM13,13h-2V7h2v6z"/>
</vector>
'''
        (drawable_dir / 'ic_error.xml').write_text(error_icon, encoding='utf-8')
        
        # Create simple launcher icons (colored squares as placeholder)
        icon_sizes = {
            'mipmap-mdpi': 48,
            'mipmap-hdpi': 72,
            'mipmap-xhdpi': 96,
            'mipmap-xxhdpi': 144,
            'mipmap-xxxhdpi': 192
        }
        
        theme_color = config.get('theme_color', '#2196F3')
        
        if HAS_PIL:
            for folder, size in icon_sizes.items():
                mipmap_dir = project_dir / 'app/src/main/res' / folder
                
                # Create square icon
                img = Image.new('RGB', (size, size), theme_color)
                draw = ImageDraw.Draw(img)
                
                # Add rounded corners effect
                img.save(mipmap_dir / 'ic_launcher.png', 'PNG')
                
                # Create round icon
                mask = Image.new('L', (size, size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, size, size], fill=255)
                
                round_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                round_img.paste(img, mask=mask)
                round_img.save(mipmap_dir / 'ic_launcher_round.png', 'PNG')
        else:
            # Create XML adaptive icons as fallback
            for folder in icon_sizes.keys():
                mipmap_dir = project_dir / 'app/src/main/res' / folder
                
                # ic_launcher.xml
                launcher_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/primary"/>
    <foreground android:drawable="@color/white"/>
</adaptive-icon>
'''
                (mipmap_dir / 'ic_launcher.xml').write_text(launcher_xml, encoding='utf-8')
                (mipmap_dir / 'ic_launcher_round.xml').write_text(launcher_xml, encoding='utf-8')
    
    def _create_instructions(self, project_dir: Path, config: Dict):
        """إنشاء ملف التعليمات"""
        instructions = f'''================================================================================
                        BUILD INSTRUCTIONS
                        {config["app_name"]}
================================================================================

GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
PACKAGE: {config["package_name"]}
VERSION: {config.get("version", "1.0.0")}
TARGET URL: {config["url"]}

================================================================================
                        OPTION 1: ANDROID STUDIO (RECOMMENDED)
================================================================================

1. INSTALL ANDROID STUDIO
   Download from: https://developer.android.com/studio
   - Install with default settings
   - Accept all SDK licenses when prompted

2. OPEN PROJECT
   - Launch Android Studio
   - Click "Open" or "Open an Existing Project"
   - Navigate to: {project_dir}
   - Click OK and wait for Gradle sync

3. BUILD DEBUG APK
   - Wait for Gradle sync to complete (may take 5-10 minutes first time)
   - Click: Build > Build Bundle(s) / APK(s) > Build APK(s)
   - APK location: app/build/outputs/apk/debug/app-debug.apk

4. BUILD RELEASE APK (for Google Play)
   - Click: Build > Generate Signed Bundle / APK
   - Select "APK" and click Next
   - Create new keystore or use existing
   - Fill in key information and click Next
   - Select "release" and click Finish
   - APK location: app/build/outputs/apk/release/app-release.apk

================================================================================
                        OPTION 2: COMMAND LINE
================================================================================

REQUIREMENTS:
- Java JDK 17 or higher
- Android SDK with Build Tools 34
- ANDROID_HOME environment variable set

STEPS:
1. Open terminal/command prompt in this directory

2. Make gradlew executable (Linux/Mac):
   chmod +x gradlew

3. Build debug APK:
   ./gradlew assembleDebug     (Linux/Mac)
   gradlew.bat assembleDebug   (Windows)

4. Build release APK:
   ./gradlew assembleRelease

================================================================================
                        CUSTOMIZATION
================================================================================

CHANGE APP ICON:
- Replace files in app/src/main/res/mipmap-* folders
- Use Android Asset Studio: https://romannurik.github.io/AndroidAssetStudio/

CHANGE COLORS:
- Edit: app/src/main/res/values/colors.xml

CHANGE APP NAME:
- Edit: app/src/main/res/values/strings.xml

CHANGE PERMISSIONS:
- Edit: app/src/main/AndroidManifest.xml

================================================================================
                        TROUBLESHOOTING
================================================================================

GRADLE SYNC FAILED:
- Check internet connection
- Try: File > Invalidate Caches / Restart
- Delete .gradle folder and re-sync

BUILD FAILED:
- Ensure SDK 34 is installed
- Check for error messages in Build output
- Update Gradle if prompted

ICON NOT SHOWING:
- Ensure all mipmap folders have icons
- Icons must be PNG format

================================================================================
                        SUPPORT
================================================================================

For issues, check:
- Android Developer Documentation: https://developer.android.com
- Stack Overflow: https://stackoverflow.com/questions/tagged/android

================================================================================
'''
        (project_dir / 'BUILD_INSTRUCTIONS.txt').write_text(instructions, encoding='utf-8')


# ============================================
# MAIN APPLICATION
# ============================================

class URLToAPKApp(ctk.CTk):
    """التطبيق الرئيسي"""
    
    VERSION = "2.0.0"
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title(f"URL to APK Converter v{self.VERSION}")
        self.geometry("950x750")
        self.minsize(900, 700)
        
        # Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.url_var = ctk.StringVar()
        self.app_name_var = ctk.StringVar()
        self.package_name_var = ctk.StringVar(value="com.app.myapp")
        self.version_var = ctk.StringVar(value="1.0.0")
        self.output_path_var = ctk.StringVar(value=str(Path.home() / "Desktop"))
        self.orientation_var = ctk.StringVar(value="portrait")
        self.fullscreen_var = ctk.BooleanVar(value=True)
        self.progress_var = ctk.DoubleVar(value=0)
        self.status_var = ctk.StringVar(value="Ready - Enter a URL to begin")
        
        # State
        self.site_info: Dict[str, Any] = {}
        self.is_processing = False
        
        # Build UI
        self._build_ui()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _build_ui(self):
        """بناء واجهة المستخدم"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._build_header()
        
        # Content
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Left panel
        self._build_input_panel()
        
        # Right panel
        self._build_settings_panel()
        
        # Bottom panel
        self._build_bottom_panel()
    
    def _build_header(self):
        """بناء الهيدر"""
        header = ctk.CTkFrame(self.main_frame, fg_color="#1a1a2e", corner_radius=15, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Title section
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=25, pady=15)
        
        title = ctk.CTkLabel(
            title_frame,
            text="URL to APK Converter",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color="#00d4ff"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Convert any website to a native Android application",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle.pack(anchor="w", pady=(2, 0))
        
        # Version badge
        version_frame = ctk.CTkFrame(header, fg_color="#333355", corner_radius=8)
        version_frame.pack(side="right", padx=25)
        
        version_label = ctk.CTkLabel(
            version_frame,
            text=f"v{self.VERSION}",
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa"
        )
        version_label.pack(padx=12, pady=6)
    
    def _build_input_panel(self):
        """بناء لوحة الإدخال"""
        left_panel = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # URL Section
        self._create_section(scroll, "Website URL", self._create_url_input)
        
        # App Name
        self._create_section(scroll, "App Name", self._create_name_input)
        
        # Package Name
        self._create_section(scroll, "Package Name", self._create_package_input)
        
        # Version
        self._create_section(scroll, "Version", self._create_version_input)
        
        # Output Path
        self._create_section(scroll, "Output Directory", self._create_output_input)
    
    def _create_section(self, parent, title: str, content_builder):
        """إنشاء قسم مع عنوان"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=(15, 0))
        
        label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        label.pack(anchor="w", pady=(0, 8))
        
        content_builder(frame)
    
    def _create_url_input(self, parent):
        """إنشاء حقل URL"""
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.url_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.url_var,
            placeholder_text="https://example.com",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.analyze_btn = ctk.CTkButton(
            input_frame,
            text="Analyze",
            width=100,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0066cc",
            hover_color="#0055aa",
            corner_radius=10,
            command=self._on_analyze
        )
        self.analyze_btn.pack(side="right")
        
        # Help text
        help_text = ctk.CTkLabel(
            parent,
            text="Enter the full URL of the website you want to convert",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        help_text.pack(anchor="w", pady=(4, 0))
    
    def _create_name_input(self, parent):
        """إنشاء حقل اسم التطبيق"""
        self.name_entry = ctk.CTkEntry(
            parent,
            textvariable=self.app_name_var,
            placeholder_text="My Awesome App",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.name_entry.pack(fill="x")
    
    def _create_package_input(self, parent):
        """إنشاء حقل اسم الحزمة"""
        self.package_entry = ctk.CTkEntry(
            parent,
            textvariable=self.package_name_var,
            placeholder_text="com.company.appname",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.package_entry.pack(fill="x")
        
        help_text = ctk.CTkLabel(
            parent,
            text="Format: com.company.app (lowercase, min 2 parts)",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        help_text.pack(anchor="w", pady=(4, 0))
    
    def _create_version_input(self, parent):
        """إنشاء حقل الإصدار"""
        self.version_entry = ctk.CTkEntry(
            parent,
            textvariable=self.version_var,
            placeholder_text="1.0.0",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.version_entry.pack(fill="x")
    
    def _create_output_input(self, parent):
        """إنشاء حقل مسار الإخراج"""
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.output_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.output_path_var,
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            input_frame,
            text="Browse",
            width=80,
            height=45,
            font=ctk.CTkFont(size=13),
            fg_color="#444466",
            hover_color="#555577",
            corner_radius=10,
            command=self._browse_output
        )
        browse_btn.pack(side="right")
    
    def _build_settings_panel(self):
        """بناء لوحة الإعدادات"""
        right_panel = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=15, width=380)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Preview section
        preview_label = ctk.CTkLabel(
            right_panel,
            text="Site Analysis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        preview_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.preview_frame = ctk.CTkFrame(right_panel, fg_color="#0f0f23", corner_radius=12, height=140)
        self.preview_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.preview_frame.pack_propagate(False)
        
        self.preview_title = ctk.CTkLabel(
            self.preview_frame,
            text="No site analyzed yet",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#666666"
        )
        self.preview_title.pack(pady=(20, 5))
        
        self.preview_desc = ctk.CTkLabel(
            self.preview_frame,
            text="Enter a URL and click Analyze to see site information",
            font=ctk.CTkFont(size=12),
            text_color="#444444",
            wraplength=300
        )
        self.preview_desc.pack()
        
        self.preview_badges = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.preview_badges.pack(pady=(10, 0))
        
        # Settings section
        settings_label = ctk.CTkLabel(
            right_panel,
            text="APK Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        settings_label.pack(anchor="w", padx=20, pady=(10, 10))
        
        # Orientation
        orientation_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        orientation_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        orientation_label = ctk.CTkLabel(
            orientation_frame,
            text="Screen Orientation",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa"
        )
        orientation_label.pack(anchor="w", pady=(0, 8))
        
        orientations = ctk.CTkFrame(orientation_frame, fg_color="transparent")
        orientations.pack(fill="x")
        
        for text, value in [("Portrait", "portrait"), ("Landscape", "landscape"), ("Auto", "unspecified")]:
            radio = ctk.CTkRadioButton(
                orientations,
                text=text,
                variable=self.orientation_var,
                value=value,
                font=ctk.CTkFont(size=12)
            )
            radio.pack(side="left", padx=(0, 15))
        
        # Fullscreen
        fullscreen_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        fullscreen_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.fullscreen_check = ctk.CTkCheckBox(
            fullscreen_frame,
            text="Enable Fullscreen Mode",
            variable=self.fullscreen_var,
            font=ctk.CTkFont(size=13),
            checkbox_width=22,
            checkbox_height=22
        )
        self.fullscreen_check.pack(anchor="w")
        
        # Features
        features_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a3a", corner_radius=10)
        features_frame.pack(fill="x", padx=20, pady=(5, 0))
        
        features_title = ctk.CTkLabel(
            features_frame,
            text="Included Features",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00d4ff"
        )
        features_title.pack(anchor="w", padx=15, pady=(12, 8))
        
        features = [
            "JavaScript & DOM Storage support",
            "File upload & download",
            "Camera & microphone access",
            "Geolocation support",
            "Pull-to-refresh gesture",
            "Smart back button handling",
            "Offline caching",
            "Splash screen"
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"  {feature}",
                font=ctk.CTkFont(size=11),
                text_color="#888888"
            )
            feature_label.pack(anchor="w", padx=15, pady=2)
        
        ctk.CTkLabel(features_frame, text="", height=10).pack()
    
    def _build_bottom_panel(self):
        """بناء اللوحة السفلية"""
        bottom = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=130)
        bottom.pack(fill="x", pady=(20, 0))
        
        # Progress section
        progress_frame = ctk.CTkFrame(bottom, fg_color="#16213e", corner_radius=12)
        progress_frame.pack(fill="x", pady=(0, 15))
        
        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(fill="x", padx=20, pady=15)
        
        # Status with icon
        status_frame = ctk.CTkFrame(progress_inner, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 8))
        
        self.status_icon = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#00d4ff",
            width=20
        )
        self.status_icon.pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            variable=self.progress_var,
            height=10,
            corner_radius=5,
            fg_color="#1a1a2e",
            progress_color="#00d4ff"
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Action buttons
        action_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        action_frame.pack(fill="x")
        
        self.generate_btn = ctk.CTkButton(
            action_frame,
            text="Generate Android Project",
            height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#00aa55",
            hover_color="#008844",
            corner_radius=12,
            command=self._on_generate
        )
        self.generate_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.open_btn = ctk.CTkButton(
            action_frame,
            text="Open Output",
            height=55,
            width=140,
            font=ctk.CTkFont(size=14),
            fg_color="#444466",
            hover_color="#555577",
            corner_radius=12,
            command=self._open_output
        )
        self.open_btn.pack(side="right")
    
    # ============================================
    # EVENT HANDLERS
    # ============================================
    
    def _browse_output(self):
        """اختيار مجلد الإخراج"""
        folder = filedialog.askdirectory(initialdir=self.output_path_var.get())
        if folder:
            self.output_path_var.set(folder)
    
    def _on_analyze(self):
        """تحليل الموقع"""
        if self.is_processing:
            return
            
        url = self.url_var.get().strip()
        if not url:
            self._show_error("Please enter a URL first")
            return
        
        self.is_processing = True
        self.analyze_btn.configure(state="disabled", text="Analyzing...")
        self.status_var.set("Analyzing website...")
        self.progress_var.set(0.1)
        
        thread = threading.Thread(target=self._analyze_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _analyze_thread(self, url: str):
        """خيط تحليل الموقع"""
        def update_progress(value: float, message: str):
            self.after(0, lambda: self.progress_var.set(value))
            self.after(0, lambda: self.status_var.set(message))
        
        analyzer = WebsiteAnalyzer(progress_callback=update_progress)
        result = analyzer.analyze(url)
        
        self.after(0, lambda: self._on_analyze_complete(result))
    
    def _on_analyze_complete(self, result: Dict[str, Any]):
        """عند اكتمال التحليل"""
        self.is_processing = False
        self.analyze_btn.configure(state="normal", text="Analyze")
        
        if result['success']:
            self.site_info = result
            self._update_preview(result)
            self.progress_var.set(1.0)
            
            pwa = " (PWA)" if result.get('is_pwa') else ""
            self.status_var.set(f"Analysis complete{pwa} - Ready to generate")
        else:
            error = result.get('error', {})
            self._show_error(ErrorHandler.format_error(error))
            self.progress_var.set(0)
            self.status_var.set(f"Error: {error.get('message_en', 'Unknown error')}")
    
    def _update_preview(self, info: Dict[str, Any]):
        """تحديث معاينة الموقع"""
        self.preview_title.configure(
            text=info.get('title', 'Unknown'),
            text_color="#ffffff"
        )
        
        desc = info.get('description', 'No description')
        if len(desc) > 150:
            desc = desc[:150] + "..."
        self.preview_desc.configure(
            text=desc,
            text_color="#aaaaaa"
        )
        
        # Clear old badges
        for widget in self.preview_badges.winfo_children():
            widget.destroy()
        
        # Add badges
        if info.get('is_pwa'):
            self._add_badge(self.preview_badges, "PWA", "#00aa55")
        if info.get('is_responsive'):
            self._add_badge(self.preview_badges, "Responsive", "#0066cc")
        
        # Auto-fill app name
        if not self.app_name_var.get():
            title = info.get('title', 'My App')
            # Clean title
            title = re.sub(r'[|–-].*$', '', title).strip()
            self.app_name_var.set(title[:50])
        
        # Generate package name
        parsed = urlparse(info['url'])
        domain = parsed.netloc.replace('www.', '')
        parts = domain.split('.')
        
        if len(parts) >= 2:
            # Reverse domain
            clean_parts = [re.sub(r'[^a-z0-9]', '', p.lower()) for p in reversed(parts)]
            clean_parts = [p for p in clean_parts if p]
            if clean_parts:
                package = '.'.join(clean_parts)
                self.package_name_var.set(package)
    
    def _add_badge(self, parent, text: str, color: str):
        """إضافة شارة"""
        badge = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=color,
            corner_radius=4,
            text_color="white"
        )
        badge.pack(side="left", padx=2)
    
    def _on_generate(self):
        """توليد مشروع Android"""
        if self.is_processing:
            return
        
        # Validate
        url = self.url_var.get().strip()
        app_name = self.app_name_var.get().strip()
        package_name = self.package_name_var.get().strip()
        
        if not url:
            self._show_error("Please enter a URL first")
            return
        if not app_name:
            self._show_error("Please enter an app name")
            return
        if not package_name:
            self._show_error("Please enter a package name")
            return
        
        # Start generation
        self.is_processing = True
        self.generate_btn.configure(state="disabled", text="Generating...")
        self.progress_var.set(0)
        
        config = {
            'url': url if url.startswith('http') else f'https://{url}',
            'app_name': app_name,
            'package_name': package_name,
            'version': self.version_var.get() or "1.0.0",
            'output_path': self.output_path_var.get(),
            'orientation': self.orientation_var.get(),
            'fullscreen': self.fullscreen_var.get(),
            'theme_color': self.site_info.get('theme_color', '#2196F3')
        }
        
        thread = threading.Thread(target=self._generate_thread, args=(config,))
        thread.daemon = True
        thread.start()
    
    def _generate_thread(self, config: Dict[str, Any]):
        """خيط توليد المشروع"""
        def progress_callback(value: float, status: str, sub_task: str):
            self.after(0, lambda: self.progress_var.set(value))
            self.after(0, lambda: self.status_var.set(status))
        
        tracker = ProgressTracker(progress_callback)
        generator = AndroidProjectGenerator(progress_tracker=tracker)
        result = generator.generate(config)
        
        self.after(0, lambda: self._on_generate_complete(result))
    
    def _on_generate_complete(self, result: Dict[str, Any]):
        """عند اكتمال التوليد"""
        self.is_processing = False
        self.generate_btn.configure(state="normal", text="Generate Android Project")
        
        if result['success']:
            self.progress_var.set(1.0)
            self.status_var.set(f"Success! Project created with {result['files_created']} files")
            
            messagebox.showinfo(
                "Success!",
                f"Android project generated successfully!\n\n"
                f"Location:\n{result['project_path']}\n\n"
                f"Files created: {result['files_created']}\n\n"
                f"Open BUILD_INSTRUCTIONS.txt for next steps."
            )
        else:
            error = result.get('error', {})
            self._show_error(ErrorHandler.format_error(error))
            self.progress_var.set(0)
            self.status_var.set(f"Error: {error.get('message_en', 'Generation failed')}")
    
    def _open_output(self):
        """فتح مجلد الإخراج"""
        path = self.output_path_var.get()
        if os.path.exists(path):
            if sys.platform == 'win32':
                os.startfile(path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
        else:
            self._show_error(f"Output folder does not exist:\n{path}")
    
    def _show_error(self, message: str):
        """عرض رسالة خطأ"""
        messagebox.showerror("Error", message)


# ============================================
# ENTRY POINT
# ============================================

def main():
    """نقطة الدخول الرئيسية"""
    try:
        app = URLToAPKApp()
        app.mainloop()
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Application failed to start:")
        print(f"Error: {str(e)}")
        print(f"\nStack trace:")
        traceback.print_exc()
        print(f"\n[TIP] Try reinstalling dependencies:")
        print(f"      pip install --upgrade customtkinter requests beautifulsoup4 Pillow")
        sys.exit(1)


if __name__ == "__main__":
    main()
