# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-14

### Added
- Initial release of MediaMTX Professional Client
- Support for 130+ cameras
- Auto-import from MediaMTX API
- Professional dark theme UI (IVMS-4200 style)
- Multi-view layouts (1x1, 2x2, 3x3, 4x4)
- Camera management (add, remove, organize)
- Video recording (MP4 format)
- Screenshot functionality (PNG format)
- Real-time video editing (brightness, contrast)
- PTZ controls dialog
- Event logging system
- Full support for Hikvision, Dahua, Uniview NVR
- Complete Russian documentation
- MediaMTX config generator script
- Import/Export functionality (JSON, CSV)
- Status indicators and monitoring
- FPS and resolution monitoring

### Features
- TreeView camera organization by groups
- Search functionality for 130+ cameras
- Lazy loading of video streams
- Caching of camera metadata
- Context menus for quick actions
- Settings management dialog
- Event log viewer
- Archive player for video playback
- Statistics display

### Documentation
- README.md - Project overview
- SETUP_GUIDE_RU.md - Step-by-step setup guide
- ARCHITECTURE_NVR_MEDIAMTX.md - System architecture
- FAQ.md - Frequently asked questions
- README_PROFESSIONAL.md - Detailed feature documentation
- RESOURCES.md - Links and references
- FILES_DESCRIPTION.txt - File structure
- PROJECT_REPORT.txt - Project report

### Technical
- Python 3.8+ support
- Cross-platform (Windows, Linux, macOS)
- PyQt5 GUI framework
- OpenCV video processing
- Requests library for API integration
- JSON configuration format
- Event-based logging

---

## [Unreleased]

### Planned for future releases
- [ ] Web interface
- [ ] Mobile application
- [ ] Motion detection
- [ ] Face recognition
- [ ] Multi-server management
- [ ] Cloud backup integration
- [ ] Alert and notification system
- [ ] Advanced video analytics
- [ ] Email notifications
- [ ] Integration with security systems

---

## Version History

### How to upgrade
- Download latest release
- Backup your cameras.json and config.json
- Replace professional_client.py
- Run with same configuration

### Compatibility
- v1.0.0 → All versions compatible
- Configuration files are backward compatible

---

## Support

For issues, questions, or suggestions:
1. Check FAQ.md
2. Search existing issues on GitHub
3. Create new issue with detailed description

---

**Latest Version:** 1.0.0  
**Release Date:** November 14, 2025  
**Status:** Stable
