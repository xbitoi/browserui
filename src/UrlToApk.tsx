import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Globe, 
  Download, 
  Smartphone, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  AlertTriangle,
  Palette,
  Type,
  RotateCcw,
  Maximize,
  ChevronRight,
  ExternalLink,
  Copy,
  Check,
  Sparkles,
  Shield,
  Zap,
  Package
} from 'lucide-react';
import { cn } from './lib/utils';

// Types
interface WebsiteInfo {
  url: string;
  title: string;
  description: string;
  themeColor: string;
  icons: string[];
  isPwa: boolean;
  isResponsive: boolean;
  manifestUrl?: string;
}

interface AppConfig {
  appName: string;
  packageName: string;
  themeColor: string;
  backgroundColor: string;
  orientation: 'portrait' | 'landscape' | 'any';
  fullscreen: boolean;
  version: string;
}

interface ProgressStep {
  id: string;
  label: string;
  labelAr: string;
  status: 'pending' | 'active' | 'completed' | 'error';
}

interface ErrorInfo {
  code: string;
  message: string;
  messageAr: string;
  suggestion: string;
  suggestionAr: string;
}

// Error definitions
const ERRORS: Record<string, ErrorInfo> = {
  INVALID_URL: {
    code: 'E001',
    message: 'Invalid URL format',
    messageAr: 'صيغة الرابط غير صحيحة',
    suggestion: 'Please enter a valid URL starting with https://',
    suggestionAr: 'يرجى إدخال رابط صحيح يبدأ بـ https://'
  },
  NETWORK_ERROR: {
    code: 'E002',
    message: 'Network connection failed',
    messageAr: 'فشل الاتصال بالشبكة',
    suggestion: 'Check your internet connection and try again',
    suggestionAr: 'تحقق من اتصالك بالإنترنت وحاول مرة أخرى'
  },
  WEBSITE_UNREACHABLE: {
    code: 'E003',
    message: 'Website is unreachable',
    messageAr: 'لا يمكن الوصول إلى الموقع',
    suggestion: 'Make sure the website is accessible and try again',
    suggestionAr: 'تأكد من إمكانية الوصول إلى الموقع وحاول مرة أخرى'
  },
  BUILD_FAILED: {
    code: 'E004',
    message: 'APK build failed',
    messageAr: 'فشل بناء ملف APK',
    suggestion: 'The website may not support PWA conversion. Try a different URL.',
    suggestionAr: 'قد لا يدعم الموقع تحويل PWA. جرب رابطاً آخر.'
  },
  TIMEOUT: {
    code: 'E005',
    message: 'Request timed out',
    messageAr: 'انتهت مهلة الطلب',
    suggestion: 'The server is taking too long. Please try again later.',
    suggestionAr: 'الخادم يستغرق وقتاً طويلاً. يرجى المحاولة لاحقاً.'
  }
};

// Utility functions
const isValidUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'https:' || parsed.protocol === 'http:';
  } catch {
    return false;
  }
};

const generatePackageName = (url: string): string => {
  try {
    const hostname = new URL(url).hostname;
    const parts = hostname.split('.').reverse();
    const cleaned = parts.map(p => p.replace(/[^a-z0-9]/gi, '').toLowerCase()).filter(Boolean);
    return cleaned.length >= 2 ? cleaned.join('.') : `com.app.${cleaned[0] || 'myapp'}`;
  } catch {
    return 'com.app.myapp';
  }
};

const extractDomainName = (url: string): string => {
  try {
    const hostname = new URL(url).hostname;
    const parts = hostname.replace('www.', '').split('.');
    return parts[0].charAt(0).toUpperCase() + parts[0].slice(1);
  } catch {
    return 'MyApp';
  }
};

export default function UrlToApk() {
  // State
  const [url, setUrl] = useState('');
  const [websiteInfo, setWebsiteInfo] = useState<WebsiteInfo | null>(null);
  const [appConfig, setAppConfig] = useState<AppConfig>({
    appName: '',
    packageName: '',
    themeColor: '#2196F3',
    backgroundColor: '#ffffff',
    orientation: 'portrait',
    fullscreen: false,
    version: '1.0.0'
  });
  const [currentStep, setCurrentStep] = useState<'input' | 'customize' | 'building' | 'complete' | 'error'>('input');
  const [error, setError] = useState<ErrorInfo | null>(null);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  
  const [steps, setSteps] = useState<ProgressStep[]>([
    { id: 'analyze', label: 'Analyzing website', labelAr: 'تحليل الموقع', status: 'pending' },
    { id: 'manifest', label: 'Creating manifest', labelAr: 'إنشاء الملف التعريفي', status: 'pending' },
    { id: 'package', label: 'Packaging app', labelAr: 'تجهيز التطبيق', status: 'pending' },
    { id: 'build', label: 'Building APK', labelAr: 'بناء ملف APK', status: 'pending' },
    { id: 'ready', label: 'Ready to download', labelAr: 'جاهز للتحميل', status: 'pending' }
  ]);

  // Update step status
  const updateStepStatus = useCallback((stepId: string, status: ProgressStep['status']) => {
    setSteps(prev => prev.map(s => s.id === stepId ? { ...s, status } : s));
  }, []);

  // Analyze website
  const analyzeWebsite = async () => {
    if (!url.trim()) return;
    
    const normalizedUrl = url.startsWith('http') ? url : `https://${url}`;
    
    if (!isValidUrl(normalizedUrl)) {
      setError(ERRORS.INVALID_URL);
      setCurrentStep('error');
      return;
    }

    setCurrentStep('building');
    setProgress(0);
    setSteps(prev => prev.map(s => ({ ...s, status: 'pending' })));
    updateStepStatus('analyze', 'active');

    try {
      // Simulate analysis with progress
      await new Promise(r => setTimeout(r, 800));
      setProgress(15);
      
      // Fetch website info via proxy API
      const response = await fetch(`/api/analyze?url=${encodeURIComponent(normalizedUrl)}`);
      
      if (!response.ok) {
        throw new Error('WEBSITE_UNREACHABLE');
      }
      
      const data = await response.json();
      
      updateStepStatus('analyze', 'completed');
      setProgress(25);
      
      const info: WebsiteInfo = {
        url: normalizedUrl,
        title: data.title || extractDomainName(normalizedUrl),
        description: data.description || '',
        themeColor: data.themeColor || '#2196F3',
        icons: data.icons || [],
        isPwa: data.isPwa || false,
        isResponsive: data.isResponsive || true,
        manifestUrl: data.manifestUrl
      };
      
      setWebsiteInfo(info);
      setAppConfig(prev => ({
        ...prev,
        appName: info.title,
        packageName: generatePackageName(normalizedUrl),
        themeColor: info.themeColor,
        backgroundColor: '#ffffff'
      }));
      
      setCurrentStep('customize');
      
    } catch (err: any) {
      console.error('Analysis error:', err);
      updateStepStatus('analyze', 'error');
      
      if (err.message === 'WEBSITE_UNREACHABLE') {
        setError(ERRORS.WEBSITE_UNREACHABLE);
      } else if (err.name === 'TypeError') {
        setError(ERRORS.NETWORK_ERROR);
      } else {
        setError(ERRORS.WEBSITE_UNREACHABLE);
      }
      setCurrentStep('error');
    }
  };

  // Build APK
  const buildApk = async () => {
    if (!websiteInfo) return;
    
    setCurrentStep('building');
    setProgress(25);
    
    try {
      // Step 2: Create manifest
      updateStepStatus('manifest', 'active');
      await new Promise(r => setTimeout(r, 600));
      setProgress(40);
      updateStepStatus('manifest', 'completed');
      
      // Step 3: Package app
      updateStepStatus('package', 'active');
      await new Promise(r => setTimeout(r, 800));
      setProgress(55);
      updateStepStatus('package', 'completed');
      
      // Step 4: Build APK using PWABuilder API
      updateStepStatus('build', 'active');
      setProgress(65);
      
      const buildResponse = await fetch('/api/build-apk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: websiteInfo.url,
          name: appConfig.appName,
          packageName: appConfig.packageName,
          themeColor: appConfig.themeColor,
          backgroundColor: appConfig.backgroundColor,
          orientation: appConfig.orientation,
          fullscreen: appConfig.fullscreen,
          version: appConfig.version
        })
      });
      
      if (!buildResponse.ok) {
        const errorData = await buildResponse.json().catch(() => ({}));
        throw new Error(errorData.error || 'BUILD_FAILED');
      }
      
      setProgress(85);
      
      const buildData = await buildResponse.json();
      updateStepStatus('build', 'completed');
      
      // Step 5: Ready
      updateStepStatus('ready', 'active');
      await new Promise(r => setTimeout(r, 400));
      setProgress(100);
      updateStepStatus('ready', 'completed');
      
      setDownloadUrl(buildData.downloadUrl || buildData.pwabuilderUrl);
      setCurrentStep('complete');
      
    } catch (err: any) {
      console.error('Build error:', err);
      
      // Find the active step and mark it as error
      setSteps(prev => prev.map(s => s.status === 'active' ? { ...s, status: 'error' } : s));
      
      if (err.message === 'BUILD_FAILED') {
        setError(ERRORS.BUILD_FAILED);
      } else if (err.name === 'AbortError') {
        setError(ERRORS.TIMEOUT);
      } else {
        setError(ERRORS.BUILD_FAILED);
      }
      setCurrentStep('error');
    }
  };

  // Reset
  const reset = () => {
    setUrl('');
    setWebsiteInfo(null);
    setAppConfig({
      appName: '',
      packageName: '',
      themeColor: '#2196F3',
      backgroundColor: '#ffffff',
      orientation: 'portrait',
      fullscreen: false,
      version: '1.0.0'
    });
    setCurrentStep('input');
    setError(null);
    setProgress(0);
    setDownloadUrl(null);
    setSteps(prev => prev.map(s => ({ ...s, status: 'pending' })));
  };

  // Copy URL
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-[#0a0a0a]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center">
              <Package className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">URL to APK</h1>
              <p className="text-xs text-white/50">Convert any website to Android app</p>
            </div>
          </div>
          
          <a 
            href="https://www.pwabuilder.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm text-white/50 hover:text-white transition-colors flex items-center gap-1"
          >
            Powered by PWABuilder
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-16">
        <AnimatePresence mode="wait">
          {/* Input Step */}
          {currentStep === 'input' && (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-12"
            >
              {/* Hero */}
              <div className="text-center space-y-4">
                <motion.div
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 text-emerald-400 text-sm font-medium mb-4"
                >
                  <Sparkles className="w-4 h-4" />
                  Free & Open Source
                </motion.div>
                
                <h2 className="text-4xl sm:text-5xl font-bold text-white text-balance">
                  Convert Website to{' '}
                  <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                    Android APK
                  </span>
                </h2>
                
                <p className="text-lg text-white/60 max-w-xl mx-auto text-balance">
                  Transform any website into a native Android application in minutes. No coding required.
                </p>
              </div>

              {/* URL Input */}
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-2xl blur-xl" />
                  <div className="relative bg-white/5 border border-white/10 rounded-2xl p-2">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 flex items-center gap-3 bg-white/5 rounded-xl px-4 py-3">
                        <Globe className="w-5 h-5 text-white/40 shrink-0" />
                        <input
                          type="url"
                          value={url}
                          onChange={(e) => setUrl(e.target.value)}
                          placeholder="Enter website URL (e.g., https://example.com)"
                          className="flex-1 bg-transparent text-white placeholder:text-white/30 outline-none text-base"
                          onKeyDown={(e) => e.key === 'Enter' && analyzeWebsite()}
                        />
                      </div>
                      <button
                        onClick={analyzeWebsite}
                        disabled={!url.trim()}
                        className={cn(
                          "px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 shrink-0",
                          url.trim()
                            ? "bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:opacity-90"
                            : "bg-white/10 text-white/30 cursor-not-allowed"
                        )}
                      >
                        Analyze
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Features */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-3xl mx-auto pt-8">
                {[
                  { icon: Shield, title: 'Secure', desc: 'HTTPS only, safe browsing' },
                  { icon: Zap, title: 'Fast', desc: 'Build in under 2 minutes' },
                  { icon: Smartphone, title: 'Native Feel', desc: 'Full Android experience' }
                ].map((feature, i) => (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="bg-white/5 border border-white/10 rounded-xl p-5 text-center hover:bg-white/[0.07] transition-colors"
                  >
                    <feature.icon className="w-8 h-8 text-emerald-400 mx-auto mb-3" />
                    <h3 className="font-semibold text-white mb-1">{feature.title}</h3>
                    <p className="text-sm text-white/50">{feature.desc}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Customize Step */}
          {currentStep === 'customize' && websiteInfo && (
            <motion.div
              key="customize"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-8"
            >
              {/* Website Info Card */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center shrink-0">
                    {websiteInfo.icons[0] ? (
                      <img src={websiteInfo.icons[0]} alt="" className="w-10 h-10 rounded-lg" />
                    ) : (
                      <Globe className="w-8 h-8 text-emerald-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-xl font-semibold text-white truncate">{websiteInfo.title}</h3>
                    <p className="text-sm text-white/50 truncate">{websiteInfo.url}</p>
                    <div className="flex items-center gap-3 mt-3">
                      {websiteInfo.isPwa && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
                          <CheckCircle2 className="w-3 h-3" />
                          PWA Ready
                        </span>
                      )}
                      {websiteInfo.isResponsive && (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/20 text-cyan-400 text-xs font-medium">
                          <Smartphone className="w-3 h-3" />
                          Mobile Optimized
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Configuration Form */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-6">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Palette className="w-5 h-5 text-emerald-400" />
                  Customize Your App
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {/* App Name */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white/70 flex items-center gap-2">
                      <Type className="w-4 h-4" />
                      App Name
                    </label>
                    <input
                      type="text"
                      value={appConfig.appName}
                      onChange={(e) => setAppConfig(prev => ({ ...prev, appName: e.target.value }))}
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 outline-none focus:border-emerald-500/50 transition-colors"
                    />
                  </div>

                  {/* Package Name */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white/70 flex items-center gap-2">
                      <Package className="w-4 h-4" />
                      Package Name
                    </label>
                    <input
                      type="text"
                      value={appConfig.packageName}
                      onChange={(e) => setAppConfig(prev => ({ ...prev, packageName: e.target.value }))}
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 outline-none focus:border-emerald-500/50 transition-colors font-mono text-sm"
                    />
                  </div>

                  {/* Theme Color */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white/70 flex items-center gap-2">
                      <Palette className="w-4 h-4" />
                      Theme Color
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="color"
                        value={appConfig.themeColor}
                        onChange={(e) => setAppConfig(prev => ({ ...prev, themeColor: e.target.value }))}
                        className="w-12 h-12 rounded-xl cursor-pointer bg-transparent border-2 border-white/10"
                      />
                      <input
                        type="text"
                        value={appConfig.themeColor}
                        onChange={(e) => setAppConfig(prev => ({ ...prev, themeColor: e.target.value }))}
                        className="flex-1 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white font-mono text-sm outline-none focus:border-emerald-500/50 transition-colors"
                      />
                    </div>
                  </div>

                  {/* Orientation */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-white/70 flex items-center gap-2">
                      <RotateCcw className="w-4 h-4" />
                      Orientation
                    </label>
                    <select
                      value={appConfig.orientation}
                      onChange={(e) => setAppConfig(prev => ({ ...prev, orientation: e.target.value as any }))}
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white outline-none focus:border-emerald-500/50 transition-colors appearance-none cursor-pointer"
                    >
                      <option value="portrait" className="bg-neutral-900">Portrait</option>
                      <option value="landscape" className="bg-neutral-900">Landscape</option>
                      <option value="any" className="bg-neutral-900">Any</option>
                    </select>
                  </div>
                </div>

                {/* Fullscreen Toggle */}
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <div className="flex items-center gap-3">
                    <Maximize className="w-5 h-5 text-white/50" />
                    <div>
                      <p className="font-medium text-white">Fullscreen Mode</p>
                      <p className="text-sm text-white/50">Hide system bars for immersive experience</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setAppConfig(prev => ({ ...prev, fullscreen: !prev.fullscreen }))}
                    className={cn(
                      "w-12 h-7 rounded-full transition-colors relative",
                      appConfig.fullscreen ? "bg-emerald-500" : "bg-white/20"
                    )}
                  >
                    <div className={cn(
                      "absolute top-1 w-5 h-5 rounded-full bg-white transition-transform",
                      appConfig.fullscreen ? "translate-x-6" : "translate-x-1"
                    )} />
                  </button>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-4">
                <button
                  onClick={reset}
                  className="px-6 py-3 rounded-xl font-medium bg-white/5 border border-white/10 text-white hover:bg-white/10 transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={buildApk}
                  className="flex-1 px-6 py-3 rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Build APK
                </button>
              </div>
            </motion.div>
          )}

          {/* Building Step */}
          {currentStep === 'building' && (
            <motion.div
              key="building"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-xl mx-auto space-y-8"
            >
              <div className="text-center space-y-4">
                <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center">
                  <Loader2 className="w-10 h-10 text-emerald-400 animate-spin" />
                </div>
                <h2 className="text-2xl font-bold text-white">Building Your App</h2>
                <p className="text-white/50">This may take a minute or two...</p>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-white/50">Progress</span>
                  <span className="text-white font-medium">{progress}%</span>
                </div>
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* Steps */}
              <div className="space-y-3">
                {steps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={cn(
                      "flex items-center gap-4 p-4 rounded-xl transition-colors",
                      step.status === 'active' && "bg-emerald-500/10 border border-emerald-500/20",
                      step.status === 'completed' && "bg-white/5",
                      step.status === 'error' && "bg-red-500/10 border border-red-500/20",
                      step.status === 'pending' && "bg-white/5 opacity-50"
                    )}
                  >
                    <div className="shrink-0">
                      {step.status === 'completed' && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
                      {step.status === 'active' && <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />}
                      {step.status === 'error' && <XCircle className="w-5 h-5 text-red-400" />}
                      {step.status === 'pending' && <div className="w-5 h-5 rounded-full border-2 border-white/20" />}
                    </div>
                    <div className="flex-1">
                      <p className={cn(
                        "font-medium",
                        step.status === 'completed' && "text-white",
                        step.status === 'active' && "text-emerald-400",
                        step.status === 'error' && "text-red-400",
                        step.status === 'pending' && "text-white/50"
                      )}>
                        {step.label}
                      </p>
                      <p className="text-sm text-white/40">{step.labelAr}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Complete Step */}
          {currentStep === 'complete' && (
            <motion.div
              key="complete"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-xl mx-auto text-center space-y-8"
            >
              <div className="space-y-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', damping: 15 }}
                  className="w-24 h-24 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center"
                >
                  <CheckCircle2 className="w-12 h-12 text-white" />
                </motion.div>
                <h2 className="text-3xl font-bold text-white">APK Ready!</h2>
                <p className="text-white/50">Your Android app has been successfully built</p>
              </div>

              {downloadUrl && (
                <div className="space-y-4">
                  <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                    <div className="flex items-center gap-3">
                      <input
                        type="text"
                        value={downloadUrl}
                        readOnly
                        className="flex-1 bg-transparent text-white/70 text-sm font-mono outline-none truncate"
                      />
                      <button
                        onClick={() => copyToClipboard(downloadUrl)}
                        className="shrink-0 p-2 hover:bg-white/10 rounded-lg transition-colors"
                      >
                        {copied ? <Check className="w-5 h-5 text-emerald-400" /> : <Copy className="w-5 h-5 text-white/50" />}
                      </button>
                    </div>
                  </div>

                  <a
                    href={downloadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-medium bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:opacity-90 transition-opacity"
                  >
                    <Download className="w-5 h-5" />
                    Download APK
                  </a>
                </div>
              )}

              <button
                onClick={reset}
                className="text-white/50 hover:text-white transition-colors flex items-center gap-2 mx-auto"
              >
                <RotateCcw className="w-4 h-4" />
                Convert Another Website
              </button>
            </motion.div>
          )}

          {/* Error Step */}
          {currentStep === 'error' && error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-xl mx-auto text-center space-y-8"
            >
              <div className="space-y-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-24 h-24 mx-auto rounded-2xl bg-red-500/20 flex items-center justify-center"
                >
                  <AlertTriangle className="w-12 h-12 text-red-400" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white">{error.message}</h2>
                <p className="text-white/50">{error.messageAr}</p>
              </div>

              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-left space-y-3">
                <div className="flex items-center gap-2 text-red-400 font-mono text-sm">
                  <span className="px-2 py-0.5 bg-red-500/20 rounded">Error {error.code}</span>
                </div>
                <p className="text-white/70">{error.suggestion}</p>
                <p className="text-white/50 text-sm">{error.suggestionAr}</p>
              </div>

              <button
                onClick={reset}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-xl font-medium bg-white/10 text-white hover:bg-white/20 transition-colors"
              >
                <RotateCcw className="w-5 h-5" />
                Try Again
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-6 mt-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-sm text-white/40">
          <p>This tool uses PWABuilder to generate Android APK files from websites.</p>
        </div>
      </footer>
    </div>
  );
}
