# 📡 RadarPro TITAN Telegram Intelligence Node (v3.7)

RadarPro TITAN, yüksek frekanslı kripto veri akışını, kurumsal düzeyde indikatörleri ve AI tahminlerini doğrudan Telegram üzerinden sunan, dünyanın en gelişmiş "Kuant İşletim Sistemi" botudur.

## 🚀 Ana Özellikler

- **🔴 Canlı Fiyat Yayını (`/canli`):** Spark Silver veri katmanından gelen verilerle saniyelik/anlık fiyat güncellemeleri.
- **⚖️ Global Arbitraj Radarı:** 10 farklı büyük borsayı (Binance, OKX, Bybit, KuCoin vb.) anlık tarayarak arbitraj fırsatlarını %0.001 hassasiyetle yakalar.
- **🧠 Spark AI (Gemini Entegrasyonu):** Piyasa duyarlılığını ve teknik verileri yorumlayarak profesyonel yatırım tavsiyesi olmayan analizler sunar.
- **🧲 Likidasyon Mıknatıs Takibi:** 25x, 50x ve 100x likidasyon bölgelerini anlık olarak raporlar.
- **🐋 Balina & Hacim Alertleri:** Kurumsal düzeydeki büyük emirleri ve hacim patlamalarını (CVD Delta) anlık bildirir.

## 🛠️ Teknik Altyapı

- **Dil:** Python 3.10+ (Aiogram 3.x)
- **Veri Akışı:** Kafka -> PySpark (Silver Process) -> Redis (Cache) -> Bot
- **Asenkron Yapı:** `aiohttp` ve `redis.asyncio` ile yüksek hızlı, bloklanmayan işlem kapasitesi.
- **API Katmanı:** RadarPro Ingestion API (FastAPI) ile tam entegrasyon.

## 📋 Komut Listesi

| Komut | Açıklama |
|-------|----------|
| `/start` | Botu ve ana kontrol panelini başlatır. |
| `/canli [SEMBOL]` | 2 dakikalık yüksek frekanslı canlı yayın başlatır. |
| `/fiyat [SEMBOL]` | Anlık derinlemesine teknik analiz snapshot'ı sunar. |
| `/arbitraj` | Piyasadaki en karlı 15 arbitraj fırsatını listeler. |
| `/ai [SORU]` | Gemini AI destekli kuant analizi yapar. |
| `/haberler` | Küresel kripto piyasasından anlık flaş haberler. |
| `/durum` | Sistemin servis (Kafka, Redis, API) sağlık durumunu raporlar. |

## 🧪 Sunum & Geliştirme Notları

- **Presentation Mode:** Tüm üyelik kısıtlamaları (FREE/VIP) sunum için devre dışı bırakılmıştır.
- **Real-time Sync:** Veriler terminal arayüzü (HTML) ile 10ms altında tam senkronize çalışır.

---
📡 **RadarPro Intelligence Group**
*"Bilgi, en güçlü kaldıraçtır."*
