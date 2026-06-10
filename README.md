# ⚡ Nexus Quantum OS - Trading Terminal v9.0

[![Python Version](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI_Framework-CustomTkinter-darkblue.svg)](https://github.com/TomsOpts/customtkinter)
[![Database](https://img.shields.io/badge/Database-SQLite-green.svg)](https://www.sqlite.org/)
[![Data Science](https://img.shields.io/badge/Data_Analysis-Pandas-purple.svg)](https://pandas.pydata.org/)

---

## 🌍 Overview / Genel Bakış

**🇬🇧 English:** Nexus Quantum OS is an enterprise-grade **Algorithmic Trading & Automation Terminal** engineered with modern Python libraries and styled according to premium Apple (macOS) design principles. The system establishes a secure, asynchronous (threaded) pipeline with the Binance network, enabling traders to manage portfolios, track custom watchlists, or deploy mathematical autopilot AI strategies.

**🇹🇷 Türkçe:** Nexus Quantum OS, modern Python kütüphaneleri ve premium Apple (macOS) tasarım standartları kullanılarak geliştirilmiş, kurumsal düzeyde bir **Algoritmik Ticaret ve Otomasyon Terminalidir.** Sistem, Binance ağı ile asenkron (Threading) bir hat kurarak kullanıcıların portföylerini yönetmesini, özel sepetler oluşturmasını ve matematiksel bir yapay zeka otopilot motorunu devreye almasını sağlar.

---

## 🚀 Key Features / Öne Çıkan Özellikler

### 🤖 Pandas RSI AI Autopilot / Yapay Zeka Otopilotu
* **EN:** Leverages `pandas` to parse 15-minute market candlesticks. Automatically triggers a `BUY` order when RSI falls below 30 (Oversold) and a `SELL` order when RSI breaks above 70 (Overbought).
* **TR:** `pandas` kütüphanesini kullanarak 15 dakikalık piyasa mumlarını arka planda analiz eder. RSI 30'un altına indiğinde (Aşırı Satım) otomatik `AL`, 70'in üzerine çıktığında (Aşırı Alım) otomatik `SAT` emri gönderir.

### 💾 SQLite Vault Data Persistence / SQLite Veri Tabanı
* **EN:** Built-in relational database that permanently logs trade history and updates your custom watchlist dynamically.
* **TR:** İşlem geçmişini kalıcı olarak kaydeden ve kullanıcı sepetini dinamik olarak güncelleyen yerel SQLite ilişkisel veri tabanı entegrasyonu.

### 🧵 Multi-Threading Engine / Asenkron Çoklu İş Parçacığı
* **EN:** Separate network pipelines prevent UI freezing during real-time Binance API handshakes, guaranteeing a crisp desktop experience.
* **TR:** Canlı Binance API veri transferleri sırasında arayüzün donmasını engelleyen, arka planda bağımsız çalışan asenkron iş parçacığı mimarisi.

### 🎨 Apple Style UI / macOS Tasarım Dili
* **EN:** Clean, sharp, corporate SaaS aesthetic with native dynamic Light/Dark mode switching, built using CustomTkinter.
* **TR:** Göz yorucu tasarımlar yerine CustomTkinter ile oluşturulmuş minimalist, dinamik Açık/Koyu tema destekli kurumsal Apple arayüzü.

---

## 📂 Project Structure / Klasör Yapısı

```text
crypto_dashboard/
├── nexus_quantum_bot.py        # Core Production Python Script / Ana Kod Dosyası
├── README.md                   # Dual-Language Documentation / İki Dilli Kılavuz
└── requirements.txt            # System Dependency Manifest / Kütüphane Listesi
