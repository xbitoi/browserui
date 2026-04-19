"""
Test script to verify URL analysis works correctly
Tests with: https://browserui-gilt.vercel.app
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import json

def analyze_url(url):
    """Analyze a URL and extract app information"""
    print(f"\n{'='*60}")
    print(f"  Testing URL Analysis")
    print(f"{'='*60}")
    print(f"\nURL: {url}")
    print("-" * 60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print("\n[1] Fetching website...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"    Status: {response.status_code} OK")
        print(f"    Content Length: {len(response.text)} bytes")
        
        print("\n[2] Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        print("\n[3] Extracting metadata...")
        title = soup.title.string if soup.title else urlparse(url).netloc
        title = title.strip() if title else "My App"
        print(f"    Title: {title}")
        
        # Extract description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '') if desc_tag else ''
        if not description:
            desc_tag = soup.find('meta', attrs={'property': 'og:description'})
            description = desc_tag.get('content', '') if desc_tag else 'No description available'
        print(f"    Description: {description[:100]}..." if len(description) > 100 else f"    Description: {description}")
        
        # Extract theme color
        theme_tag = soup.find('meta', attrs={'name': 'theme-color'})
        theme_color = theme_tag.get('content', '#1a1a2e') if theme_tag else '#1a1a2e'
        print(f"    Theme Color: {theme_color}")
        
        # Check for manifest (PWA)
        manifest_tag = soup.find('link', attrs={'rel': 'manifest'})
        is_pwa = manifest_tag is not None
        print(f"    PWA Support: {'Yes' if is_pwa else 'No'}")
        
        # Extract icons
        icon_links = soup.find_all('link', attrs={'rel': re.compile(r'icon', re.I)})
        icons = [link.get('href', '') for link in icon_links if link.get('href')]
        print(f"    Icons Found: {len(icons)}")
        for icon in icons[:3]:
            print(f"      - {icon}")
        
        # Generate package name
        domain = urlparse(url).netloc
        clean_domain = re.sub(r'[^a-zA-Z0-9]', '.', domain)
        parts = [p for p in clean_domain.split('.') if p]
        if len(parts) >= 2:
            package = f"com.{parts[-1]}.{parts[0]}"
        else:
            package = f"com.app.{parts[0] if parts else 'webview'}"
        
        print(f"\n[4] Generated values:")
        print(f"    App Name: {title}")
        print(f"    Package Name: {package.lower()}")
        print(f"    Version: 1.0.0")
        
        # Check for viewport
        viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
        viewport = viewport_tag.get('content', '') if viewport_tag else ''
        print(f"    Mobile Optimized: {'Yes' if viewport else 'No'}")
        
        # Check for service worker registration
        scripts = soup.find_all('script')
        has_sw = any('serviceWorker' in str(script) for script in scripts)
        print(f"    Service Worker: {'Detected' if has_sw else 'Not detected'}")
        
        print(f"\n{'='*60}")
        print("  ANALYSIS COMPLETE - READY FOR APK GENERATION")
        print(f"{'='*60}")
        
        return {
            'success': True,
            'title': title,
            'description': description,
            'theme_color': theme_color,
            'is_pwa': is_pwa,
            'package_name': package.lower(),
            'icons': icons,
            'mobile_optimized': bool(viewport)
        }
        
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to {url}")
        print("    Check your internet connection")
        return {'success': False, 'error': 'Connection failed'}
        
    except requests.exceptions.Timeout:
        print(f"\n[ERROR] Request timed out")
        return {'success': False, 'error': 'Timeout'}
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    # Test with the provided URL
    test_url = "https://browserui-gilt.vercel.app"
    result = analyze_url(test_url)
    
    print("\n\nJSON Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
