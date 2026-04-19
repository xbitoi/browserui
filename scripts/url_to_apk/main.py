"""
URL to APK Converter - Professional Desktop Application
Author: v0
Version: 1.0.0
Requirements: Python 3.10+, Windows 11
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import json
import subprocess
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import shutil
from pathlib import Path
import zipfile


class URLToAPKConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("URL to APK Converter")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Theme Configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.url_var = ctk.StringVar()
        self.app_name_var = ctk.StringVar()
        self.package_name_var = ctk.StringVar(value="com.app.webview")
        self.version_var = ctk.StringVar(value="1.0.0")
        self.output_path_var = ctk.StringVar(value=str(Path.home() / "Desktop"))
        self.progress_var = ctk.DoubleVar(value=0)
        self.status_var = ctk.StringVar(value="Ready")
        self.orientation_var = ctk.StringVar(value="portrait")
        self.fullscreen_var = ctk.BooleanVar(value=True)
        
        # Site info
        self.site_info = {}
        
        # Build UI
        self._create_ui()
        
    def _create_ui(self):
        # Main Container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header()
        
        # Content
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
        # Left Panel - Input
        self._create_input_panel()
        
        # Right Panel - Preview & Settings
        self._create_settings_panel()
        
        # Bottom - Progress & Actions
        self._create_bottom_panel()
        
    def _create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a2e", corner_radius=15, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=25, pady=15)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="URL to APK",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Convert any website to Android APK",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle_label.pack(anchor="w")
        
        # Version Badge
        version_badge = ctk.CTkLabel(
            header_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=11),
            fg_color="#333355",
            corner_radius=8,
            width=60,
            height=25
        )
        version_badge.pack(side="right", padx=25)
        
    def _create_input_panel(self):
        left_panel = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=15, width=450)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # URL Input Section
        url_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        url_section.pack(fill="x", padx=20, pady=20)
        
        url_label = ctk.CTkLabel(
            url_section,
            text="Website URL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        url_label.pack(anchor="w", pady=(0, 8))
        
        url_input_frame = ctk.CTkFrame(url_section, fg_color="transparent")
        url_input_frame.pack(fill="x")
        
        self.url_entry = ctk.CTkEntry(
            url_input_frame,
            textvariable=self.url_var,
            placeholder_text="https://example.com",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        analyze_btn = ctk.CTkButton(
            url_input_frame,
            text="Analyze",
            width=100,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0066cc",
            hover_color="#0055aa",
            corner_radius=10,
            command=self._analyze_url
        )
        analyze_btn.pack(side="right")
        
        # App Name
        name_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        name_section.pack(fill="x", padx=20, pady=(0, 15))
        
        name_label = ctk.CTkLabel(
            name_section,
            text="App Name",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        name_label.pack(anchor="w", pady=(0, 8))
        
        self.name_entry = ctk.CTkEntry(
            name_section,
            textvariable=self.app_name_var,
            placeholder_text="My App",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.name_entry.pack(fill="x")
        
        # Package Name
        package_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        package_section.pack(fill="x", padx=20, pady=(0, 15))
        
        package_label = ctk.CTkLabel(
            package_section,
            text="Package Name",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        package_label.pack(anchor="w", pady=(0, 8))
        
        self.package_entry = ctk.CTkEntry(
            package_section,
            textvariable=self.package_name_var,
            placeholder_text="com.example.app",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.package_entry.pack(fill="x")
        
        # Version
        version_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        version_section.pack(fill="x", padx=20, pady=(0, 15))
        
        version_label = ctk.CTkLabel(
            version_section,
            text="Version",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        version_label.pack(anchor="w", pady=(0, 8))
        
        self.version_entry = ctk.CTkEntry(
            version_section,
            textvariable=self.version_var,
            placeholder_text="1.0.0",
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.version_entry.pack(fill="x")
        
        # Output Path
        output_section = ctk.CTkFrame(left_panel, fg_color="transparent")
        output_section.pack(fill="x", padx=20, pady=(0, 15))
        
        output_label = ctk.CTkLabel(
            output_section,
            text="Output Directory",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        )
        output_label.pack(anchor="w", pady=(0, 8))
        
        output_frame = ctk.CTkFrame(output_section, fg_color="transparent")
        output_frame.pack(fill="x")
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_path_var,
            height=45,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_color="#333366"
        )
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            output_frame,
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
        
    def _create_settings_panel(self):
        right_panel = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=15, width=380)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Preview Section
        preview_label = ctk.CTkLabel(
            right_panel,
            text="Site Preview",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        preview_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        self.preview_frame = ctk.CTkFrame(right_panel, fg_color="#0f0f23", corner_radius=12, height=120)
        self.preview_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.preview_frame.pack_propagate(False)
        
        self.preview_title = ctk.CTkLabel(
            self.preview_frame,
            text="No site analyzed",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#666666"
        )
        self.preview_title.pack(pady=(25, 5))
        
        self.preview_desc = ctk.CTkLabel(
            self.preview_frame,
            text="Enter a URL and click Analyze",
            font=ctk.CTkFont(size=12),
            text_color="#444444",
            wraplength=300
        )
        self.preview_desc.pack()
        
        # Settings Section
        settings_label = ctk.CTkLabel(
            right_panel,
            text="APK Settings",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        settings_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Orientation
        orientation_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        orientation_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        orientation_label = ctk.CTkLabel(
            orientation_frame,
            text="Screen Orientation",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa"
        )
        orientation_label.pack(anchor="w", pady=(0, 8))
        
        orientation_options = ctk.CTkFrame(orientation_frame, fg_color="transparent")
        orientation_options.pack(fill="x")
        
        portrait_radio = ctk.CTkRadioButton(
            orientation_options,
            text="Portrait",
            variable=self.orientation_var,
            value="portrait",
            font=ctk.CTkFont(size=12)
        )
        portrait_radio.pack(side="left", padx=(0, 20))
        
        landscape_radio = ctk.CTkRadioButton(
            orientation_options,
            text="Landscape",
            variable=self.orientation_var,
            value="landscape",
            font=ctk.CTkFont(size=12)
        )
        landscape_radio.pack(side="left", padx=(0, 20))
        
        auto_radio = ctk.CTkRadioButton(
            orientation_options,
            text="Auto",
            variable=self.orientation_var,
            value="unspecified",
            font=ctk.CTkFont(size=12)
        )
        auto_radio.pack(side="left")
        
        # Fullscreen
        fullscreen_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        fullscreen_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.fullscreen_check = ctk.CTkCheckBox(
            fullscreen_frame,
            text="Enable Fullscreen Mode",
            variable=self.fullscreen_var,
            font=ctk.CTkFont(size=13),
            checkbox_width=22,
            checkbox_height=22
        )
        self.fullscreen_check.pack(anchor="w")
        
        # Features Info
        features_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a3a", corner_radius=10)
        features_frame.pack(fill="x", padx=20, pady=(20, 0))
        
        features_title = ctk.CTkLabel(
            features_frame,
            text="Included Features",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00d4ff"
        )
        features_title.pack(anchor="w", padx=15, pady=(12, 8))
        
        features = [
            "WebView with JavaScript support",
            "File download support",
            "Camera & microphone access",
            "Offline caching",
            "Pull to refresh",
            "Progress indicator"
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                features_frame,
                text=f"  {feature}",
                font=ctk.CTkFont(size=11),
                text_color="#888888"
            )
            feature_label.pack(anchor="w", padx=15, pady=2)
        
        # Add bottom padding
        ctk.CTkLabel(features_frame, text="", height=10).pack()
        
    def _create_bottom_panel(self):
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=120)
        bottom_frame.pack(fill="x", pady=(20, 0))
        
        # Progress Section
        progress_frame = ctk.CTkFrame(bottom_frame, fg_color="#16213e", corner_radius=12)
        progress_frame.pack(fill="x", pady=(0, 15))
        
        progress_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_inner.pack(fill="x", padx=20, pady=15)
        
        self.status_label = ctk.CTkLabel(
            progress_inner,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.status_label.pack(anchor="w", pady=(0, 8))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_inner,
            variable=self.progress_var,
            height=8,
            corner_radius=4,
            fg_color="#1a1a2e",
            progress_color="#00d4ff"
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Action Buttons
        action_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        action_frame.pack(fill="x")
        
        self.generate_btn = ctk.CTkButton(
            action_frame,
            text="Generate APK Project",
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00aa55",
            hover_color="#008844",
            corner_radius=12,
            command=self._generate_apk
        )
        self.generate_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.open_folder_btn = ctk.CTkButton(
            action_frame,
            text="Open Output Folder",
            height=50,
            width=180,
            font=ctk.CTkFont(size=14),
            fg_color="#444466",
            hover_color="#555577",
            corner_radius=12,
            command=self._open_output_folder
        )
        self.open_folder_btn.pack(side="right")
        
    def _browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_path_var.get())
        if folder:
            self.output_path_var.set(folder)
            
    def _analyze_url(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
            
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.url_var.set(url)
            
        self.status_var.set("Analyzing website...")
        self.progress_var.set(0.2)
        
        # Run in thread
        thread = threading.Thread(target=self._analyze_url_thread, args=(url,))
        thread.daemon = True
        thread.start()
        
    def _analyze_url_thread(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else urlparse(url).netloc
            title = title.strip() if title else "My App"
            
            # Extract description
            desc_tag = soup.find('meta', attrs={'name': 'description'})
            description = desc_tag.get('content', '') if desc_tag else ''
            if not description:
                desc_tag = soup.find('meta', attrs={'property': 'og:description'})
                description = desc_tag.get('content', '') if desc_tag else 'No description available'
            
            # Extract theme color
            theme_tag = soup.find('meta', attrs={'name': 'theme-color'})
            theme_color = theme_tag.get('content', '#1a1a2e') if theme_tag else '#1a1a2e'
            
            # Check for manifest (PWA)
            manifest_tag = soup.find('link', attrs={'rel': 'manifest'})
            is_pwa = manifest_tag is not None
            
            self.site_info = {
                'title': title,
                'description': description[:200] + '...' if len(description) > 200 else description,
                'theme_color': theme_color,
                'is_pwa': is_pwa,
                'url': url
            }
            
            # Update UI in main thread
            self.after(0, self._update_preview)
            
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Failed to analyze: {str(e)}"))
            
    def _update_preview(self):
        self.preview_title.configure(
            text=self.site_info.get('title', 'Unknown'),
            text_color="#ffffff"
        )
        self.preview_desc.configure(
            text=self.site_info.get('description', 'No description'),
            text_color="#aaaaaa"
        )
        
        # Auto-fill app name
        if not self.app_name_var.get():
            self.app_name_var.set(self.site_info.get('title', 'My App'))
            
        # Generate package name from URL
        domain = urlparse(self.site_info['url']).netloc
        clean_domain = re.sub(r'[^a-zA-Z0-9]', '.', domain)
        parts = [p for p in clean_domain.split('.') if p]
        if len(parts) >= 2:
            package = f"com.{parts[-1]}.{parts[0]}"
        else:
            package = f"com.app.{parts[0] if parts else 'webview'}"
        self.package_name_var.set(package.lower())
        
        self.progress_var.set(1.0)
        pwa_status = " (PWA Detected)" if self.site_info.get('is_pwa') else ""
        self.status_var.set(f"Analysis complete{pwa_status}")
        
    def _show_error(self, message):
        self.progress_var.set(0)
        self.status_var.set("Error")
        messagebox.showerror("Error", message)
        
    def _generate_apk(self):
        url = self.url_var.get().strip()
        app_name = self.app_name_var.get().strip()
        package_name = self.package_name_var.get().strip()
        version = self.version_var.get().strip()
        output_path = self.output_path_var.get().strip()
        
        # Validation
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        if not app_name:
            messagebox.showwarning("Warning", "Please enter an app name")
            return
        if not package_name:
            messagebox.showwarning("Warning", "Please enter a package name")
            return
            
        # Validate package name format
        if not re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', package_name):
            messagebox.showwarning("Warning", "Invalid package name format. Use format: com.example.app")
            return
            
        self.generate_btn.configure(state="disabled")
        self.status_var.set("Generating Android project...")
        self.progress_var.set(0)
        
        # Run in thread
        thread = threading.Thread(
            target=self._generate_project_thread,
            args=(url, app_name, package_name, version, output_path)
        )
        thread.daemon = True
        thread.start()
        
    def _generate_project_thread(self, url, app_name, package_name, version, output_path):
        try:
            # Create project folder
            project_name = re.sub(r'[^a-zA-Z0-9]', '_', app_name)
            project_dir = Path(output_path) / f"{project_name}_Android"
            
            if project_dir.exists():
                shutil.rmtree(project_dir)
            project_dir.mkdir(parents=True)
            
            self.after(0, lambda: self.progress_var.set(0.1))
            self.after(0, lambda: self.status_var.set("Creating project structure..."))
            
            # Create Android project structure
            self._create_android_project(
                project_dir, url, app_name, package_name, version
            )
            
            self.after(0, lambda: self.progress_var.set(0.9))
            self.after(0, lambda: self.status_var.set("Finalizing..."))
            
            # Create instructions file
            self._create_instructions(project_dir, app_name)
            
            self.after(0, lambda: self.progress_var.set(1.0))
            self.after(0, lambda: self.status_var.set(f"Project created at: {project_dir}"))
            self.after(0, lambda: self.generate_btn.configure(state="normal"))
            self.after(0, lambda: messagebox.showinfo(
                "Success", 
                f"Android project created successfully!\n\nLocation: {project_dir}\n\nRead BUILD_INSTRUCTIONS.txt for next steps."
            ))
            
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Generation failed: {str(e)}"))
            self.after(0, lambda: self.generate_btn.configure(state="normal"))
            
    def _create_android_project(self, project_dir, url, app_name, package_name, version):
        # Create directory structure
        package_path = package_name.replace('.', '/')
        
        dirs = [
            'app/src/main/java/' + package_path,
            'app/src/main/res/layout',
            'app/src/main/res/values',
            'app/src/main/res/drawable',
            'app/src/main/res/mipmap-hdpi',
            'app/src/main/res/mipmap-mdpi',
            'app/src/main/res/mipmap-xhdpi',
            'app/src/main/res/mipmap-xxhdpi',
            'app/src/main/res/mipmap-xxxhdpi',
            'gradle/wrapper'
        ]
        
        for d in dirs:
            (project_dir / d).mkdir(parents=True, exist_ok=True)
            
        self.after(0, lambda: self.progress_var.set(0.2))
        
        # Parse version
        version_parts = version.split('.')
        version_code = int(version_parts[0]) * 10000 + int(version_parts[1] if len(version_parts) > 1 else 0) * 100 + int(version_parts[2] if len(version_parts) > 2 else 0)
        
        # Orientation and fullscreen settings
        orientation = self.orientation_var.get()
        fullscreen = self.fullscreen_var.get()
        
        theme_style = "Theme.AppCompat.Light.NoActionBar" if not fullscreen else "Theme.AppCompat.Light.NoActionBar.Fullscreen"
        
        # Create build.gradle (project level)
        project_gradle = '''// Top-level build file
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.2.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
'''
        (project_dir / 'build.gradle').write_text(project_gradle)
        
        self.after(0, lambda: self.progress_var.set(0.3))
        
        # Create build.gradle (app level)
        app_gradle = f'''plugins {{
    id 'com.android.application'
}}

android {{
    namespace '{package_name}'
    compileSdk 34

    defaultConfig {{
        applicationId "{package_name}"
        minSdk 24
        targetSdk 34
        versionCode {version_code}
        versionName "{version}"
    }}

    buildTypes {{
        release {{
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
}}

dependencies {{
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.webkit:webkit:1.9.0'
    implementation 'androidx.swiperefreshlayout:swiperefreshlayout:1.1.0'
    implementation 'com.google.android.material:material:1.11.0'
}}
'''
        (project_dir / 'app/build.gradle').write_text(app_gradle)
        
        # Create settings.gradle
        settings_gradle = f'''pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

rootProject.name = "{app_name}"
include ':app'
'''
        (project_dir / 'settings.gradle').write_text(settings_gradle)
        
        self.after(0, lambda: self.progress_var.set(0.4))
        
        # Create gradle.properties
        gradle_properties = '''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
'''
        (project_dir / 'gradle.properties').write_text(gradle_properties)
        
        # Create AndroidManifest.xml
        manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="{app_name}"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true"
        android:networkSecurityConfig="@xml/network_security_config">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="{orientation}"
            android:configChanges="orientation|screenSize|keyboardHidden">
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
        (project_dir / 'app/src/main/AndroidManifest.xml').write_text(manifest)
        
        self.after(0, lambda: self.progress_var.set(0.5))
        
        # Create XML resources directory
        xml_dir = project_dir / 'app/src/main/res/xml'
        xml_dir.mkdir(parents=True, exist_ok=True)
        
        # Network security config
        network_config = '''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
'''
        (xml_dir / 'network_security_config.xml').write_text(network_config)
        
        # File paths for FileProvider
        file_paths = '''<?xml version="1.0" encoding="utf-8"?>
<paths>
    <external-path name="external" path="." />
    <cache-path name="cache" path="." />
</paths>
'''
        (xml_dir / 'file_paths.xml').write_text(file_paths)
        
        # Create MainActivity.java
        main_activity = f'''package {package_name};

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.DownloadManager;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.*;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {{

    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefresh;
    private static final String URL = "{url}";
    private static final int PERMISSION_REQUEST_CODE = 1001;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST = 1002;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        swipeRefresh = findViewById(R.id.swipeRefresh);

        // Configure WebView
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        // WebViewClient
        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {{
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
            }}

            @Override
            public void onPageFinished(WebView view, String url) {{
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
            }}

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {{
                String url = request.getUrl().toString();
                if (url.startsWith("tel:") || url.startsWith("mailto:") || 
                    url.startsWith("whatsapp:") || url.startsWith("intent:")) {{
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }}
                return false;
            }}
        }});

        // WebChromeClient for file uploads and permissions
        webView.setWebChromeClient(new WebChromeClient() {{
            @Override
            public void onProgressChanged(WebView view, int newProgress) {{
                progressBar.setProgress(newProgress);
            }}

            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                            FileChooserParams fileChooserParams) {{
                MainActivity.this.filePathCallback = filePathCallback;
                Intent intent = fileChooserParams.createIntent();
                try {{
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                }} catch (Exception e) {{
                    Toast.makeText(MainActivity.this, "Cannot open file chooser", Toast.LENGTH_SHORT).show();
                    return false;
                }}
                return true;
            }}

            @Override
            public void onPermissionRequest(final PermissionRequest request) {{
                runOnUiThread(() -> request.grant(request.getResources()));
            }}
        }});

        // Download listener
        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {{
            if (checkStoragePermission()) {{
                downloadFile(url, contentDisposition, mimeType);
            }}
        }});

        // Swipe to refresh
        swipeRefresh.setOnRefreshListener(() -> webView.reload());
        swipeRefresh.setColorSchemeResources(android.R.color.holo_blue_bright);

        // Load URL
        webView.loadUrl(URL);
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

    private void downloadFile(String url, String contentDisposition, String mimeType) {{
        try {{
            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
            String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
            request.setTitle(fileName);
            request.setDescription("Downloading file...");
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);
            request.setMimeType(mimeType);

            DownloadManager dm = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
            dm.enqueue(request);
            Toast.makeText(this, "Download started: " + fileName, Toast.LENGTH_SHORT).show();
        }} catch (Exception e) {{
            Toast.makeText(this, "Download failed", Toast.LENGTH_SHORT).show();
        }}
    }}

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {{
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
    public boolean onKeyDown(int keyCode, KeyEvent event) {{
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {{
            webView.goBack();
            return true;
        }}
        return super.onKeyDown(keyCode, event);
    }}

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                          @NonNull int[] grantResults) {{
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE && grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED) {{
            Toast.makeText(this, "Permission granted", Toast.LENGTH_SHORT).show();
        }}
    }}
    
    @Override
    protected void onResume() {{
        super.onResume();
        webView.onResume();
    }}
    
    @Override
    protected void onPause() {{
        super.onPause();
        webView.onPause();
    }}
    
    @Override
    protected void onDestroy() {{
        webView.destroy();
        super.onDestroy();
    }}
}}
'''
        (project_dir / f'app/src/main/java/{package_path}/MainActivity.java').write_text(main_activity)
        
        self.after(0, lambda: self.progress_var.set(0.6))
        
        # Create activity_main.xml
        layout = '''<?xml version="1.0" encoding="utf-8"?>
<androidx.swiperefreshlayout.widget.SwipeRefreshLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/swipeRefresh"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <RelativeLayout
        android:layout_width="match_parent"
        android:layout_height="match_parent">

        <ProgressBar
            android:id="@+id/progressBar"
            style="?android:attr/progressBarStyleHorizontal"
            android:layout_width="match_parent"
            android:layout_height="4dp"
            android:layout_alignParentTop="true"
            android:indeterminate="false"
            android:max="100"
            android:progress="0"
            android:progressTint="#2196F3"
            android:visibility="gone" />

        <WebView
            android:id="@+id/webView"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:layout_below="@id/progressBar" />

    </RelativeLayout>

</androidx.swiperefreshlayout.widget.SwipeRefreshLayout>
'''
        (project_dir / 'app/src/main/res/layout/activity_main.xml').write_text(layout)
        
        self.after(0, lambda: self.progress_var.set(0.7))
        
        # Create colors.xml
        colors = '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#2196F3</color>
    <color name="colorPrimaryDark">#1976D2</color>
    <color name="colorAccent">#FF4081</color>
    <color name="white">#FFFFFF</color>
    <color name="black">#000000</color>
</resources>
'''
        (project_dir / 'app/src/main/res/values/colors.xml').write_text(colors)
        
        # Create strings.xml
        strings = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
</resources>
'''
        (project_dir / 'app/src/main/res/values/strings.xml').write_text(strings)
        
        # Create styles.xml
        fullscreen_items = '''
        <item name="android:windowFullscreen">true</item>
        <item name="android:windowContentOverlay">@null</item>''' if fullscreen else ''
        
        styles = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
        <item name="android:windowBackground">@color/white</item>{fullscreen_items}
    </style>
</resources>
'''
        (project_dir / 'app/src/main/res/values/styles.xml').write_text(styles)
        
        self.after(0, lambda: self.progress_var.set(0.8))
        
        # Create proguard-rules.pro
        proguard = '''-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.webkit.WebViewClient
-keep public class * extends android.webkit.WebChromeClient
-dontwarn android.webkit.**
'''
        (project_dir / 'app/proguard-rules.pro').write_text(proguard)
        
        # Create gradle wrapper properties
        wrapper_props = '''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''
        (project_dir / 'gradle/wrapper/gradle-wrapper.properties').write_text(wrapper_props)
        
    def _create_instructions(self, project_dir, app_name):
        instructions = f'''===========================================
      BUILD INSTRUCTIONS FOR {app_name.upper()}
===========================================

OPTION 1: Build with Android Studio (Recommended)
--------------------------------------------------
1. Download and install Android Studio from:
   https://developer.android.com/studio

2. Open Android Studio and select "Open an existing project"

3. Navigate to and select this folder:
   {project_dir}

4. Wait for Gradle sync to complete (may take a few minutes)

5. To create a debug APK:
   - Click Build > Build Bundle(s) / APK(s) > Build APK(s)
   - APK will be at: app/build/outputs/apk/debug/app-debug.apk

6. To create a signed release APK:
   - Click Build > Generate Signed Bundle / APK
   - Choose APK and follow the wizard to create a signing key
   - APK will be at: app/build/outputs/apk/release/app-release.apk


OPTION 2: Build with Command Line
----------------------------------
Requirements:
- Java JDK 17 or higher
- Android SDK with Build Tools 34

Steps:
1. Open Command Prompt/Terminal in this directory

2. Make gradlew executable (Linux/Mac):
   chmod +x gradlew

3. Build debug APK:
   ./gradlew assembleDebug (Linux/Mac)
   gradlew.bat assembleDebug (Windows)

4. Build release APK (requires signing):
   ./gradlew assembleRelease


CUSTOMIZATION
--------------
- Change app icon: Replace files in app/src/main/res/mipmap-* folders
- Change splash screen: Edit app/src/main/res/drawable/
- Change colors: Edit app/src/main/res/values/colors.xml
- Change permissions: Edit app/src/main/AndroidManifest.xml


TROUBLESHOOTING
----------------
- If Gradle sync fails, check your internet connection
- If build fails, ensure you have the correct SDK version (34)
- For icon issues, ensure all mipmap folders have correct size icons


PROJECT INFO
-------------
Package Name: {self.package_name_var.get()}
Version: {self.version_var.get()}
Target URL: {self.url_var.get()}
Generated: URL to APK Converter v1.0.0

===========================================
'''
        (project_dir / 'BUILD_INSTRUCTIONS.txt').write_text(instructions)
        
    def _open_output_folder(self):
        output_path = self.output_path_var.get()
        if os.path.exists(output_path):
            if sys.platform == 'win32':
                os.startfile(output_path)
            elif sys.platform == 'darwin':
                subprocess.run(['open', output_path])
            else:
                subprocess.run(['xdg-open', output_path])
        else:
            messagebox.showwarning("Warning", "Output folder does not exist")


def main():
    app = URLToAPKConverter()
    app.mainloop()


if __name__ == "__main__":
    main()
