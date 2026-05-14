#!/bin/bash
# 🚀 AI Room Designer - Quick Setup Script
# สคริปต์นี้ช่วยติดตั้ง dependencies ได้อย่างง่ายดาย

echo "🎨 AI Room Designer - Installation Script"
echo "=========================================="
echo ""

# Check Python version
echo "1️⃣ ตรวจสอบเวอร์ชัน Python..."
python_version=$(python --version 2>&1)
echo "   $python_version"

if ! python -c 'import sys; exit(0 if sys.version_info >= (3,8) else 1)'; then
    echo "❌ ต้องมี Python 3.8 ขึ้นไป!"
    exit 1
fi
echo "   ✅ Python version OK"
echo ""

# Install dependencies
echo "2️⃣ ติดตั้ง Dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed"
else
    echo "   ❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Create .env if not exists
echo "3️⃣ ตรวจสอบไฟล์ .env..."
if [ ! -f ".env" ]; then
    echo "   ไฟล์ .env ไม่พบ"
    echo "   📋 สร้างจาก .env.example..."
    cp .env.example .env
    echo "   ✅ สร้างไฟล์ .env เรียบร้อย"
    echo ""
    echo "   ⚠️  กรุณาแก้ไข .env และเพิ่ม:"
    echo "      - GOOGLE_API_KEY (จาก aistudio.google.com)"
    echo "      - REPLICATE_API_TOKEN (จาก replicate.com/account/api-tokens)"
    echo ""
else
    echo "   ✅ ไฟล์ .env พบแล้ว"
fi
echo ""

# Test imports
echo "4️⃣ ทดสอบ imports..."
python -c "import streamlit; print('   ✅ Streamlit OK')" 2>/dev/null || echo "   ❌ Streamlit failed"
python -c "import google.generativeai; print('   ✅ Google Generative AI OK')" 2>/dev/null || echo "   ⚠️  Google API not available"
python -c "import replicate; print('   ✅ Replicate OK')" 2>/dev/null || echo "   ⚠️  Replicate not installed (optional)"
python -c "from PIL import Image; print('   ✅ Pillow OK')" 2>/dev/null || echo "   ❌ Pillow failed"
echo ""

# Summary
echo "=========================================="
echo "✅ Setup เสร็จแล้ว!"
echo ""
echo "📝 Next Steps:"
echo "   1. แก้ไขไฟล์ .env"
echo "   2. รัน: streamlit run app.py"
echo "   3. เปิด http://localhost:8501"
echo ""
echo "📚 Documentation:"
echo "   - REPLICATE_SETUP_GUIDE.md (วิธี setup Replicate)"
echo "   - API_COMPARISON_GUIDE.md (เปรียบเทียบ APIs)"
echo "   - SHOPPING_FEATURE.md (ฟีเจอร์ซื้อสินค้า)"
echo ""
echo "🚀 Let's create beautiful rooms!"
