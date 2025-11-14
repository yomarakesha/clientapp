# 📚 РЕСУРСЫ И ПОЛЕЗНЫЕ ССЫЛКИ

## 🌍 Официальные ресурсы

### MediaMTX
- **Официальный сайт:** https://github.com/bluenviron/mediamtx
- **Документация:** https://mediamtx.readthedocs.io
- **Релизы:** https://github.com/bluenviron/mediamtx/releases
- **Issues:** https://github.com/bluenviron/mediamtx/issues
- **Discussions:** https://github.com/bluenviron/mediamtx/discussions

### Python и PyQt5
- **Python:** https://www.python.org
- **PyQt5 Документация:** https://www.riverbankcomputing.com/static/Docs/PyQt5/
- **PyQt5 Tutorial:** https://www.tutorialspoint.com/pyqt5/

### OpenCV
- **Официальный сайт:** https://opencv.org
- **Документация:** https://docs.opencv.org
- **Python bindings:** https://pypi.org/project/opencv-python/

---

## 💻 Скачивание MediaMTX

### Windows
1. Перейти: https://github.com/bluenviron/mediamtx/releases
2. Скачать: `mediamtx_windows_amd64.zip`
3. Распаковать в папку (например: `C:\mediamtx`)

### Linux
```bash
mkdir /opt/mediamtx && cd /opt/mediamtx
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_linux_amd64.tar.gz
tar -xzf mediamtx_linux_amd64.tar.gz
chmod +x mediamtx
```

### macOS
```bash
mkdir ~/mediamtx && cd ~/mediamtx
wget https://github.com/bluenviron/mediamtx/releases/download/v1.5.0/mediamtx_darwin_amd64.tar.gz
tar -xzf mediamtx_darwin_amd64.tar.gz
chmod +x mediamtx
```

---

## 📖 Туториалы и обучение

### MediaMTX
- [YouTube: MediaMTX Setup](https://www.youtube.com/results?search_query=mediamtx+tutorial)
- [YouTube: RTSP Server](https://www.youtube.com/results?search_query=rtsp+server+setup)
- [Habr: Статьи про MediaMTX](https://habr.com/ru/search/?q=mediamtx)

### RTSP Протокол
- **RFC 2326:** https://tools.ietf.org/html/rfc2326 (официальный стандарт)
- [RTSP для начинающих](https://www.wowza.com/en/resources/streaming/rtsp)
- [Понимание RTSP](https://www.geeksforgeeks.org/what-is-rtsp/)

### Python для видео
- [OpenCV Tutorial](https://opencv-python-tutroals.readthedocs.io/)
- [PyQt5 Video](https://www.learnpyqt.com/)

---

## 🛠️ Инструменты и утилиты

### Для проверки RTSP потоков
- **VLC Media Player** - https://www.videolan.org/vlc/
  (Меню → Открыть сетевой поток)

- **FFmpeg** - https://ffmpeg.org/download.html
  ```bash
  ffmpeg -i "rtsp://camera:554/stream" -t 5 -f null -
  ```

- **FFplay** (входит в FFmpeg)
  ```bash
  ffplay "rtsp://camera:554/stream"
  ```

### Для работы с конфигами
- **Visual Studio Code** - https://code.visualstudio.com/
- **Notepad++** - https://notepad-plus-plus.org/
- **Sublime Text** - https://www.sublimetext.com/

### Для мониторинга сети
- **Wireshark** - https://www.wireshark.org/ (анализ трафика)
- **TCPView** - https://learn.microsoft.com/en-us/sysinternals/downloads/tcpview (сетевые соединения)

---

## 📚 Документация NVR

### Hikvision
- **Официальный сайт:** https://www.hikvision.com
- **Поддержка:** https://support.hikvision.com
- **RTSP Path:** `/Streaming/Channels/101` (для канала 1)
- **Порт:** 554

### Dahua
- **Официальный сайт:** https://www.dahuasecurity.com
- **Поддержка:** https://support.dahuasecurity.com
- **RTSP Path:** `/stream/1` (для потока 1)
- **Порт:** 554

### Uniview
- **Официальный сайт:** https://www.uniview.com
- **RTSP Path:** `/live/ch00` (для канала 1)
- **Порт:** 554

### Axis
- **Официальный сайт:** https://www.axis.com
- **RTSP Path:** `/axis-media/media.amp?camera=1`
- **Порт:** 554

---

## 🔍 Поиск решений проблем

### Общие вопросы
- [Stack Overflow - RTSP](https://stackoverflow.com/questions/tagged/rtsp)
- [Stack Overflow - OpenCV](https://stackoverflow.com/questions/tagged/opencv)
- [Stack Overflow - PyQt5](https://stackoverflow.com/questions/tagged/pyqt5)

### Форумы
- [Python Discord](https://discord.gg/python)
- [OpenCV Forum](https://answers.opencv.org/)
- [PyQt Forum](https://www.riverbankcomputing.com/pipermail/pyqt/)

### GitHub Issues
- [MediaMTX Issues](https://github.com/bluenviron/mediamtx/issues)
- [OpenCV Issues](https://github.com/opencv/opencv/issues)

---

## 📊 Примеры конфигов

### Конфиг MediaMTX для разных NVR

**Hikvision (mediamtx.yml)**
```yaml
paths:
  camera_001:
    source: rtsp://192.168.1.100:554/Streaming/Channels/101
  camera_002:
    source: rtsp://192.168.1.100:554/Streaming/Channels/102
```

**Dahua (mediamtx.yml)**
```yaml
paths:
  camera_001:
    source: rtsp://192.168.1.100:554/stream/1
  camera_002:
    source: rtsp://192.168.1.100:554/stream/2
```

---

## 💾 Примеры JSON конфигов

**cameras.json (Hikvision)**
```json
[
  {
    "name": "Вход",
    "url": "rtsp://127.0.0.1:8554/camera_001",
    "group": "Входы"
  }
]
```

**config.json**
```json
{
  "recording_dir": "recordings",
  "fps": 20,
  "bitrate": "5000k",
  "mediamtx_url": "http://127.0.0.1:9997"
}
```

---

## 🎓 Обучающие курсы

### Python
- [Python для начинающих](https://www.python.org/about/gettingstarted/)
- [Real Python](https://realpython.com/)
- [DataCamp Python](https://www.datacamp.com/courses/intro-to-python-for-data-science)

### PyQt5
- [Learn PyQt](https://www.learnpyqt.com/)
- [Real Python: PyQt5](https://realpython.com/search?q=pyqt5)
- [Udemy: PyQt5 Courses](https://www.udemy.com/search/?q=PyQt5)

### Видеопотоки
- [Coursera: Video Streaming](https://www.coursera.org/)
- [Udemy: RTSP/Video](https://www.udemy.com/search/?q=rtsp+video)

---

## 🔧 Инструменты разработки

### IDE
- **VS Code** - https://code.visualstudio.com/
- **PyCharm** - https://www.jetbrains.com/pycharm/
- **Thonny** - https://thonny.org/ (для начинающих)

### Утилиты
- **Git** - https://git-scm.com/ (контроль версий)
- **Virtual Environment** - встроено в Python

---

## 📞 Контакты и поддержка

### GitHub
- **MediaMTX:** https://github.com/bluenviron/mediamtx
- **Issues:** Создавайте issues если что-то не работает

### Сообщества
- **Reddit: r/HomeServer**
- **Reddit: r/OpenSourceAI**
- **Discord: Home Automation**

---

## 🎯 Дополнительные материалы

### Статьи
- [Habr: MediaMTX](https://habr.com/ru/search/?q=mediamtx)
- [Habr: RTSP](https://habr.com/ru/search/?q=rtsp)
- [Habr: OpenCV](https://habr.com/ru/search/?q=opencv)
- [Habr: PyQt5](https://habr.com/ru/search/?q=pyqt5)

### Видео
- YouTube: "MediaMTX tutorial"
- YouTube: "RTSP server setup"
- YouTube: "Python video streaming"
- YouTube: "PyQt5 GUI tutorial"

### Книги
- "Mastering OpenCV" - Gary Bradski, Adrian Kaehler
- "PyQt5 Application Development" - B.M. Harwani
- "Learning Python" - Mark Lutz

---

## 📋 Чек-лист ресурсов

При возникновении проблем проверьте:

- [ ] Документация MediaMTX читана?
- [ ] RTSP путь правильный?
- [ ] Порт 554 открыт?
- [ ] NVR доступна по сети?
- [ ] VLC может воспроизвести поток?
- [ ] MediaMTX запущен и работает?
- [ ] Приложение может подключиться к MediaMTX?
- [ ] Логи event.json показывают что происходит?
- [ ] FAQ.md прочитан полностью?
- [ ] SETUP_GUIDE_RU.md следован точно?

---

## 🌐 Альтернативные решения

Если что-то не подходит, есть альтернативы:

### Серверы переранслирования
- **Wowza** - https://www.wowza.com (коммерческое)
- **Nimble** - https://www.wmspanel.com/nimble (коммерческое)
- **FFmpeg** - https://ffmpeg.org (open-source)
- **GStreamer** - https://gstreamer.freedesktop.org (open-source)

### Клиенты видеонаблюдения
- **IVMS-4200** - Hikvision (официальное)
- **SmartPSS** - Dahua (официальное)
- **VLC** - https://www.videolan.org (универсальный)
- **MPV** - https://mpv.io (легковесный)

---

## 💡 Советы

1. **Начните с малого**
   - Установите 1 камеру
   - Убедитесь что работает
   - Затем добавляйте остальные

2. **Используйте TCP**
   - Более надёжен чем UDP
   - Добавьте в mediamtx.yml: `rtspTransport: tcp`

3. **Мониторьте логи**
   - MediaMTX выводит информацию в консоль
   - events.json хранит логи приложения

4. **Тестируйте в VLC**
   - Перед добавлением в приложение
   - Убедитесь что поток работает

5. **Сохраняйте конфиги**
   - Регулярно делайте резервные копии
   - Используйте Git для версионирования

---

## 🚀 Полезные команды

### Проверка доступности RTSP
```bash
ffmpeg -i "rtsp://camera:554/stream" -t 5 -f null -
```

### Проверка открытого порта
```bash
# Linux/macOS:
nc -zv camera 554

# Windows:
Test-NetConnection -ComputerName camera -Port 554
```

### Проверка DNS
```bash
nslookup camera.local
```

### Проверка соединения
```bash
ping camera
```

---

## 📞 Решение конкретных проблем

### "Не могу подключиться к NVR"
1. Проверьте IP адрес: `ping <ip>`
2. Проверьте порт: `nc -zv <ip> 554`
3. Проверьте пользователя/пароль в NVR
4. Проверьте RTSP путь для вашего NVR

### "Видео подтормаживает"
1. Используйте TCP вместо UDP
2. Снизьте разрешение на NVR
3. Увеличьте буфер в MediaMTX
4. Проверьте пропускную способность сети

### "Потоки постоянно разрываются"
1. Включите TCP в MediaMTX
2. Увеличьте timeout
3. Перезагрузите NVR
4. Проверьте стабильность сети

---

**Версия:** 1.0  
**Дата обновления:** 14 ноября 2025  
**Статус:** Production Ready ✅
