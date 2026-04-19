import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  const { url } = req.query;

  if (!url || typeof url !== 'string') {
    return res.status(400).json({ 
      error: 'URL is required',
      errorAr: 'الرابط مطلوب'
    });
  }

  try {
    // Validate URL
    const parsedUrl = new URL(url);
    
    // Fetch the website
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);

    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
      },
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (!response.ok) {
      return res.status(400).json({ 
        error: 'Website is not accessible',
        errorAr: 'لا يمكن الوصول إلى الموقع'
      });
    }

    const html = await response.text();

    // Extract metadata
    const titleMatch = html.match(/<title[^>]*>([^<]+)<\/title>/i);
    const title = titleMatch ? titleMatch[1].trim() : parsedUrl.hostname;

    const descriptionMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']+)["']/i) ||
                            html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*name=["']description["']/i) ||
                            html.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']+)["']/i);
    const description = descriptionMatch ? descriptionMatch[1].trim() : '';

    const themeColorMatch = html.match(/<meta[^>]*name=["']theme-color["'][^>]*content=["']([^"']+)["']/i) ||
                           html.match(/<meta[^>]*content=["']([^"']+)["'][^>]*name=["']theme-color["']/i);
    const themeColor = themeColorMatch ? themeColorMatch[1].trim() : '#2196F3';

    // Check for manifest (PWA)
    const manifestMatch = html.match(/<link[^>]*rel=["']manifest["'][^>]*href=["']([^"']+)["']/i) ||
                         html.match(/<link[^>]*href=["']([^"']+)["'][^>]*rel=["']manifest["']/i);
    const manifestUrl = manifestMatch ? new URL(manifestMatch[1], url).href : null;
    const isPwa = !!manifestUrl;

    // Check for viewport (responsive)
    const viewportMatch = html.match(/<meta[^>]*name=["']viewport["']/i);
    const isResponsive = !!viewportMatch;

    // Extract icons
    const icons: string[] = [];
    
    // Apple touch icon
    const appleTouchMatch = html.match(/<link[^>]*rel=["']apple-touch-icon["'][^>]*href=["']([^"']+)["']/i);
    if (appleTouchMatch) {
      icons.push(new URL(appleTouchMatch[1], url).href);
    }

    // Standard icon
    const iconMatch = html.match(/<link[^>]*rel=["']icon["'][^>]*href=["']([^"']+)["']/i) ||
                     html.match(/<link[^>]*href=["']([^"']+)["'][^>]*rel=["']icon["']/i);
    if (iconMatch) {
      icons.push(new URL(iconMatch[1], url).href);
    }

    // Favicon
    const faviconMatch = html.match(/<link[^>]*rel=["']shortcut icon["'][^>]*href=["']([^"']+)["']/i);
    if (faviconMatch) {
      icons.push(new URL(faviconMatch[1], url).href);
    }

    // OG Image as fallback
    const ogImageMatch = html.match(/<meta[^>]*property=["']og:image["'][^>]*content=["']([^"']+)["']/i);
    if (ogImageMatch && icons.length === 0) {
      icons.push(new URL(ogImageMatch[1], url).href);
    }

    return res.status(200).json({
      url,
      title,
      description,
      themeColor,
      icons: [...new Set(icons)], // Remove duplicates
      isPwa,
      isResponsive,
      manifestUrl
    });

  } catch (error: any) {
    console.error('Analysis error:', error);
    
    if (error.name === 'AbortError') {
      return res.status(408).json({ 
        error: 'Request timed out',
        errorAr: 'انتهت مهلة الطلب'
      });
    }

    return res.status(500).json({ 
      error: 'Failed to analyze website',
      errorAr: 'فشل تحليل الموقع',
      details: error.message
    });
  }
}
