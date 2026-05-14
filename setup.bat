@echo off
REM 🚀 AI Room Designer - Quick Setup Script (Windows)
REM สคริปต์นี้ช่วยติดตั้ง dependencies ได้อย่างง่ายดาย

echo.
echo 🎨 AI Room Designer - Installation Script (Windows)
echo ====================================================
echo.

REM Check Python version
echo 1️⃣  ตรวจสอบเวอร์ชัน Python...
python --version
if errorlevel 1 (
    echo ❌ ไม่พบ Python! ต้องติดตั้ง Python 3.8 ขึ้นไป
    pause
    exit /b 1
)
echo    ✅ Python found
echo.

REM Install dependencies
echo 2️⃣  ติดตั้ง Dependencies...
call pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ ไม่สำเร็จในการติดตั้ง dependencies
    pause
    exit /b 1
)
echo    ✅ Dependencies installed
echo.

REM Create .env if not exists
echo 3️⃣  ตรวจสอบไฟล์ .env...
if not exist ".env" (
    echo    ไฟล์ .env ไม่พบ
    echo    📋 สร้างจาก .env.example...
    copy .env.example .env
    echo    ✅ สร้างไฟล์ .env เรียบร้อย
    echo.
    echo    ⚠️  กรุณาแก้ไข .env และเพิ่ม:
    echo       - GOOGLE_API_KEY (จาก aistudio.google.com)
    echo       - REPLICATE_API_TOKEN (จาก replicate.com/account/api-tokens)
    echo.
) else (
    echo    ✅ ไฟล์ .env พบแล้ว
)
echo.

REM Test imports
echo 4️⃣  ทดสอบ imports...
python -c "import streamlit; print('   ✅ Streamlit OK')" 2>nul || echo    ❌ Streamlit failed
python -c "import google.generativeai; print('   ✅ Google Generative AI OK')" 2>nul || echo    ⚠️  Google API not available
python -c "import replicate; print('   ✅ Replicate OK')" 2>nul || echo    ⚠️  Replicate not installed (optional)
python -c "from PIL import Image; print('   ✅ Pillow OK')" 2>nul || echo    ❌ Pillow failed
echo.

REM Summary
echo ====================================================
echo ✅ Setup เสร็จแล้ว!
echo.
echo 📝 Next Steps:
echo    1. แก้ไขไฟล์ .env
echo    2. รัน: streamlit run app.py
echo    3. เปิด http://localhost:8501
echo.
echo 📚 Documentation:
echo    - REPLICATE_SETUP_GUIDE.md (วิธี setup Replicate)
echo    - API_COMPARISON_GUIDE.md (เปรียบเทียบ APIs)
echo    - SHOPPING_FEATURE.md (ฟีเจอร์ซื้อสินค้า)
echo.
echo 🚀 Let's create beautiful rooms!
echo.
pause
