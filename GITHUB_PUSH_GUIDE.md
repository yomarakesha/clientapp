# 🚀 ИНСТРУКЦИЯ: Первый push на GitHub

## ✅ ШАГ 1: Создать репозиторий на GitHub

1. Откройте: https://github.com/new
2. Заполните:
   - **Repository name:** `mediamtx-professional-client`
   - **Description:** `Professional CCTV management client for 130+ cameras via MediaMTX`
   - **Public** (публичный)
   - Не инициализируйте README (уже есть)
3. Нажмите **Create repository**

---

## ✅ ШАГ 2: Инициализировать Git локально

Откройте PowerShell в папке проекта и выполните:

```bash
cd "C:\Users\Windows 11 Pro\Desktop\clientapp"

# Инициализировать git
git init

# Добавить файлы
git add .

# Первый коммит
git commit -m "Initial commit: Professional MediaMTX client v1.0

- Support for 130+ cameras
- Auto-import from MediaMTX API
- Professional dark theme UI
- Multi-view layouts (1x1, 2x2, 3x3, 4x4)
- Video recording and screenshots
- Real-time video editing
- Event logging system
- Full documentation
- MediaMTX config generator"

# Переименовать ветку в main (GitHub стандарт)
git branch -M main

# Добавить удаленный репозиторий
git remote add origin https://github.com/YOUR-USERNAME/mediamtx-professional-client.git

# Первый push
git push -u origin main
```

**Замените `YOUR-USERNAME` на ваше имя пользователя GitHub!**

---

## 🔐 ШАГ 3: Аутентификация (если спросит пароль)

### Вариант A: Personal Access Token (рекомендуется)

1. GitHub → Settings → Developer settings → Personal access tokens
2. Click **Generate new token**
3. Выберите scopes: `repo`, `workflow`
4. Copy token
5. В PowerShell при запросе пароля вставьте token

### Вариант B: SSH Key (продвинуто)

```bash
# Генерировать SSH ключ
ssh-keygen -t ed25519 -C "your-email@example.com"

# Добавить на GitHub
# Settings → SSH and GPG keys → New SSH key
# Вставьте содержимое ~/.ssh/id_ed25519.pub

# Использовать SSH вместо HTTPS
git remote set-url origin git@github.com:YOUR-USERNAME/mediamtx-professional-client.git
```

---

## ✅ ШАГ 4: Проверить что push прошел

Откройте: `https://github.com/YOUR-USERNAME/mediamtx-professional-client`

Должны видеть:
- ✓ Все файлы
- ✓ README.md в основной области
- ✓ Коммиты в истории

---

## 📝 СТРУКТУРА РЕПОЗИТОРИЯ (проверьте что есть):

```
mediamtx-professional-client/
├── professional_client.py          ✓ Основное приложение
├── generate_mediamtx_config.py    ✓ Генератор конфига
├── requirements.txt                ✓ Зависимости
├── LICENSE                         ✓ MIT License
├── .gitignore                      ✓ Git ignore
├── README.md                       ✓ Главный README
├── QUICKSTART.md                   ✓ Быстрый старт
├── SETUP_GUIDE_RU.md              ✓ Инструкция (русский)
├── ARCHITECTURE_NVR_MEDIAMTX.md   ✓ Архитектура
├── README_PROFESSIONAL.md         ✓ Функции подробно
├── FAQ.md                         ✓ Вопросы-ответы
├── RESOURCES.md                   ✓ Ресурсы и ссылки
├── CONTRIBUTING.md                ✓ Для контрибьютеров
├── CHANGELOG.md                   ✓ История изменений
└── recordings/                    ✓ Папка видео (пустая)
```

---

## 🔄 ПОСЛЕ ПЕРВОГО PUSH: Обновления

Когда будете обновлять код:

```bash
# Проверить изменения
git status

# Добавить изменения
git add .

# Коммит
git commit -m "Feature: description of changes"

# Push
git push
```

---

## 📊 ХОРОШИЕ ПРАКТИКИ ДЛЯ GIT

### Коммиты

✅ **Хорошо:**
```
git commit -m "Add: PTZ controls for camera management"
git commit -m "Fix: Memory leak in video thread"
git commit -m "Update: Documentation for v1.0"
git commit -m "Refactor: Reorganize code structure"
```

❌ **Плохо:**
```
git commit -m "update"
git commit -m "fix bug"
git commit -m "asdf"
```

### Коммит сообщения

Начинайте с:
- **Add:** новая функция
- **Fix:** исправление ошибки
- **Update:** обновление документации
- **Refactor:** переделка кода
- **Remove:** удаление
- **Improve:** улучшение производительности

---

## 🏷️ ТЕГИ (версии)

После стабильного релиза:

```bash
# Создать тег
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push тег на GitHub
git push origin v1.0.0

# Или все теги сразу
git push origin --tags
```

---

## 📋 ВЕТКИ (для больших изменений)

```bash
# Создать ветку для новой функции
git checkout -b feature/new-feature

# Работайте в этой ветке
git add .
git commit -m "Add: new feature"

# Push ветки
git push origin feature/new-feature

# На GitHub: Create Pull Request
# После review - merge в main
```

---

## 🚀 GITHUB ACTIONS (CI/CD) - Опционально

Создайте файл `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python -m pytest
```

---

## 📚 ДОБАВЛЯЕМ BADGE В README

В начало README.md добавьте:

```markdown
![GitHub release](https://img.shields.io/github/v/release/YOUR-USERNAME/mediamtx-professional-client)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen)
```

---

## 🎯 ИТОГОВЫЙ ЧЕКЛИСТ

- [ ] Создали репозиторий на GitHub
- [ ] Git инициализирован локально
- [ ] Файлы добавлены (git add .)
- [ ] Первый коммит (git commit)
- [ ] Ветка переименована в main
- [ ] Remote добавлен (git remote add origin)
- [ ] Push выполнен (git push)
- [ ] Проверили на GitHub что всё загрузилось
- [ ] README видно на главной странице
- [ ] Можно скачать репозиторий через git clone

---

## 🆘 ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК

### "fatal: Not a git repository"
```bash
git init
```

### "Authentication failed"
- Используйте Personal Access Token вместо пароля
- Или настройте SSH

### "rejected – non-fast-forward"
```bash
git pull origin main
git push origin main
```

### "Хочу переделать последний коммит"
```bash
git add .
git commit --amend -m "New message"
git push -f origin main  # Осторожно - перезаписывает историю!
```

---

## 📖 ПОЛЕЗНЫЕ КОМАНДЫ

```bash
# Проверить статус
git status

# Просмотреть историю
git log

# Просмотреть коммит подробно
git show COMMIT_HASH

# Откатить изменения
git reset --hard HEAD

# Клонировать репозиторий
git clone https://github.com/USER/repo.git

# Выгрузить конкретный файл
git checkout origin/main -- path/to/file

# Синхронизировать с GitHub
git pull origin main
```

---

## 🎉 ГОТОВО!

Поздравляем! Ваш первый GitHub репозиторий готов! 🚀

**Дальше:**
1. Поделитесь ссылкой
2. Ждите feedback
3. Добавляйте новые функции
4. Развивайте проект!

---

**Need help?** 
- GitHub Docs: https://docs.github.com
- Git Tutorial: https://git-scm.com/book/en/v2
