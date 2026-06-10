import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
import sqlite3
import webbrowser
import pandas as pd
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- PREMIUM APPLE GÖRSEL ALTYAPISI ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class NexusQuantumBotV9(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NEXUS QUANTUM OS - ENTERPRISE TRADING TERMINAL")
        self.geometry("1050x780")
        self.resizable(False, False)
        self.configure(fg_color=("#F5F5F7", "#0F0F11"))

        # --- MERKEZİ VERİ DEĞİŞKENLERİ ---
        self.client = None
        self.is_connected = False
        self.all_symbols = []
        self.filtered_symbols = []
        self.my_basket = []
        
        self.current_coin = "BTCUSDT"
        self.current_price = 0.0
        self.price_change_pct = 0.0
        self.history_prices = []
        self.usdt_balance = 0.0

        # Algoritmik Yapay Zeka Değişkenleri
        self.is_algo_active = False
        self.algo_coin = "BTCUSDT"
        self.current_rsi = 50.0

        # --- ÇEKİRDEK MOTORLARI DEVREYE AL ---
        self.init_database()
        self.build_apple_interface()

        # Asenkron Thread İşçilerini Başlat
        threading.Thread(target=self.load_all_binance_symbols, daemon=True).start()
        threading.Thread(target=self.live_market_data_stream, daemon=True).start()
        threading.Thread(target=self.quantum_ai_strategy_core, daemon=True).start()
        
        self.update_chart_data()
        self.system_refresh_loop()

    # ==========================================
    # 💾 SQLITE VERI TABANI MOTORU
    # ==========================================
    def init_database(self):
        """Sistem geçmişi ve izleme sepeti veri tabanını kurar"""
        self.db_conn = sqlite3.connect("nexus_vault.db", check_same_thread=False)
        self.db_cursor = self.db_conn.cursor()
        
        # İşlemler tablosu
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT, coin TEXT, side TEXT, qty REAL, price REAL, mode TEXT
            )
        """)
        # Sepetim tablosu
        self.db_cursor.execute("CREATE TABLE IF NOT EXISTS watchlist (coin TEXT PRIMARY KEY)")
        self.db_conn.commit()
        self.sync_basket_from_db()

    def sync_basket_from_db(self):
        try:
            self.db_cursor.execute("SELECT coin FROM watchlist")
            self.my_basket = [row[0] for row in self.db_cursor.fetchall()]
        except Exception:
            self.my_basket = ["BTCUSDT", "ETHUSDT"]

    # ==========================================
    # 🤖 PANDAS YAPAY ZEKA VE STRATEJİ ÇEKİRDEĞİ
    # ==========================================
    def calculate_pandas_rsi(self, symbol, period=14):
        """Binance ham mum verilerini alıp Pandas ile RSI indikatörünü hesaplar"""
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=50"
            res = requests.get(url, timeout=3).json()
            
            df = pd.DataFrame(res, columns=['time', 'open', 'high', 'low', 'close', 'vol', 'c_time', 'qav', 'nat', 'tbb', 'tbq', 'ignore'])
            df['close'] = df['close'].astype(float)
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / (loss + 1e-10) # 0'a bölünme hatasını engellemek için mini tolerans
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except Exception:
            return 50.0

    def quantum_ai_strategy_core(self):
        """7/24 Arka planda piyasayı tarayıp otomatik karar alan yapay zeka motoru"""
        while True:
            if self.is_algo_active and self.current_price > 0:
                self.current_rsi = self.calculate_pandas_rsi(self.algo_coin)
                
                # RSI Dip Stratejisi (Alım)
                if self.current_rsi < 30.0:
                    self.execute_trade_logic(self.algo_coin, "BUY", 0.001, "AI AUTOMATION (RSI OVERSOLD)")
                    self.send_telegram_notification(f"🤖 AI TRADE EXECUTED\nSymbol: {self.algo_coin}\nSide: BUY\nRSI: {self.current_rsi:.2f}")
                    self.toggle_algo_engine()
                
                # RSI Zirve Stratejisi (Satım)
                elif self.current_rsi > 70.0:
                    self.execute_trade_logic(self.algo_coin, "SELL", 0.001, "AI AUTOMATION (RSI OVERBOUGHT)")
                    self.send_telegram_notification(f"🤖 AI TRADE EXECUTED\nSymbol: {self.algo_coin}\nSide: SELL\nRSI: {self.current_rsi:.2f}")
                    self.toggle_algo_engine()
                    
            time.sleep(10)

    def process_pandas_pnl_analytics(self):
        """SQLite verilerini Pandas veri çerçevesine döküp finansal rapor hazırlar"""
        try:
            df = pd.read_sql_query("SELECT * FROM trades", self.db_conn)
            if df.empty: return 0, 0.0, 0.0
            
            total_trades = len(df)
            buy_volume = df[df['side'] == 'BUY']['qty'] * df[df['side'] == 'BUY']['price']
            sell_volume = df[df['side'] == 'SELL']['qty'] * df[df['side'] == 'SELL']['price']
            
            net_pnl = sell_volume.sum() - buy_volume.sum()
            total_volume = buy_volume.sum() + sell_volume.sum()
            return total_trades, total_volume, net_pnl
        except Exception:
            return 0, 0.0, 0.0

    # ==========================================
    # 📱 APPLE SEKMELİ UI TASARIMI
    # ==========================================
    def build_apple_interface(self):
        # Üst Panel
        header = ctk.CTkFrame(self, height=60, fg_color="transparent")
        header.pack(fill="x", pady=(15, 0), padx=25)
        
        ctk.CTkLabel(header, text="NEXUS QUANTUM OS", font=ctk.CTkFont(family="SF Pro Display", size=24, weight="bold")).pack(side="left")
        
        self.theme_switch = ctk.CTkSwitch(header, text="Karanlık Tema", font=ctk.CTkFont(weight="bold"), command=self.handle_theme_change)
        self.theme_switch.pack(side="right")
        self.theme_switch.select()

        # macOS Tarzı Ana Sekme Yapısı
        self.tabview = ctk.CTkTabview(self, corner_radius=16, fg_color=("#FFFFFF", "#18181C"))
        self.tabview.pack(fill="both", expand=True, padx=20, pady=15)
        
        self.tab_market = self.tabview.add("📊 Piyasalar & Sepetim")
        self.tab_ai = self.tabview.add("🤖 Yapay Zeka Kontrol")
        self.tab_wallet = self.tabview.add("💼 Cüzdan & Analitik")
        self.tab_config = self.tabview.add("⚙️ Sistem Entegrasyonu")

        # Sekme İçeriklerini İnşa Et
        self.init_market_tab()
        self.init_ai_tab()
        self.init_wallet_tab()
        self.init_config_tab()

    # 1. SEKME: MARKET VE SEPET
    def init_market_tab(self):
        left_frame = ctk.CTkFrame(self.tab_market, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        right_frame = ctk.CTkFrame(self.tab_market, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Sol Alan: Arama Motoru ve Küresel Havuz
        ctk.CTkLabel(left_frame, text="🔍 Küresel Borsa Havuzu", font=ctk.CTkFont(size=13, weight="bold"), text_color="gray").pack(anchor="w")
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.rebuild_search_ui_buttons())
        ctk.CTkEntry(left_frame, textvariable=self.search_var, placeholder_text="Yüzlerce coin arasında ara...").pack(fill="x", pady=5)
        
        self.scroll_search = ctk.CTkScrollableFrame(left_frame, height=130, fg_color=("#F5F5F7", "#0F0F11"))
        self.scroll_search.pack(fill="x", pady=(0, 10))

        # Sol Alt Alan: Kullanıcı İzleme Sepeti
        ctk.CTkLabel(left_frame, text="🧺 Benim Portföy Sepetim", font=ctk.CTkFont(size=13, weight="bold"), text_color="#007AFF").pack(anchor="w")
        self.scroll_basket = ctk.CTkScrollableFrame(left_frame, fg_color=("#F5F5F7", "#0F0F11"))
        self.scroll_basket.pack(fill="both", expand=True, pady=5)

        # Sağ Alan: Büyük Bilgi Kartı
        self.card_info = ctk.CTkFrame(right_frame, corner_radius=14, fg_color=("#F5F5F7", "#1E1E22"))
        self.card_info.pack(fill="x", pady=(0, 10))
        
        self.lbl_active_coin = ctk.CTkLabel(self.card_info, text="BTCUSDT", font=ctk.CTkFont(size=15, weight="bold"), text_color="gray")
        self.lbl_active_coin.pack(pady=(12, 2))
        self.lbl_live_price = ctk.CTkLabel(self.card_info, text="Yükleniyor...", font=ctk.CTkFont(size=40, weight="bold"))
        self.lbl_live_price.pack(pady=2)
        self.lbl_live_change = ctk.CTkLabel(self.card_info, text="% 0.00", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_live_change.pack(pady=(0, 12))

        # Sepet Yönetim Butonları
        row_basket_btn = ctk.CTkFrame(right_frame, fg_color="transparent")
        row_basket_btn.pack(fill="x", pady=(0, 15))
        ctk.CTkButton(row_basket_btn, text="＋ Sepete Ekle", fg_color="#007AFF", hover_color="#0056B3", command=self.add_coin_to_watchlist).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(row_basket_btn, text="🗑️ Sepetten Çıkar", fg_color="#8E8E93", hover_color="#636366", command=self.remove_coin_from_watchlist).pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Yerel Çizgi Grafik (Harita) Alanı
        ctk.CTkLabel(right_frame, text="📈 Son 24 Saatlik Trend Grafiği", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").pack(anchor="w")
        self.canvas_trend = tk.Canvas(right_frame, height=100, bg="#111115", highlightthickness=0)
        self.canvas_trend.pack(fill="x", pady=5)
        ctk.CTkButton(right_frame, text="TradingView Profesyonel Haritayı Aç ↗", height=24, fg_color="transparent", text_color="#4facfe", command=self.launch_tradingview_link).pack(anchor="e")

        # Manuel Emir Verme Alanı
        ctk.CTkLabel(right_frame, text="İşlem Miktarı (Adet):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 0))
        self.entry_trade_qty = ctk.CTkEntry(right_frame, placeholder_text="0.001", justify="center")
        self.entry_trade_qty.insert(0, "0.001")
        self.entry_trade_qty.pack(fill="x", pady=4)

        self.switch_safety_mode = ctk.CTkSwitch(right_frame, text="Güvenli Simülasyon (Bakiye Koruması)", progress_color="#FF3B30", font=ctk.CTkFont(weight="bold"))
        self.switch_safety_mode.pack(pady=10)
        self.switch_safety_mode.select()

        row_trade_btn = ctk.CTkFrame(right_frame, fg_color="transparent")
        row_trade_btn.pack(fill="x", pady=5)
        ctk.CTkButton(row_trade_btn, text="MARKET BUY (AL)", fg_color="#34C759", hover_color="#28A745", height=40, font=ctk.CTkFont(weight="bold"), command=lambda: self.trigger_manual_order("BUY")).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(row_trade_btn, text="MARKET SELL (SAT)", fg_color="#FF3B30", hover_color="#D70015", height=40, font=ctk.CTkFont(weight="bold"), command=lambda: self.trigger_manual_order("SELL")).pack(side="right", fill="x", expand=True, padx=(5, 0))

    # 2. SEKME: YAPAY ZEKA KONTROLÜ
    def init_ai_tab(self):
        ai_card = ctk.CTkFrame(self.tab_ai, corner_radius=14, fg_color=("#E5F0FF", "#0A244D"))
        ai_card.pack(fill="x", padx=25, pady=25)
        
        ctk.CTkLabel(ai_card, text="Quantum AI Autopilot Engine", font=ctk.CTkFont(size=18, weight="bold"), text_color="#007AFF").pack(pady=(15, 5))
        ctk.CTkLabel(ai_card, text="Yapay zeka arka planda asenkron olarak Pandas matematik kütüphanesini çalıştırır. Belirlediğiniz varlığın 15 dakikalık mum grafiğinde RSI değerini hesaplar. RSI 30 altına indiğinde dipten otomatik satın alır, 70 üstüne çıktığında kâr realizasyonu yaparak satar.", wraplength=650, text_color=("#1C1C1E", "#A6ADC8")).pack(pady=10, padx=20)
        
        self.entry_ai_target_coin = ctk.CTkEntry(ai_card, placeholder_text="İzlenecek Çift (Örn: BTCUSDT)", height=38, justify="center")
        self.entry_ai_target_coin.insert(0, "BTCUSDT")
        self.entry_ai_target_coin.pack(fill="x", padx=100, pady=10)

        self.lbl_ai_engine_status = ctk.CTkLabel(ai_card, text="Otopilot Durumu: DEAKTİF ⏸️", font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF3B30")
        self.lbl_ai_engine_status.pack(pady=5)
        
        self.lbl_ai_live_rsi = ctk.CTkLabel(ai_card, text="Canlı RSI İndikatörü: Hesaplamalar Bekleniyor...", font=ctk.CTkFont(family="Consolas", size=18, weight="bold"))
        self.lbl_ai_live_rsi.pack(pady=(5, 15))

        self.btn_toggle_ai = ctk.CTkButton(ai_card, text="🤖 YAPAY ZEKA OTOPİLOTUNU DEVREYE AL", height=45, font=ctk.CTkFont(weight="bold"), fg_color="#007AFF", hover_color="#0056B3", command=self.toggle_algo_engine)
        self.btn_toggle_ai.pack(pady=(0, 20), padx=100, fill="x")

    # 3. SEKME: CÜZDAN VE PNL ANALİTİK
    def init_wallet_tab(self):
        # Finansal Gösterge Kartları Üst Alanı
        self.stats_frame = ctk.CTkFrame(self.tab_wallet, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=15)
        
        # Yerel Defter Kayıt Alanı (SQLite Geçmişi)
        ctk.CTkLabel(self.tab_wallet, text="📜 Sistem Muhasebe Kayıtları (Kalıcı SQLite Defteri)", font=ctk.CTkFont(size=13, weight="bold"), text_color="gray").pack(anchor="w", padx=25, pady=(10, 2))
        self.txt_history_log = ctk.CTkTextbox(self.tab_wallet, font=ctk.CTkFont(family="Consolas", size=12), fg_color=("#F5F5F7", "#0F0F11"), corner_radius=12)
        self.txt_history_log.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.rebuild_wallet_analytics_ui()

    def rebuild_wallet_analytics_ui(self):
        """Pandas analizlerini ve veri tabanı loglarını ekrana basar"""
        for w in self.stats_frame.winfo_children(): w.destroy()
        
        t_trades, t_vol, net_pnl = self.process_pandas_pnl_analytics()
        
        # Kart 1: Cüzdan Bakiyesi
        c1 = ctk.CTkFrame(self.stats_frame, corner_radius=12, fg_color=("#E5F0FF", "#0A244D"))
        c1.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(c1, text="Cüzdan Bakiyesi", font=ctk.CTkFont(size=11), text_color="#007AFF").pack(pady=(8, 0))
        self.lbl_wallet_usdt = ctk.CTkLabel(c1, text=f"$ {self.usdt_balance:,.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color="#007AFF")
        self.lbl_wallet_usdt.pack(pady=(0, 8))

        # Kart 2: Toplam Hacim
        c2 = ctk.CTkFrame(self.stats_frame, corner_radius=12, fg_color=("#F5F5F7", "#1E1E22"))
        c2.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(c2, text="Bot İşlem Hacmi", font=ctk.CTkFont(size=11)).pack(pady=(8, 0))
        ctk.CTkLabel(c2, text=f"${t_vol:,.2f}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 8))

        # Kart 3: Net PNL
        c3 = ctk.CTkFrame(self.stats_frame, corner_radius=12, fg_color=("#F5F5F7", "#1E1E22"))
        c3.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkLabel(c3, text="Sistem Net PNL", font=ctk.CTkFont(size=11)).pack(pady=(8, 0))
        p_color = "#34C759" if net_pnl >= 0 else "#FF3B30"
        ctk.CTkLabel(c3, text=f"${net_pnl:,.2f}", font=ctk.CTkFont(size=20, weight="bold"), text_color=p_color).pack(pady=(0, 8))
        
        self.rebuild_history_textbox_log()

    def rebuild_history_textbox_log(self):
        self.txt_history_log.configure(state="normal")
        self.txt_history_log.delete("1.0", tk.END)
        try:
            self.db_cursor.execute("SELECT date, coin, side, qty, price, mode FROM trades ORDER BY id DESC")
            rows = self.db_cursor.fetchall()
            self.txt_history_log.insert(tk.END, f"{'Zaman Damgası':<22} {'Varlık':<12} {'Yön':<8} {'Miktar':<12} {'Birim Fiyat':<14} {'Mekanizma Motoru'}\n")
            self.txt_history_log.insert(tk.END, "="*85 + "\n")
            for r in rows:
                self.txt_history_log.insert(tk.END, f"{r[0]:<22} {r[1]:<12} {r[2]:<8} {r[3]:<12.4f} ${r[4]:<13.2f} {r[5]}\n")
        except Exception: pass
        self.txt_history_log.configure(state="disabled")

    # 4. SEKME: ENTEGRASYON VE BULUT AYARLARI
    def init_config_tab(self):
        box_api = ctk.CTkFrame(self.tab_config, corner_radius=14, fg_color=("#F5F5F7", "#1E1E22"))
        box_api.pack(fill="x", padx=25, pady=15)
        
        ctk.CTkLabel(box_api, text="🔐 1. Cloud API Gateway Configuration", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_api_key = ctk.CTkEntry(box_api, placeholder_text="Binance API Key girin...", height=35)
        self.entry_api_key.pack(fill="x", padx=20, pady=5)
        self.entry_secret_key = ctk.CTkEntry(box_api, placeholder_text="Binance Secret Key girin...", show="*", height=35)
        self.entry_secret_key.pack(fill="x", padx=20, pady=5)
        
        self.btn_api_connect = ctk.CTkButton(box_api, text="Anahtarları Doğrula & Cüzdanı Eşitle", height=38, font=ctk.CTkFont(weight="bold"), command=self.connect_binance_cloud_gateway)
        self.btn_api_connect.pack(fill="x", padx=20, pady=(10, 15))

        box_tg = ctk.CTkFrame(self.tab_config, corner_radius=14, fg_color=("#F5F5F7", "#1E1E22"))
        box_tg.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(box_tg, text="📱 2. Mobil Telegram Bildirim Ağı", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(15, 2))
        ctk.CTkLabel(box_tg, text="BotFather şifreniz yoksa boş bırakabilirsiniz, sistem etkilenmeden çalışır.", font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))
        
        self.entry_tg_token = ctk.CTkEntry(box_tg, placeholder_text="Telegram HTTP Bot Token (Örn: 51234:AAFe...)", height=35)
        self.entry_tg_token.pack(fill="x", padx=20, pady=5)
        self.entry_tg_chat = ctk.CTkEntry(box_tg, placeholder_text="Telegram Chat ID numaranız", height=35)
        self.entry_tg_chat.pack(fill="x", padx=20, pady=(5, 15))

    # ==========================================
    # ⚙️ ARKA PLAN VERI AKIŞ VE KONTROL MODÜLLERİ
    # ==========================================
    def handle_theme_change(self):
        ctk.set_appearance_mode("dark" if self.theme_switch.get() == 1 else "light")

    def toggle_algo_engine(self):
        self.is_algo_active = not self.is_algo_active
        if self.is_algo_active:
            self.algo_coin = self.entry_ai_target_coin.get().upper().strip()
            self.lbl_ai_engine_status.configure(text=f"Otopilot Durumu: {self.algo_coin} TARANIYOR 🟢", text_color="#34C759")
            self.btn_toggle_ai.configure(text="🛑 AUTOPILOT ENGINE'I DURDUR", fg_color="#FF3B30", hover_color="#D70015")
            self.send_telegram_notification(f"🚀 AI OS DEPLOYED\nAutopilot has started scanning {self.algo_coin} market matrix.")
        else:
            self.lbl_ai_engine_status.configure(text="Otopilot Durumu: DEAKTİF ⏸️", text_color="#FF3B30")
            self.btn_toggle_ai.configure(text="🤖 YAPAY ZEKA OTOPİLOTUNU DEVREYE AL", fg_color=["#3B8ED0", "#1F6AA5"])

    def connect_binance_cloud_gateway(self):
        k = self.entry_api_key.get().strip()
        s = self.entry_secret_key.get().strip()
        if not k or not s: return

        try:
            self.client = Client(k, s)
            acct = self.client.get_account()
            for asset in acct['balances']:
                if asset['asset'] == 'USDT':
                    self.usdt_balance = float(asset['free'])
                    break
            self.is_connected = True
            self.btn_api_connect.configure(text="✓ Entegrasyon Sağlandı", fg_color="#34C759", state="disabled")
            self.rebuild_wallet_analytics_ui()
            messagebox.showinfo("Başarılı", "Binance API sunucularına şifreli tünel açıldı, bakiye senkronize.")
        except Exception:
            messagebox.showerror("Hata", "API geçersiz veya borsadan Spot ticaret izni verilmemiş.")

    def load_all_binance_symbols(self):
        try:
            res = requests.get("https://api.binance.com/api/v3/ticker/price", timeout=5).json()
            self.all_symbols = sorted([item['symbol'] for item in res if item['symbol'].endswith('USDT')])
            self.filtered_symbols = self.all_symbols
            self.rebuild_search_ui_buttons()
            self.rebuild_basket_ui_buttons()
        except Exception: pass

    def rebuild_search_ui_buttons(self):
        q = self.search_var.get().upper().strip()
        self.filtered_symbols = [s for s in self.all_symbols if q in s] if q else self.all_symbols
        
        for w in self.scroll_search.winfo_children(): w.destroy()
        for sym in self.filtered_symbols[:15]:
            btn = ctk.CTkButton(self.scroll_search, text=f" ₿ {sym}", font=ctk.CTkFont(size=12, weight="bold"), fg_color="transparent", text_color=("#1C1C1E", "#FFFFFF"), hover_color=("#E5E5EA", "#2C2C2E"), anchor="w", height=28, command=lambda s=sym: self.focus_market_target(s))
            btn.pack(fill="x", pady=1)

    def rebuild_basket_ui_buttons(self):
        for w in self.scroll_basket.winfo_children(): w.destroy()
        if not self.my_basket:
            ctk.CTkLabel(self.scroll_basket, text="Sepet boş. Üstten coin arayıp ekleyin.", font=ctk.CTkFont(size=12, style="italic"), text_color="gray").pack(pady=15)
            return
        for b_coin in self.my_basket:
            btn = ctk.CTkButton(self.scroll_basket, text=f" 🧺 {b_coin}", font=ctk.CTkFont(size=12, weight="bold"), fg_color="transparent", text_color=("#1C1C1E", "#007AFF"), hover_color=("#E5E5EA", "#2C2C2E"), anchor="w", height=28, command=lambda c=b_coin: self.focus_market_target(c))
            btn.pack(fill="x", pady=1)

    def add_coin_to_watchlist(self):
        self.db_cursor.execute("INSERT OR IGNORE INTO watchlist (coin) VALUES (?)", (self.current_coin,))
        self.db_conn.commit()
        self.sync_basket_from_db()
        self.rebuild_basket_ui_buttons()

    def remove_coin_from_watchlist(self):
        self.db_cursor.execute("DELETE FROM watchlist WHERE coin = ?", (self.current_coin,))
        self.db_conn.commit()
        self.sync_basket_from_db()
        self.rebuild_basket_ui_buttons()

    def focus_market_target(self, symbol):
        self.current_coin = symbol
        self.lbl_active_coin.configure(text=symbol)
        self.lbl_live_price.configure(text="Sorgulanıyor...")
        self.update_chart_data()

    def live_market_data_stream(self):
        while True:
            try:
                url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={self.current_coin}"
                res = requests.get(url, timeout=3).json()
                self.current_price = float(res['lastPrice'])
                self.price_change_pct = float(res['priceChangePercent'])
            except Exception: pass
            time.sleep(1.2)

    def update_chart_data(self):
        def fetch():
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={self.current_coin}&interval=1h&limit=24"
                res = requests.get(url, timeout=5).json()
                self.history_prices = [float(candle[4]) for candle in res]
                self.draw_vector_trend_chart()
            except Exception: pass
        threading.Thread(target=fetch, daemon=True).start()

    def draw_vector_trend_chart(self):
        self.canvas_trend.delete("all")
        if not self.history_prices: return
        w, h = 450, 100
        min_p, max_p = min(self.history_prices), max(self.history_prices)
        spread = max_p - min_p if max_p != min_p else 1
        points = []
        step_x = w / (len(self.history_prices) - 1)
        for i, p in enumerate(self.history_prices):
            x = i * step_x
            y = h - 10 - ((p - min_p) / spread) * (h - 20)
            points.append((x, y))
        if len(points) > 1:
            self.canvas_trend.create_line(points, fill="#34C759" if self.price_change_pct >= 0 else "#FF3B30", width=2, smooth=True)

    def launch_tradingview_link(self):
        webbrowser.open(f"https://www.tradingview.com/symbols/BINANCE-{self.current_coin}/?theme=dark")

    def trigger_manual_order(self, side):
        if not self.is_connected:
            return messagebox.showerror("Bağlantı Yok", "Lütfen önce Sistem Entegrasyonu sekmesinden API bağlayın.")
        try:
            qty = float(self.entry_trade_qty.get())
            if qty <= 0: raise ValueError
        except Exception: return
        
        is_simulation = (self.switch_safety_mode.get() == 1)
        mode_label = "SİMÜLASYON TEST" if is_simulation else "CANLI GERÇEK"
        
        if messagebox.askyesno("Emir Onayı", f"Piyasa Emri: {side}\nVarlık: {self.current_coin}\nMiktar: {qty}\nMod: {mode_label}\n\nOnaylıyor musunuz?"):
            self.execute_trade_logic(self.current_coin, side, qty, f"MANUEL ({mode_label})")

    def execute_trade_logic(self, coin, side, qty, mode):
        try:
            is_simulation = "TEST" in mode or "SIMULATION" in mode
            if not is_simulation and self.client:
                self.client.create_order(symbol=coin, side=side, type='MARKET', quantity=qty)
            elif is_simulation and self.client:
                self.client.create_test_order(symbol=coin, side=side, type='MARKET', quantity=qty)
                
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db_cursor.execute("INSERT INTO trades (date, coin, side, qty, price, mode) VALUES (?, ?, ?, ?, ?, ?)",
                                  (now, coin, side, qty, self.current_price, mode))
            self.db_conn.commit()
            self.rebuild_wallet_analytics_ui()
        except BinanceAPIException as e:
            messagebox.showerror("Borsa Emir Reddi", e.message)

    def send_telegram_notification(self, msg):
        tok = self.entry_tg_token.get().strip()
        chat = self.entry_tg_chat.get().strip()
        if not tok or not chat: return
        url = f"https://api.telegram.org/bot{tok}/sendMessage"
        threading.Thread(target=lambda: requests.post(url, json={"chat_id": chat, "text": msg}, timeout=3)).start()

    # ==========================================
    # 🔁 KESINTISIZ YENILEME DÖNGÜSÜ
    # ==========================================
    def system_refresh_loop(self):
        if self.current_price > 0:
            self.lbl_live_price.configure(text=f"${self.current_price:,.4f}")
            self.lbl_live_change.configure(
                text=f"{'▲ +' if self.price_change_pct >= 0 else '▼ '}%{self.price_change_pct:.2f}",
                text_color="#34C759" if self.price_change_pct >= 0 else "#FF3B30"
            )
        if self.is_algo_active:
            self.lbl_ai_live_rsi.configure(text=f"Canlı RSI İndikatörü: {self.current_rsi:.2f}")
            
        self.after(400, self.system_refresh_loop)

if __name__ == "__main__":
    app = NexusQuantumBotV9()
    app.mainloop()