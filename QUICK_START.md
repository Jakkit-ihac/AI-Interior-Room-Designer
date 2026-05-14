# ⚡ Quick Start Guide (2 Minutes)

## 🚀 Start Your App in 2 Minutes

### Step 1: Get API Key (1 minute)
```
Visit: https://aistudio.google.com/
Click: "Create API Key"
Copy: Your free API key
```

### Step 2: Configure (30 seconds)
```bash
# Open .env file and add:
GOOGLE_API_KEY=your_api_key_here
```

### Step 3: Run (30 seconds)
```bash
streamlit run app.py
```

### Step 4: Design! 
```
Your app opens at http://localhost:8501
Start creating beautiful rooms! 🎨
```

---

## 🎯 What You Can Do

### Create Rooms:
1. Select room type (Living Room, Bedroom, etc.)
2. Choose style (Modern, Japandi, etc.)
3. Pick color theme
4. Click "🚀 สร้างห้อง"

### Add Decorations:
1. Upload decoration image
2. Remove background (optional)
3. Adjust position & size
4. See instant preview

### Shop Products:
1. See detected furniture
2. Get product suggestions
3. Add to cart
4. Checkout

---

## 🔑 API Keys Guide

### Option A: Free (Gemini Only)
```
✅ Always works
✅ Fast (5-10 seconds)
✅ Free tier: 60 requests/minute
⏳ Good quality images

Get: https://aistudio.google.com/
```

### Option B: Better Quality (+ Replicate)
```
✅ Replicate gives better images
✅ Automatic fallback system
✅ More reliable

Get Replicate: https://replicate.com/account/api-tokens
Add to .env: REPLICATE_API_TOKEN=r8_xxxxx
```

### Option C: Fully Free (Pollinations)
```
✅ Completely free
✅ Always works
✅ No API key needed
⏳ Slower (10-30 seconds)

Uses automatically if others fail
```

---

## 📁 File Structure

```
AI-Interior-Room-Designer/
├── app.py                    ← Run this!
├── requirements.txt          ← Dependencies
├── .env                      ← Your API keys
├── product_shopping_utils.py ← Shopping logic
├── README.md                 ← Full documentation
├── PROJECT_STATUS.md         ← Current status
└── docs/                     ← Guides & examples
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Module not found" | Run: `pip install -r requirements.txt` |
| "API key not found" | Check .env file has your key |
| "App won't start" | Check Python 3.8+: `python --version` |
| "Slow generation" | Use Replicate API for faster |
| "Poor image quality" | Get Replicate API token |

---

## 🎨 Tips for Best Results

### Room Generation:
- Be specific with descriptions
- Choose consistent style + color
- Use modern/natural room types

### Decorations:
- Use PNG with transparency
- PNG works best for removal
- JPG also works but manual trim needed

### Shopping:
- More detected items = more choices
- Budget-friendly categories work well
- Multiple stores for best prices

---

## 📊 API Comparison (Quick)

| | Gemini | Replicate | Pollinations |
|---|--------|-----------|--------------|
| Speed | ⚡⚡⚡⚡ (5s) | ⚡⚡⚡ (30s) | ⚡⚡ (15s) |
| Quality | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Cost | $0.05 | $0.01-0.15 | FREE |
| Quota | 60/min | Unlimited | Unlimited |
| Key Needed | ✅ Yes | ✅ Yes | ❌ No |

---

## 🎯 Your First 5 Minutes

```
0:00 - Read this guide
1:00 - Get Gemini API key
1:30 - Add to .env file
2:00 - Run: streamlit run app.py
2:30 - App opens in browser
3:00 - Create your first room
4:00 - Upload decoration
5:00 - View results & shop!
```

---

## ✨ Features at a Glance

```
✅ AI Room Design (3 API support)
✅ Product Detection (Automatic)
✅ Background Removal (Easy)
✅ Shopping Cart (Real-time)
✅ Budget Calculator (Instant)
✅ 30+ Products (Ready)
✅ Thai Language (Complete)
✅ Professional UI (Beautiful)
```

---

## 🚀 Next Steps

1. **Right Now:** Get API key → Run app → Design room
2. **Tomorrow:** Try Replicate API → Get better images
3. **This Week:** Integrate real shopping links
4. **This Month:** Deploy online → Share with users

---

## 💡 Pro Tips

- Restart app if you change .env
- Use Firefox/Chrome for best experience
- Keep decorations under 5MB
- PNG = better results than JPG
- Longer descriptions = better rooms

---

## 📞 Quick Reference

**Get Help:**
- Check README.md for full docs
- Read REPLICATE_COMPLETE_GUIDE.md for setup
- See SHOPPING_FEATURE.md for shopping details

**Get Keys:**
- Gemini: https://aistudio.google.com/
- Replicate: https://replicate.com/account/api-tokens

**Run App:**
```bash
streamlit run app.py
```

---

## 🎉 Ready?

**Start creating NOW:**
```bash
streamlit run app.py
```

Your room designer is ready to go! 🛋️✨

---

*Quick Start Guide v1.0*  
*Updated: May 12, 2026*
