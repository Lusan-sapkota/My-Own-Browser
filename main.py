import sys
import os
import requests
from urllib.parse import urlparse
from PyQt5.QtCore import (
    QUrl, Qt, QStandardPaths, QSize, QSettings, QTimer,
    QFile, QSaveFile, QPoint, QEvent
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QAction,
    QLineEdit, QDockWidget, QListWidget, QMessageBox, QMenu,
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QDialog, QComboBox, QListWidgetItem, QStyle, QFileDialog,
    QProgressBar, QToolButton, QGraphicsOpacityEffect, QInputDialog
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView, QWebEngineDownloadItem, QWebEngineProfile, QWebEnginePage, QWebEngineSettings
)
from PyQt5.QtGui import (
    QIcon, QKeySequence, QDesktopServices, QFont, QPixmap,
    QPainter, QColor, QPalette, QCursor
)
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo

os.environ['QT_SSL_VERSION'] = 'tlsv1.3'
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'

# ------------------------- Configuration -------------------------
SETTINGS = QSettings("NextGenBrowser", "Settings")
DARK_STYLE = """
    QMainWindow, QDialog, QDockWidget, QWidget {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    QToolBar {
        background-color: #3d3d3d;
        border: none;
        padding: 4px;
    }
    QLineEdit {
        background-color: #4d4d4d;
        color: #ffffff;
        border: 1px solid #5d5d5d;
        border-radius: 20px;
        padding: 8px;
    }
    QListWidget {
        background-color: #3d3d3d;
        color: #ffffff;
        border: none;
    }
    QTabBar::tab {
        background: #3d3d3d;
        color: #ffffff;
        padding: 12px 20px;
        border: none;
        border-left: 3px solid transparent;
    }
    QTabBar::tab:selected {
        background: #4d4d4d;
        border-left: 3px solid #2196F3;
    }
    QProgressBar {
        background: #3d3d3d;
        color: #ffffff;
        border: 1px solid #5d5d5d;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #2196F3;
    }
"""

DARK_STYLE_CSS = """
html {
    background-color: #1a1a1a !important;
    filter: invert(1) hue-rotate(180deg) contrast(0.9);
}
img, video, iframe {
    filter: invert(1) hue-rotate(180deg) contrast(0.9);
}
"""

# ------------------------- Persistent Storage -------------------------
class PersistentListWidget(QListWidget):
    def __init__(self, settings_key, parent=None):
        super().__init__(parent)
        self.settings_key = settings_key
        self.load_items()

    def load_items(self):
        self.clear()
        items = SETTINGS.value(self.settings_key, []) or []
        for item in items:
            self.addItem(item)

    def save_items(self):
        items = [self.item(i).text() for i in range(self.count())]
        SETTINGS.setValue(self.settings_key, items)

# ------------------------- Ad Blocker -------------------------
class AdBlockerInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocked_domains = set()
        self.load_blocklist()

    def load_blocklist(self):
        try:
            with open("blocklist.txt", "r") as f:
                self.blocked_domains = {
                    line.strip() for line in f 
                    if line.strip() and not line.startswith('#')
                }
        except FileNotFoundError:
            self.update_blocklist()

    def update_blocklist(self):
        try:
            url = "https://easylist.to/easylist/easylist.txt"
            response = requests.get(url)
            with open("blocklist.txt", "w") as f:
                f.write(response.text)
            self.load_blocklist()
            return True
        except Exception as e:
            print(f"Blocklist update failed: {e}")
            return False

    def interceptRequest(self, info):
        host = info.requestUrl().host()
        resource_type = info.resourceType()
        
        if host and ('localhost' in host or host.endswith('.local')):
            return
            
        if resource_type in [
            QWebEngineUrlRequestInfo.ResourceTypeMedia,
            QWebEngineUrlRequestInfo.ResourceTypePluginResource
        ]:
            return

        if any(domain in host for domain in self.blocked_domains):
            info.block(True)

# ------------------------- Settings Dialog -------------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout(self)

        # Theme Selection
        self.theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(SETTINGS.value("Theme", "Light"))
        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_combo)

        # Search Engine
        self.search_engine_label = QLabel("Search Engine:")
        self.search_engine_combo = QComboBox()
        self.search_engine_combo.addItems(["Google", "DuckDuckGo", "Bing", "Yahoo"])
        self.search_engine_combo.setCurrentText(SETTINGS.value("SearchEngine", "Google"))
        layout.addWidget(self.search_engine_label)
        layout.addWidget(self.search_engine_combo)

        # Home Page
        self.home_page_label = QLabel("Home Page:")
        self.home_page_edit = QLineEdit()
        self.home_page_edit.setText(SETTINGS.value("HomePage", "https://www.google.com"))
        self.home_page_browse = QPushButton("...")
        self.home_page_browse.clicked.connect(self.browse_home_page)
        home_layout = QHBoxLayout()
        home_layout.addWidget(self.home_page_edit)
        home_layout.addWidget(self.home_page_browse)
        layout.addWidget(self.home_page_label)
        layout.addLayout(home_layout)

        # Blocklist Update
        self.update_blocklist_btn = QPushButton("Update Ad Blocklist")
        self.update_blocklist_btn.clicked.connect(self.update_blocklist)
        layout.addWidget(self.update_blocklist_btn)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def browse_home_page(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Home Page", "", "HTML Files (*.html *.htm)")
        if file_name:
            self.home_page_edit.setText(file_name)

    def update_blocklist(self):
        interceptor = self.parent().profile.requestInterceptor()
        if interceptor.update_blocklist():
            QMessageBox.information(self, "Success", "Ad blocklist updated successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to update ad blocklist")

    def save_settings(self):
        SETTINGS.setValue("Theme", self.theme_combo.currentText())
        SETTINGS.setValue("SearchEngine", self.search_engine_combo.currentText())
        SETTINGS.setValue("HomePage", self.home_page_edit.text())
        self.parent().apply_theme(self.theme_combo.currentText())
        self.accept()

# ------------------------- Enhanced Web Page -------------------------
class CustomWebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loadFinished.connect(self.handle_load_finished)

    def handle_load_finished(self, ok):
        if not ok:
            self.show_error_page()

    def show_error_page(self):
        error_html = """
        <html>
            <body style="background: #f0f0f0; text-align: center; padding: 50px;">
                <h1 style="color: #d32f2f;">⚠️ Connection Error</h1>
                <p>Unable to reach this website</p>
                <p>Possible reasons:</p>
                <ul style="list-style: none; padding: 0;">
                    <li>Internet connection lost</li>
                    <li>Website server is down</li>
                    <li>SSL certificate error</li>
                </ul>
                <button onclick="window.history.back()" 
                        style="padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 4px;">
                    Go Back
                </button>
            </body>
        </html>
        """
        self.setHtml(error_html, QUrl("about:error"))

    def certificateError(self, error):
        reply = QMessageBox.question(
            self.view().window(),
            "SSL Certificate Error",
            f"This site's security certificate is not trusted.\n\n{error.description()}\n\nProceed anyway?",
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes

# ------------------------- Downloads Manager -------------------------
class DownloadsManager(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Downloads", parent)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.downloads = []

        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.downloads_list = QListWidget()
        layout.addWidget(self.downloads_list)
        self.setWidget(widget)

    def add_download(self, download):
        item = QListWidgetItem()
        widget = QWidget()
        layout = QHBoxLayout(widget)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)

        self.file_label = QLabel(download.path().split('/')[-1])
        self.cancel_btn = QPushButton()
        self.cancel_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.cancel_btn.clicked.connect(download.cancel)

        layout.addWidget(self.file_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.cancel_btn)

        download.downloadProgress.connect(lambda r, t: self.progress.setValue(int(100 * (r / t))) if t > 0 else None)
        download.finished.connect(lambda: self.progress.setValue(100))

        self.downloads_list.addItem(item)
        self.downloads_list.setItemWidget(item, widget)

# ------------------------- Main Window -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        QWebEngineProfile.defaultProfile().setHttpCacheType(QWebEngineProfile.NoCache)
        QWebEngineProfile.defaultProfile().setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--ignore-certificate-errors --enable-features=AllowInsecureLocalhost'
        super().__init__()
        self.setWindowTitle("My Own Browser")
        self.setMinimumSize(1024, 768)

        # Initialize ad blocker
        self.profile = QWebEngineProfile.defaultProfile()
        self.interceptor = AdBlockerInterceptor()
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # Initialize UI
        self.init_ui()
        self.init_connections()
        self.apply_theme(SETTINGS.value("Theme", "Light"))

        # Initial tab
        self.add_new_tab(QUrl(SETTINGS.value("HomePage", "https://www.google.com")), "New Tab")
        self.tab_previews = {}
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.show_tab_preview)

                # Site dark mode state
        self.site_dark_mode = False
        self.dark_style_file = "dark_mode.css"
        
        # Enable dev tools
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        QWebEngineSettings.globalSettings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)

    def init_ui(self):
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setTabPosition(QTabWidget.East)
        self.setCentralWidget(self.tabs)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)

        # Navigation
        nav_actions = [
            (QStyle.SP_ArrowBack, "Back", "Alt+Left", lambda: self.current_browser().back()),
            (QStyle.SP_ArrowForward, "Forward", "Alt+Right", lambda: self.current_browser().forward()),
            (QStyle.SP_BrowserReload, "Reload", "F5", lambda: self.current_browser().reload()),
            (QStyle.SP_DirHomeIcon, "Home", "Alt+Home", self.go_home)
        ]
        for icon, text, shortcut, handler in nav_actions:
            action = QAction(self.style().standardIcon(icon), text, self)
            action.setShortcut(shortcut)
            action.triggered.connect(handler)
            self.toolbar.addAction(action)

        # URL Bar and Security Status
        self.url_bar = QLineEdit()
        self.url_bar.setClearButtonEnabled(True)
        self.url_bar.setPlaceholderText("Search or enter address")
        self.toolbar.addWidget(self.url_bar)
        
        self.security_status = QLabel()
        self.security_status.setFixedWidth(120)
        self.toolbar.addWidget(self.security_status)

        # Menu
        self.menu_btn = QToolButton()
        self.menu_btn.setText("☰")
        self.menu_btn.setFont(QFont("Arial", 14))
        self.menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.menu = QMenu()
        self.create_menu()
        self.menu_btn.setMenu(self.menu)
        self.toolbar.addWidget(self.menu_btn)

        # Docks
        self.init_docks()

    def init_docks(self):
        # History
        self.history_dock = QDockWidget("History", self)
        self.history_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.history_list = PersistentListWidget("History")
        self.history_dock.setWidget(self.history_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.history_dock)

        # Bookmarks
        self.bookmarks_dock = QDockWidget("Bookmarks", self)
        self.bookmarks_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.bookmarks_list = PersistentListWidget("Bookmarks")
        self.bookmarks_dock.setWidget(self.bookmarks_list)
        self.addDockWidget(Qt.RightDockWidgetArea, self.bookmarks_dock)

        # Downloads
        self.downloads_dock = DownloadsManager(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.downloads_dock)

        # Hide docks initially
        self.history_dock.hide()
        self.bookmarks_dock.hide()
        self.downloads_dock.hide()

    def create_menu(self):
        # New Tab
        new_tab_action = QAction("New Tab", self)
        new_tab_action.setShortcut(QKeySequence.AddTab)
        new_tab_action.triggered.connect(lambda: self.add_new_tab())
        self.menu.addAction(new_tab_action)

        # Bookmarks
        bookmark_action = QAction("Bookmark Page", self)
        bookmark_action.triggered.connect(self.bookmark_current_page)
        self.menu.addAction(bookmark_action)

        # Downloads
        downloads_action = QAction("Downloads", self)
        downloads_action.triggered.connect(lambda: self.downloads_dock.setVisible(not self.downloads_dock.isVisible()))
        self.menu.addAction(downloads_action)

        # Page Actions
        view_source_action = QAction("View Page Source", self)
        view_source_action.triggered.connect(self.view_page_source)
        self.menu.addAction(view_source_action)

        save_page_action = QAction("Save Page As...", self)
        save_page_action.triggered.connect(self.save_page)
        self.menu.addAction(save_page_action)

        # Full Screen
        fullscreen_action = QAction("Toggle Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.menu.addAction(fullscreen_action)

        # Site Dark Mode toggle
        self.site_dark_action = QAction("Site Dark Mode", self)
        self.site_dark_action.setCheckable(True)
        self.site_dark_action.toggled.connect(self.toggle_site_dark_mode)
        self.menu.addAction(self.site_dark_action)

        # Inspect menu
        inspect_menu = self.menu.addMenu("Inspect")
        inspect_element = QAction("Inspect Element", self)
        inspect_element.setShortcut("Ctrl+Shift+I")
        inspect_element.triggered.connect(self.show_dev_tools)
        inspect_menu.addAction(inspect_element)

        # Settings
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(settings_action)

        # GitHub
        github_action = QAction(QIcon.fromTheme("applications-internet"), "My GitHub", self)
        github_action.triggered.connect(self.open_github)
        github_action.setShortcut(QKeySequence("Ctrl+G"))
        self.menu.addSeparator()
        self.menu.addAction(github_action)

    def toggle_site_dark_mode(self, checked):
        self.site_dark_mode = checked
        if checked:
            # Create dark mode CSS file
            with open(self.dark_style_file, "w") as f:
                f.write(DARK_STYLE_CSS)
            self.profile.setUserStyleSheetUrl(QUrl.fromLocalFile(os.path.abspath(self.dark_style_file)))
        else:
            self.profile.setUserStyleSheetUrl(QUrl())

    def show_dev_tools(self):
        current_page = self.current_browser().page()
        current_page.triggerAction(QWebEnginePage.InspectElement)


    def init_connections(self):
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.tabs.tabBar().installEventFilter(self)

    def apply_theme(self, theme_name):
        if theme_name == "Dark":
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet("")

    def current_browser(self):
        return self.tabs.currentWidget()

    def add_new_tab(self, url=None, title="New Tab"):
        browser = QWebEngineView()
        page = CustomWebPage(browser)
        browser.setPage(page)
        
        browser.setUrl(url or QUrl(SETTINGS.value("HomePage", "https://www.google.com")))
        
        index = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(self.update_url)
        browser.titleChanged.connect(lambda t: self.update_tab_title(index, t))
        browser.iconChanged.connect(lambda: self.tabs.setTabIcon(index, browser.icon()))
        browser.loadProgress.connect(lambda p: self.statusBar().showMessage(f"Loading... {p}%", 2000))
        browser.page().profile().downloadRequested.connect(self.download_requested)
        browser.page().loadFinished.connect(lambda: self.capture_tab_preview(browser))

        # Context menu
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        menu = QMenu()
        
        # Standard actions
        back_action = QAction("Back", self)
        back_action.triggered.connect(self.current_browser().back)
        menu.addAction(back_action)

        forward_action = QAction("Forward", self)
        forward_action.triggered.connect(self.current_browser().forward)
        menu.addAction(forward_action)

        reload_action = QAction("Reload", self)
        reload_action.triggered.connect(self.current_browser().reload)
        menu.addAction(reload_action)

        menu.addSeparator()

        # Custom actions
        view_source_action = QAction("View Page Source", self)
        view_source_action.triggered.connect(self.view_page_source)
        menu.addAction(view_source_action)

        save_page_action = QAction("Save Page As...", self)
        save_page_action.triggered.connect(self.save_page)
        menu.addAction(save_page_action)

        menu.exec_(self.current_browser().mapToGlobal(pos))

    def view_page_source(self):
        def callback(content):
            browser = QWebEngineView()
            browser.setHtml(content)
            self.add_new_tab(QUrl("view-source"), "Page Source")
        self.current_browser().page().toHtml(callback)

    def save_page(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Page", "", "HTML Files (*.html)")
        if path:
            def callback(content):
                with open(path, 'w') as f:
                    f.write(content)
            self.current_browser().page().toHtml(callback)

    def capture_tab_preview(self, browser):
        pixmap = QPixmap(browser.size())
        painter = QPainter(pixmap)
        browser.render(painter)
        painter.end()
        self.tab_previews[browser] = pixmap.scaled(QSize(200, 150), Qt.KeepAspectRatio)

    def show_tab_preview(self):
        index = self.tabs.tabBar().tabAt(self.tabs.mapFromGlobal(QCursor.pos()))
        if index >= 0 and (browser := self.tabs.widget(index)) in self.tab_previews:
            preview = QLabel(self)
            preview.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
            preview.setPixmap(self.tab_previews[browser])
            preview.move(QCursor.pos() + QPoint(20, 20))
            preview.show()
            QTimer.singleShot(3000, preview.deleteLater)

    def eventFilter(self, obj, event):
        if obj == self.tabs.tabBar():
            if event.type() == QEvent.MouseMove:
                self.preview_timer.start(500)
            elif event.type() == QEvent.Leave:
                self.preview_timer.stop()
        return super().eventFilter(obj, event)

    def toggle_fullscreen(self):
        self.showFullScreen() if not self.isFullScreen() else self.showNormal()

    def navigate_to_url(self):
        raw_input = self.url_bar.text().strip()
        if not raw_input:
            return

        # Check if input is a URL
        if any(x in raw_input for x in ['.', ':', 'localhost']):
            parsed = urlparse(raw_input)
            if not parsed.scheme:
                if raw_input.startswith('//'):
                    raw_input = 'http:' + raw_input
                else:
                    if 'localhost' in raw_input:
                        raw_input = f'http://{raw_input}'
                    else:
                        raw_input = f'https://{raw_input}'
            
            qurl = QUrl(raw_input)
            if qurl.isValid():
                self.current_browser().setUrl(qurl)
                return
        
        # If not URL, perform search
        search_engine = SETTINGS.value("SearchEngine", "Google")
        search_urls = {
            "Google": f"https://www.google.com/search?q={raw_input}",
            "DuckDuckGo": f"https://duckduckgo.com/?q={raw_input}",
            "Bing": f"https://www.bing.com/search?q={raw_input}",
            "Yahoo": f"https://search.yahoo.com/search?p={raw_input}"
        }
        qurl = QUrl(search_urls[search_engine])
        self.current_browser().setUrl(qurl)

    def update_security_status(self, qurl):
        scheme = qurl.scheme()
        host = qurl.host()
        
        if scheme == 'https':
            self.security_status.setText("Secure 🔒")
            self.security_status.setStyleSheet("color: #4CAF50;")
        elif scheme == 'http':
            if host and ('localhost' in host or '127.0.0.1' in host):
                self.security_status.setText("Local 🏠")
                self.security_status.setStyleSheet("color: #FF9800;")
            else:
                self.security_status.setText("Not Secure 🔓")
                self.security_status.setStyleSheet("color: #F44336;")
        else:
            self.security_status.setText("Unknown ❓")
            self.security_status.setStyleSheet("color: #9E9E9E;")

    def update_url(self, qurl):
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)
        self.history_list.addItem(qurl.toString())
        self.update_security_status(qurl)

    def update_tab_title(self, index, title):
        self.tabs.setTabText(index, title[:20] + "..." if len(title) > 20 else title)

    def go_home(self):
        self.current_browser().setUrl(QUrl(SETTINGS.value("HomePage", "https://www.google.com")))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def tab_changed(self, index):
        if self.tabs.count() == 0: return
        self.update_url(self.current_browser().url())

    def bookmark_current_page(self):
        url = self.current_browser().url().toString()
        if not any(url == self.bookmarks_list.item(i).text() for i in range(self.bookmarks_list.count())):
            self.bookmarks_list.addItem(url)
            QMessageBox.information(self, "Bookmarked", "Page added to bookmarks")

    def download_requested(self, download):
        path = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        download.setPath(f"{path}/{download.suggestedFileName()}")
        download.accept()
        self.downloads_dock.add_download(download)
        self.downloads_dock.show()

    def open_github(self):
        github_url = "https://github.com/Lusan-sapkota"
        self.add_new_tab(QUrl(github_url), "GitHub - Lusan")

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def closeEvent(self, event):
        self.history_list.save_items()
        self.bookmarks_list.save_items()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Apply saved theme
    theme = SETTINGS.value("Theme", "Light")
    if theme == "Dark":
        app.setStyleSheet(DARK_STYLE)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
