# MediaMTX Professional Client - Quick Start for GitHub

## 🎬 Installation & Quick Start

### Requirements
- Python 3.8+
- Windows/Linux/macOS

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate MediaMTX config
```bash
python generate_mediamtx_config.py
# Choose NVR type, enter IP and number of cameras
# Creates mediamtx.yml automatically
```

### 3. Run MediaMTX
```bash
mediamtx mediamtx.yml
# Download from: https://github.com/bluenviron/mediamtx/releases
```

### 4. Run the application
```bash
python professional_client.py
```

### 5. Import cameras
- File → Import from MediaMTX
- URL: http://127.0.0.1:9997
- Click Import
- **All cameras loaded!** ✅

## 📖 Documentation

- **README.md** - Overview and features
- **SETUP_GUIDE_RU.md** - Complete setup guide (Russian)
- **FAQ.md** - Common questions and solutions
- **ARCHITECTURE_NVR_MEDIAMTX.md** - System architecture

## 🎯 Key Features

✅ Support for 130+ cameras  
✅ Auto-import from MediaMTX  
✅ Professional dark theme  
✅ Multi-layout views (1-16 cameras)  
✅ Video recording & screenshots  
✅ Real-time editing (brightness/contrast)  
✅ PTZ controls  
✅ Event logging  
✅ Works with Hikvision, Dahua, Uniview  

## 🐛 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📜 License

MIT License - See [LICENSE](LICENSE)

## 📞 Support

- 📖 Read documentation first
- 🔍 Check FAQ.md
- 🐛 Report issues on GitHub
- 💬 Start a discussion

---

**Version:** 1.0.0  
**Status:** Production Ready ✅
