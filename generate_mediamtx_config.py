#!/usr/bin/env python3
"""
Генератор конфигурации MediaMTX для 130+ камер
Создает mediamtx.yml с автоматическим подключением к NVR
"""

import os
import sys

def generate_hikvision_config(output_file="mediamtx.yml", nvr_ip="192.168.1.100", num_cameras=130):
    """Генерирует конфиг для Hikvision NVR (каналы 101-230)"""
    print(f"📝 Генерирую конфиг для Hikvision {num_cameras} камер...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# MediaMTX Configuration for Hikvision NVR\n")
        f.write(f"# Generated for {num_cameras} cameras\n")
        f.write(f"# NVR IP: {nvr_ip}\n\n")
        f.write("paths:\n")
        
        for i in range(1, num_cameras + 1):
            cam_name = f"camera_{i:03d}"
            channel = 100 + i
            
            f.write(f"""  {cam_name}:
    source: rtsp://{nvr_ip}:554/Streaming/Channels/{channel}
    rtspTransport: tcp
    readBufferCount: 100
    readTimeout: 10s
    writeTimeout: 10s

""")
    
    print(f"✓ Создан конфиг: {output_file}")
    print(f"✓ Камер: {num_cameras}")
    print(f"✓ Каналы: 101-{100 + num_cameras}")
    return output_file

def generate_dahua_config(output_file="mediamtx.yml", nvr_ip="192.168.1.100", num_cameras=130):
    """Генерирует конфиг для Dahua NVR (потоки 1-N)"""
    print(f"📝 Генерирую конфиг для Dahua {num_cameras} камер...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# MediaMTX Configuration for Dahua NVR\n")
        f.write(f"# Generated for {num_cameras} cameras\n")
        f.write(f"# NVR IP: {nvr_ip}\n\n")
        f.write("paths:\n")
        
        for i in range(1, num_cameras + 1):
            cam_name = f"camera_{i:03d}"
            
            f.write(f"""  {cam_name}:
    source: rtsp://{nvr_ip}:554/stream/{i}
    rtspTransport: tcp
    readBufferCount: 100
    readTimeout: 10s
    writeTimeout: 10s

""")
    
    print(f"✓ Создан конфиг: {output_file}")
    print(f"✓ Камер: {num_cameras}")
    print(f"✓ Потоки: 1-{num_cameras}")
    return output_file

def generate_uniview_config(output_file="mediamtx.yml", nvr_ip="192.168.1.100", num_cameras=130):
    """Генерирует конфиг для Uniview NVR (каналы ch00-chNN)"""
    print(f"📝 Генерирую конфиг для Uniview {num_cameras} камер...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# MediaMTX Configuration for Uniview NVR\n")
        f.write(f"# Generated for {num_cameras} cameras\n")
        f.write(f"# NVR IP: {nvr_ip}\n\n")
        f.write("paths:\n")
        
        for i in range(0, num_cameras):
            cam_name = f"camera_{i+1:03d}"
            channel = str(i).zfill(2)
            
            f.write(f"""  {cam_name}:
    source: rtsp://{nvr_ip}:554/live/ch{channel}
    rtspTransport: tcp
    readBufferCount: 100
    readTimeout: 10s
    writeTimeout: 10s

""")
    
    print(f"✓ Создан конфиг: {output_file}")
    print(f"✓ Камер: {num_cameras}")
    print(f"✓ Каналы: ch00-ch{num_cameras-1:02d}")
    return output_file

def generate_cameras_json(output_file="cameras.json", num_cameras=130, group_name="Imported", base_url="rtsp://127.0.0.1:8554"):
    """Генерирует cameras.json для импорта в приложение"""
    print(f"📝 Генерирую cameras.json для {num_cameras} камер...")
    
    import json
    
    cameras = []
    for i in range(1, num_cameras + 1):
        cameras.append({
            "name": f"Camera {i:03d}",
            "url": f"{base_url}/camera_{i:03d}",
            "group": group_name,
            "source": "mediamtx"
        })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cameras, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Создан файл: {output_file}")
    print(f"✓ Камер: {num_cameras}")
    return output_file

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║           MediaMTX Configuration Generator                     ║
║        For Large-Scale NVR Deployments (100+ cameras)         ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    # Determine NVR type
    print("\n🔧 Выберите тип NVR:")
    print("  1 - Hikvision (каналы 101-230)")
    print("  2 - Dahua (потоки 1-N)")
    print("  3 - Uniview (каналы ch00-chNN)")
    print("  4 - Custom (другой)")
    
    nvr_type = input("\nВыбор (1-4): ").strip()
    
    # Get NVR IP
    nvr_ip = input("IP адрес NVR (по умолчанию 192.168.1.100): ").strip()
    if not nvr_ip:
        nvr_ip = "192.168.1.100"
    
    # Get number of cameras
    num_str = input("Количество камер (по умолчанию 130): ").strip()
    try:
        num_cameras = int(num_str) if num_str else 130
    except ValueError:
        num_cameras = 130
    
    # Generate config
    print("\n" + "="*60)
    
    if nvr_type == "1":
        generate_hikvision_config(nvr_ip=nvr_ip, num_cameras=num_cameras)
    elif nvr_type == "2":
        generate_dahua_config(nvr_ip=nvr_ip, num_cameras=num_cameras)
    elif nvr_type == "3":
        generate_uniview_config(nvr_ip=nvr_ip, num_cameras=num_cameras)
    else:
        print("❌ Неподдерживаемый тип")
        return
    
    # Generate cameras.json
    generate_cameras_json(num_cameras=num_cameras)
    
    print("\n" + "="*60)
    print("""
✅ Конфигурация готова!

📋 Что дальше:

1. Переместите mediamtx.yml в папку MediaMTX
2. Запустите MediaMTX:
   mediamtx mediamtx.yml

3. Проверьте в браузере:
   http://127.0.0.1:9997/list

4. В приложении импортируйте:
   File → Import from MediaMTX

5. Камеры появятся в приложении!

📝 Советы:
  • Сохраните этот скрипт для переиспользования
  • Отредактируйте cameras.json для лучших названий
  • Используйте группы для организации камер
  • Проверьте доступность первой камеры в VLC

🔗 Полезные ссылки:
  • MediaMTX: https://github.com/bluenviron/mediamtx
  • Документация: https://mediamtx.readthedocs.io

Вопросы? Обратитесь к документации!
""")

if __name__ == "__main__":
    main()
