# My Own Browser - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage Guide](#usage)
5. [Shortcut Keys](#shortcuts)
6. [Advanced Customization](#customization)
7. [Troubleshooting](#troubleshooting)
8. [FAQs](#faqs)
9. [Developer Information](#developer)

---

## 1. Overview <a name="overview"></a>
"My Own Browser" is a modern, customizable web browser built with Python and PyQt5. Designed for privacy and efficiency, it combines essential browsing features with advanced customization options.

<table>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/4832d7e7-dce8-45d5-9e9f-a4a465376d75" alt="Screenshot 1" width="500">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/efb87f5e-a5eb-4838-9ca5-93947a9226e9" alt="Screenshot 2" width="500">
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/aeabe256-e802-4e50-a4dc-66254530e70a" alt="Screenshot 3" width="500">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/c00c1762-c73c-48c6-9775-5ae8dced094b" alt="Screenshot 4" width="500">
    </td>
  </tr>
</table>

---

## 2. Features <a name="features"></a>
### Core Functionality
- **Tabbed Browsing**: Vertical tab arrangement with hover previews
- **Ad Blocking**: Built-in EasyList integration with manual updates
- **Dual Themes**: Light/Dark mode switching
- **Privacy Focus**: No persistent cookies or cache
- **Custom Search**: Supports Google, DuckDuckGo, Bing, Yahoo

### Advanced Features![Leonardo_Phoenix_10_Logo_ConceptOverall_ShapeStart_with_a_circ_2-removebg-preview](https://github.com/user-attachments/assets/5ff37885-4fdc-4d2b-a72e-995a5fd36184)

- GitHub Profile integration (Developer quick-access)
- Download manager with progress tracking
- Bookmark and History persistence
- SSL/TLS error bypass
- Content Security Policy filtering
- Customizable keyboard shortcuts

---

## 3. Installation <a name="installation"></a>
### Requirements
- Python 3.7+
- 500MB Disk Space
- Modern GPU (WebGL acceleration)

### Installation Steps
```bash
# Create virtual environment
python -m venv browser-env

# Activate environment
source browser-env/bin/activate  # Linux/MacOS
browser-env\Scripts\activate  # Windows

# Install dependencies
pip install PyQt5 PyQtWebEngine requests
```

---

## 4. Usage Guide <a name="usage"></a>
### Basic Navigation
1. **Address Bar**
   - Enter URLs directly
   - Search using: `[keyword] [search terms]`
   - Example: `g python tutorial` (Google search)

2. **Tab Management**
   - Right-click tabs for context menu
   - Drag tabs to reorder

3. **Dockable Panels**
   - History (Left)
   - Bookmarks (Right)
   - Downloads (Bottom)

### Advanced Usage
- **Force Dark Mode**: Edit `DARK_STYLE` in code
- **Custom Blocklists**: Replace `blocklist.txt`
- **GitHub Access**: Menu ➔ My GitHub

---

## 5. Shortcut Keys <a name="shortcuts"></a>
| Shortcut            | Action                          | Context       |
|---------------------|---------------------------------|---------------|
| `Ctrl + T`          | New Tab                         | Global        |
| `Ctrl + W`          | Close Tab                       | Tab           |
| `Ctrl + Shift + T`  | Reopen Closed Tab               | Global        |
| `F11`               | Toggle Full Screen              | Global        |
| `Alt + ←`           | Navigate Back                   | Page          |
| `Alt + →`           | Navigate Forward                | Page          |
| `Ctrl + D`          | Bookmark Current Page           | Global        |
| `Ctrl + G`          | Open Developer GitHub           | Global        |
| `Ctrl + ,`          | Open Settings                   | Global        |

---

## 6. Advanced Customization <a name="customization"></a>
### Configuration Files
- **Settings**: `~/.config/NextGenBrowser/Settings.ini`
- **Bookmarks**: `~/.local/share/MyOwnBrowser/bookmarks.json`
- **History**: `~/.local/share/MyOwnBrowser/history.db`

### Code Customization Points
1. **Search Engines**  
   Modify `navigate_to_url` method:
   ```python
   search_urls = {
       "MySearch": "https://mysearch.com?q={}"
   }
   ```

2. **Theme Colors**  
   Edit `DARK_STYLE` CSS variables

3. **Blocklist Sources**  
   Modify `AdBlockerInterceptor` class

---

## 7. Troubleshooting <a name="troubleshooting"></a>
### Common Issues
**Problem**: SSL Certificate Errors  
**Solution**:  
```python
# Add to startup script
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--ignore-certificate-errors'
```

**Problem**: Missing Media Codecs  
**Solution**:
```bash
sudo apt install gstreamer1.0-libav
```

**Problem**: Ad Blocking Not Working  
**Solution**:
1. Open Settings ➔ Update Ad Blocklist
2. Manually check `blocklist.txt` exists

---

## 8. FAQs <a name="faqs"></a>
**Q: How to change default download location?**  
A: Modify `download_requested` method path:
```python
download.setPath("/custom/path/" + filename)
```

**Q: Can I add vertical scroll to tabs?**  
A: Yes, enable in QTabWidget properties:
```python
self.tabs.setUsesScrollButtons(True)
```

**Q: How to disable tab previews?**  
A: Comment out `eventFilter` and `preview_timer` code

---

## 9. Developer Information <a name="developer"></a>
### Project Structure
```
MyOwnBrowser/
├── main.py             # Main application logic
├── blocklist.txt       # Ad blocking rules
├── Icon.png            # Icon
└── README.md           # Documentation assets
```

### Contribution Guidelines
1. Fork repository
2. Create feature branch
3. Submit PR with:
   - Updated documentation
   - Passing basic tests
   - Screenshots for UI changes

### License
MIT License - Free for personal and commercial use

---

[⬆ Back to Top](#overview)  
*Documentation version: 1.2 | Last updated: 2024-02-19*  
*Maintainer: Lusan Sapkota | Contact: [GitHub Profile](https://github.com/Lusan-sapkota)*

This documentation can be saved as `DOCUMENTATION.md` in your project root. For visual completeness, consider adding:
1. Actual screenshots in the Overview section
2. Architecture diagram in Developer section
3. Video tutorial links for complex features
