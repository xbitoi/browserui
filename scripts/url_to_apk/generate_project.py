"""
Generate Android Project from URL - Command Line Version
Tests the project generation with: https://browserui-gilt.vercel.app
"""

import os
import re
import shutil
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def analyze_url(url):
    """Analyze URL and return site info"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.title.string.strip() if soup.title and soup.title.string else urlparse(url).netloc
    
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if not desc_tag:
        desc_tag = soup.find('meta', attrs={'property': 'og:description'})
    description = desc_tag.get('content', '') if desc_tag else ''
    
    theme_tag = soup.find('meta', attrs={'name': 'theme-color'})
    theme_color = theme_tag.get('content', '#2196F3') if theme_tag else '#2196F3'
    
    return {
        'title': title,
        'description': description,
        'theme_color': theme_color,
        'url': url
    }

def generate_android_project(url, output_dir, app_name=None, package_name=None, version="1.0.0"):
    """Generate a complete Android project"""
    
    print(f"\n{'='*60}")
    print("  Android Project Generator")
    print(f"{'='*60}")
    
    # Analyze URL
    print(f"\n[1/5] Analyzing URL: {url}")
    info = analyze_url(url)
    print(f"      Title: {info['title']}")
    
    # Set defaults
    if not app_name:
        app_name = info['title']
    
    if not package_name:
        domain = urlparse(url).netloc
        clean = re.sub(r'[^a-zA-Z0-9]', '.', domain)
        parts = [p for p in clean.split('.') if p]
        package_name = f"com.{parts[-1]}.{parts[0]}".lower() if len(parts) >= 2 else f"com.app.{parts[0]}".lower()
    
    project_name = re.sub(r'[^a-zA-Z0-9]', '_', app_name)
    project_dir = Path(output_dir) / f"{project_name}_Android"
    
    print(f"\n[2/5] Creating project structure...")
    print(f"      Project: {project_dir}")
    
    if project_dir.exists():
        shutil.rmtree(project_dir)
    
    # Create directories
    package_path = package_name.replace('.', '/')
    dirs = [
        'app/src/main/java/' + package_path,
        'app/src/main/res/layout',
        'app/src/main/res/values',
        'app/src/main/res/drawable',
        'app/src/main/res/xml',
        'app/src/main/res/mipmap-hdpi',
        'app/src/main/res/mipmap-mdpi',
        'app/src/main/res/mipmap-xhdpi',
        'app/src/main/res/mipmap-xxhdpi',
        'app/src/main/res/mipmap-xxxhdpi',
        'gradle/wrapper'
    ]
    
    for d in dirs:
        (project_dir / d).mkdir(parents=True, exist_ok=True)
    
    print(f"      Directories created: {len(dirs)}")
    
    # Parse version
    vp = version.split('.')
    version_code = int(vp[0]) * 10000 + int(vp[1] if len(vp) > 1 else 0) * 100 + int(vp[2] if len(vp) > 2 else 0)
    
    print(f"\n[3/5] Generating Gradle files...")
    
    # Project build.gradle
    (project_dir / 'build.gradle').write_text('''buildscript {
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
''')
    
    # App build.gradle
    (project_dir / 'app/build.gradle').write_text(f'''plugins {{
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
''')

    # Settings gradle
    (project_dir / 'settings.gradle').write_text(f'''pluginManagement {{
    repositories {{
        google()
        mavenCentral()
        gradlePluginPortal()
    }}
}}

rootProject.name = "{app_name}"
include ':app'
''')

    # gradle.properties
    (project_dir / 'gradle.properties').write_text('''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
''')

    # Gradle wrapper
    (project_dir / 'gradle/wrapper/gradle-wrapper.properties').write_text('''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
''')

    print(f"\n[4/5] Generating Android source files...")
    
    # AndroidManifest.xml
    (project_dir / 'app/src/main/AndroidManifest.xml').write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />

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
            android:screenOrientation="portrait"
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
''')

    # Network security config
    (project_dir / 'app/src/main/res/xml/network_security_config.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
''')

    # File paths
    (project_dir / 'app/src/main/res/xml/file_paths.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<paths>
    <external-path name="external" path="." />
    <cache-path name="cache" path="." />
</paths>
''')

    # MainActivity.java
    (project_dir / f'app/src/main/java/{package_path}/MainActivity.java').write_text(f'''package {package_name};

import android.annotation.SuppressLint;
import android.app.DownloadManager;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.*;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {{

    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefresh;
    private static final String URL = "{url}";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        swipeRefresh = findViewById(R.id.swipeRefresh);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setAllowFileAccess(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {{
                progressBar.setVisibility(View.VISIBLE);
            }}

            @Override
            public void onPageFinished(WebView view, String url) {{
                progressBar.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
            }}

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {{
                String requestUrl = request.getUrl().toString();
                if (requestUrl.startsWith("tel:") || requestUrl.startsWith("mailto:") || 
                    requestUrl.startsWith("whatsapp:") || requestUrl.startsWith("intent:")) {{
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(requestUrl));
                    startActivity(intent);
                    return true;
                }}
                return false;
            }}
        }});

        webView.setWebChromeClient(new WebChromeClient() {{
            @Override
            public void onProgressChanged(WebView view, int newProgress) {{
                progressBar.setProgress(newProgress);
            }}

            @Override
            public void onPermissionRequest(final PermissionRequest request) {{
                runOnUiThread(() -> request.grant(request.getResources()));
            }}
        }});

        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {{
            try {{
                DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
                request.setTitle(fileName);
                request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);
                DownloadManager dm = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
                dm.enqueue(request);
                Toast.makeText(this, "Downloading: " + fileName, Toast.LENGTH_SHORT).show();
            }} catch (Exception e) {{
                Toast.makeText(this, "Download failed", Toast.LENGTH_SHORT).show();
            }}
        }});

        swipeRefresh.setOnRefreshListener(() -> webView.reload());
        swipeRefresh.setColorSchemeResources(android.R.color.holo_blue_bright);

        webView.loadUrl(URL);
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
''')

    # Layout
    (project_dir / 'app/src/main/res/layout/activity_main.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
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
''')

    # Resources
    (project_dir / 'app/src/main/res/values/colors.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#2196F3</color>
    <color name="colorPrimaryDark">#1976D2</color>
    <color name="colorAccent">#FF4081</color>
    <color name="white">#FFFFFF</color>
</resources>
''')

    (project_dir / 'app/src/main/res/values/strings.xml').write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{app_name}</string>
</resources>
''')

    (project_dir / 'app/src/main/res/values/styles.xml').write_text('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
        <item name="android:windowBackground">@color/white</item>
        <item name="android:windowFullscreen">true</item>
    </style>
</resources>
''')

    # Proguard
    (project_dir / 'app/proguard-rules.pro').write_text('''-keepattributes *Annotation*
-keep public class * extends android.app.Activity
-keep public class * extends android.webkit.WebViewClient
-dontwarn android.webkit.**
''')

    print(f"\n[5/5] Generating instructions...")
    
    (project_dir / 'BUILD_INSTRUCTIONS.txt').write_text(f'''
================================================================================
                    BUILD INSTRUCTIONS - {app_name}
================================================================================

PROJECT DETAILS
---------------
App Name: {app_name}
Package: {package_name}
Version: {version}
URL: {url}

BUILD WITH ANDROID STUDIO (Recommended)
---------------------------------------
1. Download Android Studio: https://developer.android.com/studio
2. Open this project folder in Android Studio
3. Wait for Gradle sync to complete
4. Click Build > Build Bundle(s) / APK(s) > Build APK(s)
5. APK location: app/build/outputs/apk/debug/app-debug.apk

COMMAND LINE BUILD
------------------
Prerequisites: Java JDK 17, Android SDK 34

Windows:
  gradlew.bat assembleDebug

Linux/Mac:
  chmod +x gradlew
  ./gradlew assembleDebug

================================================================================
''')

    print(f"\n{'='*60}")
    print("  PROJECT GENERATED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"\n  Location: {project_dir}")
    print(f"  App Name: {app_name}")
    print(f"  Package:  {package_name}")
    print(f"  Version:  {version}")
    print(f"\n  Next Steps:")
    print(f"  1. Open the project in Android Studio")
    print(f"  2. Wait for Gradle sync")
    print(f"  3. Build > Build APK")
    print(f"\n{'='*60}\n")
    
    return str(project_dir)


if __name__ == "__main__":
    # Test with provided URL
    url = "https://browserui-gilt.vercel.app"
    output = "/vercel/share/v0-project/scripts/url_to_apk/output"
    
    project_path = generate_android_project(
        url=url,
        output_dir=output,
        app_name="BrowserUI",
        version="1.0.0"
    )
    
    # List generated files
    print("\nGenerated files:")
    for root, dirs, files in os.walk(project_path):
        level = root.replace(project_path, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = '  ' * (level + 1)
        for file in files[:5]:  # Limit files shown
            print(f"{subindent}{file}")
        if len(files) > 5:
            print(f"{subindent}... and {len(files) - 5} more files")
