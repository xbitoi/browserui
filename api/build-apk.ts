import type { VercelRequest, VercelResponse } from '@vercel/node';

interface BuildRequest {
  url: string;
  name: string;
  packageName: string;
  themeColor: string;
  backgroundColor: string;
  orientation: 'portrait' | 'landscape' | 'any';
  fullscreen: boolean;
  version: string;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const body: BuildRequest = req.body;

    if (!body.url || !body.name || !body.packageName) {
      return res.status(400).json({
        error: 'Missing required fields: url, name, packageName',
        errorAr: 'حقول مطلوبة مفقودة: url, name, packageName'
      });
    }

    // Validate URL
    try {
      new URL(body.url);
    } catch {
      return res.status(400).json({
        error: 'Invalid URL format',
        errorAr: 'صيغة الرابط غير صحيحة'
      });
    }

    // Validate package name
    const packageNameRegex = /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/i;
    if (!packageNameRegex.test(body.packageName)) {
      return res.status(400).json({
        error: 'Invalid package name format. Use format like: com.example.app',
        errorAr: 'صيغة اسم الحزمة غير صحيحة. استخدم صيغة مثل: com.example.app'
      });
    }

    // Create PWA manifest for PWABuilder
    const manifest = {
      name: body.name,
      short_name: body.name.substring(0, 12),
      description: `${body.name} - Android App`,
      start_url: body.url,
      scope: body.url,
      display: body.fullscreen ? 'fullscreen' : 'standalone',
      orientation: body.orientation,
      theme_color: body.themeColor,
      background_color: body.backgroundColor,
      icons: [
        {
          src: `https://www.google.com/s2/favicons?domain=${new URL(body.url).hostname}&sz=512`,
          sizes: '512x512',
          type: 'image/png',
          purpose: 'any maskable'
        }
      ]
    };

    // PWABuilder API endpoint
    // Note: PWABuilder has a web interface that generates APKs
    // We'll provide the PWABuilder URL with pre-filled parameters
    
    const pwabuilderUrl = `https://www.pwabuilder.com/reportcard?site=${encodeURIComponent(body.url)}`;

    // For direct APK generation, we would use Bubblewrap or PWABuilder's API
    // Since PWABuilder's direct API requires authentication, we provide the web URL
    
    // Alternative: Use CloudAPK service (if available)
    // const cloudApkUrl = `https://appmaker.xyz/pwa-to-apk/?url=${encodeURIComponent(body.url)}`;

    // Return the PWABuilder URL for the user to download the APK
    return res.status(200).json({
      success: true,
      message: 'APK build request processed',
      messageAr: 'تم معالجة طلب بناء APK',
      pwabuilderUrl,
      downloadUrl: pwabuilderUrl,
      manifest,
      instructions: {
        en: [
          '1. Click the download link to open PWABuilder',
          '2. Wait for the analysis to complete',
          '3. Click "Package for stores"',
          '4. Select "Android" and click "Generate"',
          '5. Download your APK file'
        ],
        ar: [
          '1. انقر على رابط التحميل لفتح PWABuilder',
          '2. انتظر اكتمال التحليل',
          '3. انقر على "Package for stores"',
          '4. اختر "Android" وانقر "Generate"',
          '5. حمّل ملف APK الخاص بك'
        ]
      },
      config: {
        appName: body.name,
        packageName: body.packageName,
        version: body.version,
        themeColor: body.themeColor,
        backgroundColor: body.backgroundColor,
        orientation: body.orientation,
        fullscreen: body.fullscreen
      }
    });

  } catch (error: any) {
    console.error('Build error:', error);
    
    return res.status(500).json({
      error: 'Failed to process build request',
      errorAr: 'فشل معالجة طلب البناء',
      details: error.message
    });
  }
}
