import React, { useState, useEffect, useRef } from 'react';
import { db } from './firebase';
import { doc, onSnapshot, setDoc, collection, addDoc, getDocs, query, orderBy, limit, deleteDoc, getDoc, updateDoc, increment } from 'firebase/firestore';
import { Settings, Lock, Globe, Power, Users, Key, Palette, MessageSquare, Trash2, ChevronLeft, ShieldAlert, Database, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './lib/utils';
import { Pool } from '@neondatabase/serverless';

// Default settings if none exist
const DEFAULT_SETTINGS = {
  url: 'https://example.com',
  isActive: true,
  settingsPassword: 'admin',
  welcomeMessage: 'مرحباً بك في تطبيقنا',
  welcomeMessageDuration: 5,
  themeColor: '#3b82f6', // blue-500
  databaseUrl: 'postgresql://neondb_owner:npg_90bOimpSEhvo@ep-soft-thunder-amezsr4d-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require',
  firebaseKey: '',
  databaseType: 'postgresql' as 'postgresql' | 'firebase',
  marqueeDirection: 'rtl' as 'rtl' | 'ltr',
  isWelcomePermanent: false,
  broadcastMessage: { text: '', id: 0, isActive: false },
  messageHistory: [] as Array<{ id: number, text: string, date: string }>
};

export default function App() {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [isLoading, setIsLoading] = useState(true);
  const [view, setView] = useState<'main' | 'login' | 'settings'>('main');
  const hasLoggedVisitor = useRef(false);

  // Fetch Settings
  useEffect(() => {
    const settingsRef = doc(db, 'settings', 'main');
    const unsubscribe = onSnapshot(settingsRef, (docSnap) => {
      if (docSnap.exists()) {
        setSettings(docSnap.data() as typeof DEFAULT_SETTINGS);
      } else {
        // Initialize default settings
        setDoc(settingsRef, DEFAULT_SETTINGS);
      }
      setIsLoading(false);
    }, (error) => {
      console.error("Error fetching settings:", error);
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Log Visitor
  useEffect(() => {
    if (hasLoggedVisitor.current) return;
    
    const logVisitor = async () => {
      try {
        hasLoggedVisitor.current = true;
        
        // Generate a device ID based on user agent and platform to group same devices
        const generateDeviceId = (ua: string, platform: string) => {
          const str = `${ua}-${platform}`;
          let hash = 0;
          for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
          }
          return 'device_' + Math.abs(hash).toString(36);
        };
        
        const deviceId = generateDeviceId(navigator.userAgent, navigator.platform);

        const visitorRef = doc(db, 'visitors', deviceId);
        const visitorSnap = await getDoc(visitorRef);

        if (visitorSnap.exists()) {
          await updateDoc(visitorRef, {
            visitedAt: new Date().toISOString(),
            visitCount: increment(1)
          });
        } else {
          await setDoc(visitorRef, {
            visitedAt: new Date().toISOString(),
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            visitCount: 1
          });
        }
      } catch (error) {
        console.error("Failed to log visitor:", error);
      }
    };

    logVisitor();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50" dir="rtl">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 font-sans" dir="rtl" style={{ '--theme-color': settings.themeColor } as React.CSSProperties}>
      <AnimatePresence mode="wait">
        {view === 'main' && (
          <MainView 
            key="main" 
            settings={settings} 
            onOpenSettings={() => setView('login')} 
          />
        )}
        {view === 'login' && (
          <LoginView 
            key="login" 
            correctPassword={settings.settingsPassword} 
            onSuccess={() => setView('settings')} 
            onCancel={() => setView('main')} 
          />
        )}
        {view === 'settings' && (
          <SettingsView 
            key="settings" 
            settings={settings} 
            onClose={() => setView('main')} 
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function MainView({ settings, onOpenSettings }: { key?: React.Key, settings: typeof DEFAULT_SETTINGS, onOpenSettings: () => void }) {
  const [showWelcome, setShowWelcome] = useState(true);
  const [popup, setPopup] = useState({ show: false, text: '', id: 0 });
  const gestureRef = useRef({ startX: 0, lastX: 0, lastDirection: 0, swipeCount: 0, completed: false, isSwiping: false });

  const handleBannerTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      gestureRef.current = {
        startX: e.touches[0].clientX,
        lastX: e.touches[0].clientX,
        lastDirection: 0,
        swipeCount: 0,
        completed: false,
        isSwiping: false
      };
    }
  };

  const handleBannerTouchMove = (e: React.TouchEvent) => {
    if (e.touches.length !== 1 || gestureRef.current.completed) return;
    
    const currentX = e.touches[0].clientX;
    const deltaX = currentX - gestureRef.current.startX;

    if (Math.abs(currentX - gestureRef.current.lastX) > 10) {
      gestureRef.current.isSwiping = true;
    }

    if (Math.abs(deltaX) > 40) {
      const currentDirection = Math.sign(deltaX);
      
      if (gestureRef.current.lastDirection !== 0 && currentDirection !== gestureRef.current.lastDirection) {
        gestureRef.current.swipeCount++;
        gestureRef.current.startX = currentX;
      } else if (gestureRef.current.lastDirection === 0) {
        gestureRef.current.lastDirection = currentDirection;
        gestureRef.current.startX = currentX;
      }
      
      gestureRef.current.lastDirection = currentDirection;

      if (gestureRef.current.swipeCount >= 5) {
        gestureRef.current.completed = true;
        onOpenSettings();
      }
    }
    gestureRef.current.lastX = currentX;
  };

  const handleBannerClick = () => {
    if (!gestureRef.current.isSwiping) {
      setShowWelcome(false);
    }
  };

  useEffect(() => {
    if (settings.welcomeMessage && (settings.welcomeMessageDuration > 0 || settings.isWelcomePermanent)) {
      setShowWelcome(true);
      if (!settings.isWelcomePermanent) {
        const timer = setTimeout(() => setShowWelcome(false), settings.welcomeMessageDuration * 1000);
        return () => clearTimeout(timer);
      }
    } else {
      setShowWelcome(false);
    }
  }, [settings.welcomeMessage, settings.welcomeMessageDuration, settings.isWelcomePermanent]);

  useEffect(() => {
    if (settings.broadcastMessage?.isActive && settings.broadcastMessage?.text) {
      const seenId = localStorage.getItem('seenMessageId');
      if (seenId !== String(settings.broadcastMessage.id)) {
        setPopup({ show: true, text: settings.broadcastMessage.text, id: settings.broadcastMessage.id });
      }
    } else {
      setPopup(prev => ({ ...prev, show: false }));
    }
  }, [settings.broadcastMessage?.id, settings.broadcastMessage?.isActive, settings.broadcastMessage?.text]);

  if (!settings.isActive) {
    return (
      <motion.div 
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-6"
      >
        <ShieldAlert className="w-24 h-24 text-red-500 mb-6" />
        <h1 className="text-3xl font-bold mb-4 text-center">التطبيق متوقف حالياً</h1>
        <p className="text-gray-400 text-center max-w-md">
          عذراً، التطبيق غير متاح في الوقت الحالي. يرجى المحاولة في وقت لاحق.
        </p>
        <button 
          onClick={onOpenSettings}
          className="absolute top-6 left-6 p-3 rounded-full bg-gray-800 hover:bg-gray-700 transition-colors opacity-50 hover:opacity-100"
        >
          <Settings className="w-6 h-6" />
        </button>
      </motion.div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      className="h-screen w-full relative overflow-hidden flex flex-col"
    >
      {/* Header Bar (Only for Welcome Message) */}
      <AnimatePresence initial={false}>
        {showWelcome && (
          <motion.div 
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 64, opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-full flex items-center justify-between px-4 shadow-md z-20 text-white overflow-hidden shrink-0 cursor-pointer"
            style={{ backgroundColor: settings.themeColor }}
            onClick={handleBannerClick}
            onTouchStart={handleBannerTouchStart}
            onTouchMove={handleBannerTouchMove}
          >
            <div className="flex-1 overflow-hidden relative flex items-center h-full pointer-events-none">
              {settings.welcomeMessage.length > 40 ? (
                <div className={cn("whitespace-nowrap font-bold text-lg", settings.marqueeDirection === 'ltr' ? 'animate-marquee-ltr' : 'animate-marquee-rtl')}>
                  {settings.welcomeMessage}
                </div>
              ) : (
                <div className="font-bold text-lg w-full flex items-center justify-center">
                  <motion.span initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="truncate">
                    {settings.welcomeMessage}
                  </motion.span>
                </div>
              )}
            </div>
            
            <button 
              onClick={(e) => { e.stopPropagation(); onOpenSettings(); }}
              className="p-2 rounded-full hover:bg-black/20 transition-colors z-50 mr-2 shrink-0"
              title="الإعدادات"
            >
              <Settings className="w-5 h-5" />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content (Iframe) */}
      <div className="flex-1 bg-white relative w-full">
        {settings.url ? (
          <iframe 
            src={settings.url} 
            className="w-full h-full border-none"
            title="App Content"
            sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400 flex-col">
            <Globe className="w-16 h-16 mb-4 opacity-50" />
            <p>لم يتم تعيين رابط بعد</p>
          </div>
        )}
      </div>

      {/* Popup Message Modal */}
      <AnimatePresence>
        {popup.show && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }}
              className="bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full text-center"
            >
              <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">رسالة إدارية</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">{popup.text}</p>
              <button 
                onClick={() => {
                  localStorage.setItem('seenMessageId', String(popup.id));
                  setPopup({ ...popup, show: false });
                }}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
              >
                إغلاق
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function LoginView({ correctPassword, onSuccess, onCancel }: { key?: React.Key, correctPassword: string, onSuccess: () => void, onCancel: () => void }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === correctPassword) {
      onSuccess();
    } else {
      setError(true);
      setTimeout(() => setError(false), 2000);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}
      className="min-h-screen flex items-center justify-center p-4 bg-gray-100"
    >
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md relative overflow-hidden">
        <button 
          onClick={onCancel}
          className="absolute top-4 left-4 p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        
        <div className="flex justify-center mb-6">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-600">
            <Lock className="w-8 h-8" />
          </div>
        </div>
        
        <h2 className="text-2xl font-bold text-center mb-8">تسجيل الدخول للإعدادات</h2>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">كلمة المرور</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={cn(
                "w-full px-4 py-3 rounded-xl border focus:ring-2 focus:outline-none transition-all",
                error ? "border-red-500 focus:ring-red-200" : "border-gray-300 focus:border-blue-500 focus:ring-blue-200"
              )}
              placeholder="أدخل كلمة المرور..."
              autoFocus
            />
            {error && <p className="text-red-500 text-sm mt-2">كلمة المرور غير صحيحة</p>}
          </div>
          
          <button 
            type="submit"
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors shadow-md hover:shadow-lg"
          >
            دخول
          </button>
        </form>
      </div>
    </motion.div>
  );
}

function SettingsView({ settings, onClose }: { key?: React.Key, settings: typeof DEFAULT_SETTINGS, onClose: () => void }) {
  const [localSettings, setLocalSettings] = useState(settings);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [dbTestStatus, setDbTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [firebaseTestStatus, setFirebaseTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'general' | 'messages' | 'visitors'>('general');
  const [visitors, setVisitors] = useState<any[]>([]);
  const [isLoadingVisitors, setIsLoadingVisitors] = useState(false);
  const [messageText, setMessageText] = useState('');

  useEffect(() => {
    if (activeTab === 'visitors') {
      loadVisitors();
    }
  }, [activeTab]);

  const loadVisitors = async () => {
    setIsLoadingVisitors(true);
    try {
      const q = query(collection(db, 'visitors'), orderBy('visitedAt', 'desc'), limit(100));
      const querySnapshot = await getDocs(q);
      
      // Group visitors by userAgent + platform to merge old duplicates
      const groupedVisitors = new Map();
      
      querySnapshot.docs.forEach(doc => {
        const data = doc.data();
        const key = `${data.userAgent}-${data.platform}`;
        
        if (groupedVisitors.has(key)) {
          const existing = groupedVisitors.get(key);
          existing.visitCount = (existing.visitCount || 1) + (data.visitCount || 1);
          if (new Date(data.visitedAt) > new Date(existing.visitedAt)) {
            existing.visitedAt = data.visitedAt;
          }
        } else {
          groupedVisitors.set(key, { id: doc.id, ...data, visitCount: data.visitCount || 1 });
        }
      });
      
      const v = Array.from(groupedVisitors.values())
        .sort((a, b) => new Date(b.visitedAt).getTime() - new Date(a.visitedAt).getTime())
        .slice(0, 50); // Keep top 50 after grouping
        
      setVisitors(v);
    } catch (error) {
      console.error("Error loading visitors:", error);
    }
    setIsLoadingVisitors(false);
  };

  const clearVisitors = async () => {
    try {
      const q = query(collection(db, 'visitors'), limit(100));
      const querySnapshot = await getDocs(q);
      const deletePromises = querySnapshot.docs.map(d => deleteDoc(doc(db, 'visitors', d.id)));
      await Promise.all(deletePromises);
      loadVisitors();
      setShowClearConfirm(false);
    } catch (error) {
      console.error("Error clearing visitors:", error);
    }
  };

  const handleSave = async () => {
    setSaveStatus('saving');
    try {
      await setDoc(doc(db, 'settings', 'main'), localSettings);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error("Error saving settings:", error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const testDbConnection = async () => {
    if (!localSettings.databaseUrl) return;
    setDbTestStatus('testing');
    try {
      const pool = new Pool({ connectionString: localSettings.databaseUrl });
      await pool.query('SELECT 1');
      await pool.end();
      setDbTestStatus('success');
    } catch (error) {
      console.error("DB Test Error:", error);
      setDbTestStatus('error');
    }
  };

  const testFirebaseConnection = async () => {
    if (!localSettings.firebaseKey) return;
    setFirebaseTestStatus('testing');
    try {
      const res = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${localSettings.firebaseKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (data.error && data.error.message === 'API_KEY_INVALID') {
        setFirebaseTestStatus('error');
      } else {
        setFirebaseTestStatus('success');
      }
    } catch (error) {
      console.error("Firebase Test Error:", error);
      setFirebaseTestStatus('error');
    }
  };

  const handleSendMessage = async () => {
    if (!messageText.trim()) return;
    setSaveStatus('saving');
    try {
      const newMessage = { text: messageText, id: Date.now(), isActive: true };
      const historyItem = { id: newMessage.id, text: newMessage.text, date: new Date().toISOString() };
      const updatedHistory = [historyItem, ...(localSettings.messageHistory || [])].slice(0, 50); // Keep last 50
      
      const updatedSettings = { 
        ...localSettings, 
        broadcastMessage: newMessage,
        messageHistory: updatedHistory
      };
      
      await setDoc(doc(db, 'settings', 'main'), updatedSettings);
      setLocalSettings(updatedSettings);
      setMessageText('');
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error("Error sending message:", error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const toggleMessageActive = async (isActive: boolean) => {
    setSaveStatus('saving');
    try {
      const updatedSettings = { 
        ...localSettings, 
        broadcastMessage: { ...localSettings.broadcastMessage, isActive } 
      };
      await setDoc(doc(db, 'settings', 'main'), updatedSettings);
      setLocalSettings(updatedSettings);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error("Error toggling message:", error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  const deleteMessageFromHistory = async (msgId: number) => {
    setSaveStatus('saving');
    try {
      const updatedHistory = localSettings.messageHistory.filter((m: any) => m.id !== msgId);
      const updatedSettings = { ...localSettings, messageHistory: updatedHistory };
      await setDoc(doc(db, 'settings', 'main'), updatedSettings);
      setLocalSettings(updatedSettings);
      setSaveStatus('success');
      setConfirmDeleteId(null);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error("Error deleting message:", error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 20 }}
      className="min-h-screen bg-gray-50 flex flex-col"
    >
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
            <ChevronLeft className="w-6 h-6 text-gray-600" />
          </button>
          <h1 className="text-xl font-bold text-gray-800">لوحة التحكم</h1>
        </div>
        <div className="flex items-center gap-4">
          <AnimatePresence>
            {saveStatus === 'success' && (
              <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} className="text-green-600 font-medium text-sm">
                تم الحفظ بنجاح ✓
              </motion.span>
            )}
            {saveStatus === 'error' && (
              <motion.span initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} className="text-red-600 font-medium text-sm">
                حدث خطأ أثناء الحفظ ✕
              </motion.span>
            )}
          </AnimatePresence>
          <button 
            onClick={handleSave}
            disabled={saveStatus === 'saving'}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {saveStatus === 'saving' ? 'جاري الحفظ...' : 'حفظ التغييرات'}
          </button>
        </div>
      </div>

      <div className="flex-1 max-w-5xl w-full mx-auto p-6 flex flex-col md:flex-row gap-6">
        {/* Sidebar */}
        <div className="w-full md:w-64 space-y-2">
          <button 
            onClick={() => setActiveTab('general')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors",
              activeTab === 'general' ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-100"
            )}
          >
            <Settings className="w-5 h-5" />
            إعدادات عامة
          </button>
          <button 
            onClick={() => setActiveTab('messages')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors",
              activeTab === 'messages' ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-100"
            )}
          >
            <MessageSquare className="w-5 h-5" />
            إرسال رسالة
          </button>
          <button 
            onClick={() => setActiveTab('visitors')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors",
              activeTab === 'visitors' ? "bg-blue-50 text-blue-700" : "text-gray-600 hover:bg-gray-100"
            )}
          >
            <Users className="w-5 h-5" />
            سجل الزوار
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 bg-white rounded-2xl shadow-sm border p-6">
          {activeTab === 'general' && (
            <div className="space-y-8">
              {/* App Status */}
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border">
                <div>
                  <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                    <Power className="w-5 h-5 text-gray-500" />
                    حالة التطبيق
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">إيقاف أو تشغيل التطبيق لجميع المستخدمين</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    className="sr-only peer"
                    checked={localSettings.isActive}
                    onChange={(e) => setLocalSettings({...localSettings, isActive: e.target.checked})}
                  />
                  <div className="w-14 h-7 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-green-500"></div>
                </label>
              </div>

              {/* URL Settings */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2 border-b pb-2">
                  <Globe className="w-5 h-5 text-gray-500" />
                  رابط التطبيق
                </h3>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">الرابط (URL)</label>
                  <input 
                    type="url" 
                    value={localSettings.url}
                    onChange={(e) => setLocalSettings({...localSettings, url: e.target.value})}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                    placeholder="https://..."
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Appearance */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2 border-b pb-2">
                  <Palette className="w-5 h-5 text-gray-500" />
                  المظهر والترحيب
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">رسالة الترحيب</label>
                    <input 
                      type="text" 
                      value={localSettings.welcomeMessage}
                      onChange={(e) => setLocalSettings({...localSettings, welcomeMessage: e.target.value})}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                      placeholder="اتركها فارغة لإلغاء الرسالة"
                    />
                  </div>
                  <div className="flex flex-col justify-center">
                    <label className="flex items-center gap-2 cursor-pointer mt-6">
                      <input 
                        type="checkbox" 
                        checked={localSettings.isWelcomePermanent || false}
                        onChange={(e) => setLocalSettings({...localSettings, isWelcomePermanent: e.target.checked})}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-800 font-medium">ظهور دائم للشريط (لا يختفي تلقائياً)</span>
                    </label>
                  </div>
                  <div className={localSettings.isWelcomePermanent ? "opacity-50 pointer-events-none" : ""}>
                    <label className="block text-sm text-gray-600 mb-1">مدة ظهور الرسالة (بالثواني)</label>
                    <input 
                      type="number" 
                      min="1"
                      max="60"
                      value={localSettings.welcomeMessageDuration || 5}
                      onChange={(e) => setLocalSettings({...localSettings, welcomeMessageDuration: parseInt(e.target.value) || 5})}
                      className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                      disabled={localSettings.isWelcomePermanent}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">لون الواجهة الرئيسي</label>
                    <div className="flex items-center gap-3">
                      <input 
                        type="color" 
                        value={localSettings.themeColor}
                        onChange={(e) => setLocalSettings({...localSettings, themeColor: e.target.value})}
                        className="w-10 h-10 rounded cursor-pointer border-0 p-0"
                      />
                      <span className="text-sm text-gray-500 font-mono" dir="ltr">{localSettings.themeColor}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Security */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2 border-b pb-2">
                  <Key className="w-5 h-5 text-gray-500" />
                  الأمان
                </h3>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">كلمة سر الإعدادات</label>
                  <input 
                    type="text" 
                    value={localSettings.settingsPassword}
                    onChange={(e) => setLocalSettings({...localSettings, settingsPassword: e.target.value})}
                    className="w-full max-w-md px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                  />
                  <p className="text-xs text-gray-500 mt-2">ملاحظة: هذه الكلمة تستخدم للدخول إلى هذه اللوحة.</p>
                </div>
              </div>

              {/* Database */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2 border-b pb-2">
                  <Database className="w-5 h-5 text-gray-500" />
                  قاعدة البيانات
                </h3>

                <div>
                  <label className="block text-sm text-gray-600 mb-2">نوع قاعدة البيانات</label>
                  <div className="flex gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        name="databaseType"
                        value="postgresql"
                        checked={localSettings.databaseType !== 'firebase'}
                        onChange={() => setLocalSettings({...localSettings, databaseType: 'postgresql'})}
                        className="text-blue-600 focus:ring-blue-500 w-4 h-4"
                      />
                      <span className="text-sm text-gray-800">PostgreSQL</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        name="databaseType"
                        value="firebase"
                        checked={localSettings.databaseType === 'firebase'}
                        onChange={() => setLocalSettings({...localSettings, databaseType: 'firebase'})}
                        className="text-blue-600 focus:ring-blue-500 w-4 h-4"
                      />
                      <span className="text-sm text-gray-800">Firebase</span>
                    </label>
                  </div>
                </div>

                {localSettings.databaseType !== 'firebase' ? (
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">رابط الاتصال (Connection String)</label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <input 
                          type="text" 
                          value={localSettings.databaseUrl || ''}
                          onChange={(e) => {
                            setLocalSettings({...localSettings, databaseUrl: e.target.value});
                            setDbTestStatus('idle');
                          }}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none font-mono text-sm"
                          placeholder="postgresql://user:password@host/dbname"
                          dir="ltr"
                        />
                      </div>
                      <button
                        onClick={testDbConnection}
                        disabled={dbTestStatus === 'testing' || !localSettings.databaseUrl}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
                      >
                        {dbTestStatus === 'testing' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'فحص الاتصال'}
                      </button>
                    </div>
                    
                    <AnimatePresence>
                      {dbTestStatus === 'success' && (
                        <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} className="mt-2 flex items-center gap-1.5 text-green-600 text-sm font-medium">
                          <CheckCircle2 className="w-4 h-4" />
                          تم الاتصال بقاعدة البيانات بنجاح (حقيقي)
                        </motion.div>
                      )}
                      {dbTestStatus === 'error' && (
                        <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} className="mt-2 flex items-center gap-1.5 text-red-600 text-sm font-medium">
                          <XCircle className="w-4 h-4" />
                          فشل الاتصال بقاعدة البيانات. يرجى التأكد من الرابط.
                        </motion.div>
                      )}
                    </AnimatePresence>
                    
                    <p className="text-xs text-gray-500 mt-2">سيتم حفظ هذا الرابط ومزامنته عبر جميع الأجهزة المتصلة.</p>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">مفتاح Firebase (API Key)</label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <input 
                          type="text" 
                          value={localSettings.firebaseKey || ''}
                          onChange={(e) => {
                            setLocalSettings({...localSettings, firebaseKey: e.target.value});
                            setFirebaseTestStatus('idle');
                          }}
                          className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none font-mono text-sm"
                          placeholder="AIzaSy..."
                          dir="ltr"
                        />
                      </div>
                      <button
                        onClick={testFirebaseConnection}
                        disabled={firebaseTestStatus === 'testing' || !localSettings.firebaseKey}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
                      >
                        {firebaseTestStatus === 'testing' ? <Loader2 className="w-4 h-4 animate-spin" /> : 'فحص المفتاح'}
                      </button>
                    </div>

                    <AnimatePresence>
                      {firebaseTestStatus === 'success' && (
                        <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} className="mt-2 flex items-center gap-1.5 text-green-600 text-sm font-medium">
                          <CheckCircle2 className="w-4 h-4" />
                          المفتاح صالح ويعمل بنجاح
                        </motion.div>
                      )}
                      {firebaseTestStatus === 'error' && (
                        <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -5 }} className="mt-2 flex items-center gap-1.5 text-red-600 text-sm font-medium">
                          <XCircle className="w-4 h-4" />
                          المفتاح غير صالح. يرجى التأكد منه.
                        </motion.div>
                      )}
                    </AnimatePresence>

                    <p className="text-xs text-gray-500 mt-2">مفتاح واجهة برمجة تطبيقات Firebase.</p>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm text-gray-600 mb-2">اتجاه حركة الشريط العلوي</label>
                  <div className="flex gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        name="marqueeDirection"
                        value="rtl"
                        checked={localSettings.marqueeDirection !== 'ltr'}
                        onChange={() => setLocalSettings({...localSettings, marqueeDirection: 'rtl'})}
                        className="text-blue-600 focus:ring-blue-500 w-4 h-4"
                      />
                      <span className="text-sm text-gray-800">من اليمين لليسار</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        name="marqueeDirection"
                        value="ltr"
                        checked={localSettings.marqueeDirection === 'ltr'}
                        onChange={() => setLocalSettings({...localSettings, marqueeDirection: 'ltr'})}
                        className="text-blue-600 focus:ring-blue-500 w-4 h-4"
                      />
                      <span className="text-sm text-gray-800">من اليسار لليمين</span>
                    </label>
                  </div>
                </div>
              </div>

            </div>
          )}

          {activeTab === 'messages' && (
            <div className="space-y-8">
              <div className="border-b pb-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-gray-500" />
                  إدارة الرسائل المنبثقة
                </h3>
              </div>
              
              {/* Current Message Status */}
              <div className="bg-gray-50 p-4 rounded-xl border flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-gray-900">حالة الرسالة الحالية</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {localSettings.broadcastMessage?.isActive ? 'الرسالة تظهر للزوار حالياً' : 'لا توجد رسالة نشطة'}
                  </p>
                  {localSettings.broadcastMessage?.text && (
                    <p className="text-sm mt-2 text-gray-700 bg-white p-2 rounded border">
                      "{localSettings.broadcastMessage.text}"
                    </p>
                  )}
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input 
                    type="checkbox" 
                    className="sr-only peer"
                    checked={localSettings.broadcastMessage?.isActive || false}
                    onChange={(e) => toggleMessageActive(e.target.checked)}
                    disabled={!localSettings.broadcastMessage?.text || saveStatus === 'saving'}
                  />
                  <div className="w-14 h-7 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:right-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              {/* Send New Message */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">إرسال رسالة جديدة</label>
                <textarea 
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all resize-none h-32"
                  placeholder="اكتب رسالتك هنا..."
                />
                <button 
                  onClick={handleSendMessage}
                  disabled={saveStatus === 'saving' || !messageText.trim()}
                  className="mt-3 w-full md:w-auto px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors disabled:opacity-50"
                >
                  {saveStatus === 'saving' ? 'جاري الإرسال...' : 'إرسال ونشر الرسالة'}
                </button>
              </div>

              {/* Message History */}
              {localSettings.messageHistory && localSettings.messageHistory.length > 0 && (
                <div className="pt-6 border-t">
                  <h4 className="font-semibold text-gray-900 mb-4">سجل الرسائل السابقة</h4>
                  <div className="space-y-3">
                    {localSettings.messageHistory.map((msg: any) => (
                      <div key={msg.id} className="bg-white border rounded-lg p-4 flex justify-between items-start gap-4">
                        <div>
                          <p className="text-gray-800">{msg.text}</p>
                          <p className="text-xs text-gray-400 mt-2" dir="ltr">{format(new Date(msg.date), 'yyyy-MM-dd HH:mm')}</p>
                        </div>
                        <div className="flex gap-2">
                          {confirmDeleteId === msg.id ? (
                            <div className="flex items-center gap-2 bg-red-50 px-3 py-1.5 rounded-lg">
                              <span className="text-xs text-red-600 font-medium">تأكيد الحذف؟</span>
                              <button 
                                onClick={() => deleteMessageFromHistory(msg.id)}
                                className="text-white bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-xs transition-colors"
                              >
                                نعم
                              </button>
                              <button 
                                onClick={() => setConfirmDeleteId(null)}
                                className="text-gray-600 bg-gray-200 hover:bg-gray-300 px-2 py-1 rounded text-xs transition-colors"
                              >
                                إلغاء
                              </button>
                            </div>
                          ) : (
                            <>
                              <button 
                                onClick={() => setMessageText(msg.text)}
                                className="text-blue-600 hover:bg-blue-50 px-3 py-1.5 rounded-lg text-sm transition-colors whitespace-nowrap"
                              >
                                إعادة استخدام
                              </button>
                              <button 
                                onClick={() => setConfirmDeleteId(msg.id)}
                                className="text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-lg text-sm transition-colors whitespace-nowrap"
                              >
                                حذف
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'visitors' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b pb-4">
                <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                  <Users className="w-5 h-5 text-gray-500" />
                  سجل الزوار (آخر 50 زيارة)
                </h3>
                {showClearConfirm ? (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-red-600 font-medium">هل أنت متأكد؟</span>
                    <button onClick={clearVisitors} className="bg-red-600 text-white px-3 py-1 rounded-lg text-sm hover:bg-red-700 transition-colors">نعم، امسح</button>
                    <button onClick={() => setShowClearConfirm(false)} className="bg-gray-200 text-gray-700 px-3 py-1 rounded-lg text-sm hover:bg-gray-300 transition-colors">إلغاء</button>
                  </div>
                ) : (
                  <button 
                    onClick={() => setShowClearConfirm(true)}
                    className="text-red-500 hover:bg-red-50 px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    مسح السجل
                  </button>
                )}
              </div>

              {isLoadingVisitors ? (
                <div className="py-12 flex justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
              ) : visitors.length === 0 ? (
                <div className="py-12 text-center text-gray-500">
                  لا يوجد زوار حتى الآن
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-right">
                    <thead className="bg-gray-50 text-gray-600">
                      <tr>
                        <th className="px-4 py-3 rounded-tr-lg">التاريخ والوقت</th>
                        <th className="px-4 py-3">عدد الزيارات</th>
                        <th className="px-4 py-3">المنصة</th>
                        <th className="px-4 py-3">اللغة</th>
                        <th className="px-4 py-3 rounded-tl-lg">المتصفح / الجهاز</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {visitors.map((v) => (
                        <tr key={v.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 whitespace-nowrap" dir="ltr">
                            {v.visitedAt ? format(new Date(v.visitedAt), 'yyyy-MM-dd HH:mm:ss') : '-'}
                          </td>
                          <td className="px-4 py-3">
                            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                              {v.visitCount || 1}
                            </span>
                          </td>
                          <td className="px-4 py-3">{v.platform || '-'}</td>
                          <td className="px-4 py-3">{v.language || '-'}</td>
                          <td className="px-4 py-3 text-gray-500 max-w-xs truncate" title={v.userAgent} dir="ltr">
                            {v.userAgent || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

