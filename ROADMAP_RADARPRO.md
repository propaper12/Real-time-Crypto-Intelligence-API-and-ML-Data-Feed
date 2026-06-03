# 🗺️ RadarPro: Otonom Güvenli İşlem ve AI Agent Yol Haritası

Bu döküman, RadarPro platformunun "Veri Terminali" aşamasından "Otonom Yapay Zeka İşlem Ağı" aşamasına geçiş planını içerir.

---

## 🎯 Vizyon
Kripto piyasalarındaki sahte hacim ve manipülasyonlardan arındırılmış, en güvenli arbitraj fırsatlarını otonom olarak bulan ve kullanıcı adına (veya harici botlara) karar veren bir ekosistem inşa etmek.

---

## 📅 Faz 1: "Güvenli Arbitraj" (Safe-Arbitrage) Motoru
**Amaç:** Fiyat farklarını risk metrikleriyle süzmek.

- [ ] **Data Merging:** `ingestion_api.py` üzerindeki arbitraj mantığına Redis'teki `GOD_MODE` verilerini (VPIN, Anomaly, Imbalance) entegre etmek.
- [ ] **Trust Score (Güven Skoru):** Her sinyal için 0-100 arası puan üreten bir algoritma yazmak.
    - *Kriterler:* Düşük VPIN, Anomali yok (No Wash Trading), Yüksek Emir Defteri Derinliği.
- [ ] **Smart Alerts:** Sadece Güven Skoru > 75 olan sinyallerin VIP kanallara ve API'ye "GÜVENLİ" etiketiyle gönderilmesi.

---

## 🧠 Faz 2: RadarAI - Karar Verici Agent
**Amaç:** Gemini 2.5 Flash'ı sadece soru cevaplayan değil, karar veren bir birim haline getirmek.

- [ ] **Proaktif Analiz:** Gemini'nin her 1 dakikada bir en karlı 5 sembolü analiz edip "Kısa Özet + Karar" üretmesi.
- [ ] **Context-Aware Decisions:** Fiyat + Haberler + Teknik Metrikler birleştirilerek Gemini'ye "İşleme girilmeli mi?" sorusunun sordurulması.
- [ ] **Agent API:** Dış trading botlarının AI'dan "Onay" alabileceği `/api/v1/agent/validate` endpoint'inin açılması.

---

## 🔌 Faz 3: Kurumsal API ve SDK (Agent-as-a-Service)
**Amaç:** Sistemin zekasını diğer geliştiricilere satılabilir hale getirmek.

- [ ] **Standardized API:** Tüm sinyal ve risk metriklerinin profesyonel Swagger dökümantasyonuyla dışarı açılması.
- [ ] **Webhook Gateway:** Önemli bir fırsat oluştuğunda harici botlara (TradingView, custom bots) "PUSH" bildirimi gönderilmesi.
- [ ] **Developer SDK:** Python ve Node.js için basit "RadarPro Client" kütüphane örneklerinin hazırlanması.

---

## 🤖 Faz 4: Native RadarPro Trading Bot (İşlem Motoru)
**Amaç:** Kullanıcıların analizle uğraşmadan, sistemin sinyallerini otomatik işleme dönüştürmesini sağlamak.

- [ ] **Execution Engine:** Binance ve diğer borsaların API'lerini kullanarak hızlı emir iletim modülü.
- [ ] **Risk Management Suite:** Kullanıcının durdurma (stop-loss) ve kâr alma (take-profit) limitlerini ayarlayabildiği panel.
- [ ] **Strategy Templates:** "Güvenli Arbitraj", "AI Destekli Trend Takibi" gibi hazır strateji paketleri.
- [ ] **P&L Dashboard:** Botun yaptığı işlemlerin anlık kâr/zarar durumunu gösteren profesyonel takip ekranı.
- [ ] **Telegram Approval:** Kritik işlemler için botun kullanıcıdan Telegram üzerinden onay alması (Opsiyonel Güvenlik).

---

## 🛠️ Teknik Öncelik Listesi (Hemen Başlanacaklar)
1. `ingestion_api.py` -> `get_arbitrage_opportunities` fonksiyonuna risk kontrolü ekle.
2. `arbitrage_worker.py` -> Mesaj formatına "Güven Skoru" ekle.
3. `ask_ai` -> "Trader" modunu güçlendir.

---
*Bu yol haritası RadarPro'yu sektördeki en güvenli ve zeki kripto altyapısı haline getirecektir.*
