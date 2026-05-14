# 🏡 AI Room Designer

ออกแบบห้องเปล่าของคุณเองให้เป็นพื้นที่สวยงาม ใช้ AI ช่วยแต่งแต้มด้วยความคิดสร้างสรรค์ของคุณ

## 🎯 ฟีเจอร์

- **เลือกประเภทห้อง** - Living Room, Bedroom, Kitchen, Office ฯลฯ
- **เลือกสไตล์ห้อง** - Modern, Minimalist, Japandi, Industrial, Scandinavian ฯลฯ
- **เลือกธีมสี** - Warm, Cool, Neutral, Bold, Earthy
- **เลือกเฟอร์นิเจอร์** - ลิสต์ที่เหมาะสมกับประเภทห้อง
- **🆕 อัพโหลดตกแต่ง** - อัพโหลดรูปเฟอร์นิเจอร์/ตกแต่ง
- **🆕 ตัดพื้นหลัง** - Auto-remove background ด้วย AI (rembg)
- **🆕 วางตกแต่งลงในภาพ** - ปรับตำแหน่งและขนาดของตกแต่ง
- **🆕🛍️ ตรวจจับและซื้อสินค้า** - AI ตรวจจับเฟอร์นิเจอร์ → แนะนำสินค้า → ช้อปปิ้งออนไลน์
- **เพิ่มรายละเอียด** - คำสั่งเพิ่มเติมสำหรับปรับแต่งเอง
- **AI สร้างห้อง** - ใช้ Gemini 2.5 Flash ในการวาดห้องเปล่าสำเร็จรูป

## 📋 ความต้องการ

- Python 3.8+
- Google API Key (Gemini) - **optional**
- Replicate API Token - **recommended** ⭐ (สร้างรูปคุณภาพสูง)
- ไฟล์ .env ที่มี `GOOGLE_API_KEY` และ `REPLICATE_API_TOKEN`

### 🎨 Image Generation APIs:
ระบบรองรับ 3 APIs พร้อม fallback อัตโนมัติ:
1. **Gemini 2.5 Flash** - เร็ว (5-10วินาที)
2. **Replicate (Stable Diffusion 3)** - คุณภาพสูง ⭐ ถูกกว่า
3. **Pollinations** - Free fallback

ดู `API_COMPARISON_GUIDE.md` สำหรับรายละเอียด

## 🚀 การเริ่มต้น

1. **ติดตั้ง Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **สร้างไฟล์ .env** (copy จาก .env.example)
   ```bash
   cp .env.example .env
   ```
   
   **หรือสร้างด้วยมือ:**
   ```
   # Google Gemini API (optional)
   GOOGLE_API_KEY=your_gemini_key_here
   
   # Replicate API (recommended) ⭐
   REPLICATE_API_TOKEN=your_replicate_token_here
   ```

3. **รัน Streamlit App**
   ```bash
   streamlit run app.py
   ```

4. **เปิด Browser**
   ```
   http://localhost:8501
   ```

## 🔑 วิธีการได้ API Keys

### 1. Google Gemini API (Optional)
```
1. ไปที่ https://aistudio.google.com/
2. คลิก "Create API Key"
3. Copy key ใส่ใน .env
```

### 2. Replicate API Token (Recommended) ⭐
```
1. ไปที่ https://replicate.com
2. Sign Up ด้วย GitHub
3. ไปที่ https://replicate.com/account/api-tokens
4. คลิก "Create Token"
5. Copy token ใส่ใน .env

💡 Free tier: 10 requests/month
💰 Paid: $0.01-0.15 ต่อรูป (ถูกกว่า Gemini!)
```

ดูรายละเอียดเพิ่มเติมใน:
- 📖 `REPLICATE_SETUP_GUIDE.md` - วิธี setup Replicate
- 📊 `API_COMPARISON_GUIDE.md` - เปรียบเทียบ APIs

## 📁 โครงสร้างไฟล์

```
AI-Interior-Room-Designer/
├── app.py                    # Streamlit main application
├── vision_utils.py          # Vision analysis utilities
├── prompt_utils.py          # Prompt building functions
├── image_gen_utils.py       # Image generation utilities
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (ต้องสร้างเอง)
└── README.md               # This file
```

## 🎨 การใช้งาน

1. **ขั้นตอนที่ 1** - เลือกประเภทห้อง สไตล์ และธีมสี
2. **ขั้นตอนที่ 2** - เลือกเฟอร์นิเจอร์ที่ต้องการ (สามารถเลือกหลายชิ้น)
3. **ขั้นตอนที่ 2.5** - 🆕 (ไม่บังคับ) อัพโหลดรูปตกแต่ง
   - อัพโหลดไฟล์ PNG/JPG
   - คลิก "✂️ ตัดพื้นหลังออก" → "🔄 ประมวลผล"
   - ระบบจะ auto-remove background ด้วย rembg AI
4. **ขั้นตอนที่ 3** - เพิ่มรายละเอียดเพิ่มเติมหากต้องการ
5. **ขั้นตอนที่ 4** - คลิกปุ่ม "🚀 สร้างห้องใหม่"
6. **ผลลัพธ์** - ดูห้องที่ AI สร้างให้
   - ถ้ามีตกแต่ง: ปรับตำแหน่ง X, Y และขนาด (scale)
   - คลิก "💾 ดาวน์โหลด" เพื่อบันทึก
   - คลิก "🔄 ออกแบบใหม่" เพื่อเริ่มใหม่
   - คลิก "✏️ เปลี่ยนตกแต่ง" เพื่อลองตกแต่งอื่น

## 🔧 Utilities

### vision_utils.py
- `analyze_room_style()` - วิเคราะห์สไตล์ห้องและให้คำแนะนำ

### prompt_utils.py
- `build_room_prompt()` - สร้าง Prompt ละเอียดสำหรับ AI
- `build_minimalist_prompt()` - สร้าง Prompt แบบสั้น

### image_gen_utils.py
- `generate_room_image()` - สร้างภาพห้องด้วย Gemini AI
- `get_fallback_image()` - Fallback image URL เมื่อ Gemini ล้ม
- `estimate_generation_time()` - ประมาณเวลาในการสร้าง

## 💡 Tips

- เลือกเฟอร์นิเจอร์ 3-7 ชิ้นเพื่อได้ผลลัพธ์ที่ดีที่สุด
- เพิ่มรายละเอียดเช่น "ต้องมีแสงสดใส" หรือ "ชอบสีเขียว"
- หากรูปไม่ออกมาดี ลองลดจำนวนเฟอร์นิเจอร์ลง
- **สำหรับตกแต่ง**: ยิ่งรูปมีพื้นหลังกว่างๆ ยิ่งตัดพื้นหลังได้ดี
- ลองปรับตำแหน่ง X, Y ต่างๆ เพื่อหาตำแหน่งที่ดูเหมาะสม

## 🔧 Background Removal

แอปใช้ **rembg** ซึ่งเป็น AI model ที่ตัดพื้นหลังจากรูป:

```
รูป input → rembg AI → รูป PNG transparent
         (มี background)  (ไม่มี background)
```

หลังจากตัดพื้นหลัง ระบบจะ overlay รูปลงในภาพห้องที่ AI สร้างขึ้น

### ตัวอย่างการใช้:
1. อัพโหลดรูปเก้าอี้ / โต๊ะ / โคมไฟ ฯลฯ
2. คลิก "✂️ ตัดพื้นหลังออก" 
3. คลิก "🔄 ประมวลผล"
4. สร้างห้องด้วย AI
5. ปรับตำแหน่งและขนาดในผลลัพธ์

## 📝 License

MIT License

## 🤝 Support

หากมีปัญหา ตรวจสอบ:
- API Key ถูกต้องหรือไม่
- ไฟล์ .env มีอยู่ในโฟลเดอร์หลักหรือไม่
- Internet connection เชื่อมต่อดีหรือไม่
