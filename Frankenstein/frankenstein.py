import sys
import os
import json
import re # Import re for parsing LLM commands
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QSplitter, QToolBar, QLineEdit, QPushButton, QTextEdit,
    QMenu, QMessageBox, QInputDialog, QStatusBar, QLabel 
)
from PyQt6.QtCore import Qt, QUrl, QProcess
from PyQt6.QtGui import QFont, QColor, QPalette, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView 

from llm_manager import LLMManager # Import LLMManager
from terminal_panel import TerminalPanel # Import TerminalPanel

BOOKMARKS_FILE = os.path.join(os.path.dirname(__file__), "victors_lab_bookmarks.json")

class VictorsLabMode(QMainWindow):
    def __init__(self, parent_app=None): # Added parent_app parameter
        super().__init__()
        self.parent_app = parent_app # Store reference to the main app

        self.setWindowTitle("Victor's Lab - Experimental Browser & Terminal")
        self.setGeometry(100, 100, 1200, 800)

        self.apply_victors_lab_theme()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bookmarks = []
        self.load_bookmarks()

        # Status Bar - Initialize before connecting signals from browser
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.llm_manager = LLMManager() # Instantiate LLMManager

        self._build_ui()
        # self.start_terminal() # Terminal logic now handled by TerminalPanel

    def apply_victors_lab_theme(self):
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#222222"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#EEEEEE"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#EEEEEE"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#00FFFF"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #222222;
            }
            QWidget {
                background-color: #222222;
                color: #EEEEEE;
            }
            QToolBar {
                background-color: #333333;
                border: 1px solid #444444;
                spacing: 5px;
            }
            QPushButton {
                background-color: #555555;
                color: #EEEEEE;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
                border-color: #00FFFF;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QLineEdit {
                background-color: #444444;
                color: #EEEEEE;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 3px;
            }
            QTextEdit {
                background-color: #1a1a1a;
                color: #00FF00;
                border: 1px solid #444444;
                font-family: 'Consolas', 'Monospace';
                font-size: 10pt;
            }
            QSplitter::handle {
                background-color: #555555;
            }
            QMenu {
                background-color: #333333;
                color: #EEEEEE;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #00FFFF;
                color: #000000;
            }
            QStatusBar {
                background-color: #333333;
                color: #00FF00;
                border-top: 1px solid #444444;
            }
        """)
        font = QFont("Arial")
        font.setPointSize(10)
        self.setFont(font)

    def _build_ui(self):
        # Web Browser Component - Initialize first
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com")) # Set an initial URL
        self.browser.urlChanged.connect(self.update_url_bar) # Update URL bar on navigation
        self.browser.loadStarted.connect(lambda: self.status_bar.showMessage("Loading..."))
        self.browser.loadFinished.connect(lambda ok: self.status_bar.showMessage("Page loaded." if ok else "Page failed to load."))
        self.browser.titleChanged.connect(self.setWindowTitle)

        # Navigation Bar (Toolbar)
        self.navigation_bar = QToolBar("Navigation")
        self.addToolBar(self.navigation_bar)

        back_button = QPushButton("Back")
        back_button.clicked.connect(self.browser.back)
        self.navigation_bar.addWidget(back_button)

        forward_button = QPushButton("Forward")
        forward_button.clicked.connect(self.browser.forward)
        self.navigation_bar.addWidget(forward_button)

        reload_button = QPushButton("Reload")
        reload_button.clicked.connect(self.browser.reload)
        self.navigation_bar.addWidget(reload_button)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.url_bar)

        add_bookmark_button = QPushButton("Add Bookmark")
        add_bookmark_button.clicked.connect(self.add_bookmark)
        self.navigation_bar.addWidget(add_bookmark_button)

        self.bookmarks_button = QPushButton("Bookmarks")
        self.bookmarks_button.setMenu(QMenu(self))
        self.bookmarks_button.clicked.connect(self.show_bookmarks_menu)
        self.navigation_bar.addWidget(self.bookmarks_button)

        # Create a splitter to divide the window
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Web Browser Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True) # Make tabs look more modern
        self.tab_widget.setTabsClosable(True) # Allow closing tabs
        self.tab_widget.tabCloseRequested.connect(self.close_browser_tab)
        self.splitter.addWidget(self.tab_widget)

        # Add the initial browser as a tab
        self.tab_widget.addTab(self.browser, "New Tab")
        self.tab_widget.setCurrentWidget(self.browser) # Set the initial tab as current

        # Terminal Area - Split vertically for multiple terminals
        self.terminal_area_widget = QWidget()
        self.terminal_area_layout = QVBoxLayout(self.terminal_area_widget) # Use QVBoxLayout for button
        self.terminal_area_layout.setContentsMargins(0,0,0,0)

        self.terminal_splitter = QSplitter(Qt.Orientation.Vertical) # Splitter for terminals
        self.terminal_area_layout.addWidget(self.terminal_splitter) # Add splitter to terminal_area_layout

        # Terminal 1
        self.terminal1 = TerminalPanel(self, shell_command=self._detect_shell(), llm_manager=self.llm_manager)
        self.terminal1.closed_signal.connect(self._remove_terminal_panel)
        self.terminal_splitter.addWidget(self.terminal1)

        # "Back to the Drawing Board" Button
        back_to_app_button = QPushButton("Back to the Drawing Board")
        back_to_app_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: #EEEEEE;
                border: 1px solid #777777;
                border-radius: 4px;
                padding: 3px 6px; /* Smaller padding for mini button */
                font-size: 8pt; /* Smaller font size */
            }
            QPushButton:hover {
                background-color: #666666;
                border-color: #00FFFF;
            }
        """)
        back_to_app_button.clicked.connect(self.back_to_app_selection)
        self.terminal_area_layout.addWidget(back_to_app_button)
        # self.terminal_area_layout.addStretch() # Push button to top of its allocated space

        self.splitter.addWidget(self.terminal_area_widget)

        # Set initial sizes for the splitter (e.g., 70% browser, 30% terminal)
        self.splitter.setSizes([700, 300])

        # Initial update of URL bar - now connects to the current tab's browser
        self.update_url_bar(self.browser.url())

    def close_browser_tab(self, index):
        if self.tab_widget.count() < 2: # Don't close the last tab
            return
        widget = self.tab_widget.widget(index)
        widget.deleteLater() # Delete the widget
        self.tab_widget.removeTab(index)

    def _remove_terminal_panel(self, panel: QWidget):
        # Prevent closing if only one terminal remains
        if self.terminal_splitter.count() <= 1:
            QMessageBox.information(self, "Cannot Close", "Cannot close the last terminal panel.")
            return

        # Find the index of the panel in the splitter
        index = self.terminal_splitter.indexOf(panel)
        if index != -1:
            # Take the item from the splitter and schedule its widget for deletion
            item = self.terminal_splitter.takeAt(index)
            if item and item.widget():
                item.widget().deleteLater()

    def back_to_app_selection(self):
        if self.parent_app:
            self.parent_app.show()
            self.hide()

    def navigate_to_url(self):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            url = self.url_bar.text()
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url
            current_browser.setUrl(QUrl(url))

    def update_url_bar(self, url):
        # This also needs to be updated for current tab, connected to tab_widget.currentChanged signal
        self.url_bar.setText(url.toString())

    def load_bookmarks(self):
        if os.path.exists(BOOKMARKS_FILE):
            try:
                with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                    self.bookmarks = json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "Bookmarks Error", f"Could not load bookmarks: {e}")

    def save_bookmarks(self):
        try:
            with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.bookmarks, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Bookmarks Error", f"Could not save bookmarks: {e}")

    def add_bookmark(self):
        current_browser = self.tab_widget.currentWidget()
        if not current_browser:
            return
        current_url = current_browser.url().toString()
        current_title = current_browser.title()
        
        text, ok = QInputDialog.getText(self, "Add Bookmark", "Bookmark Name:", QLineEdit.EchoMode.Normal, current_title or current_url)
        
        if ok and text:
            self.bookmarks.append({"name": text, "url": current_url})
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmark Added", f"Bookmark '{text}' added.")

    def show_bookmarks_menu(self):
        menu = QMenu(self)
        if not self.bookmarks:
            menu.addAction("No Bookmarks")
        else:
            for bookmark in self.bookmarks:
                action = QAction(bookmark["name"], self)
                action.setData(bookmark["url"])
                action.triggered.connect(lambda checked, url=bookmark["url"]: self.navigate_to_bookmark(url))
                menu.addAction(action)
        
        menu.exec(self.bookmarks_button.mapToGlobal(self.bookmarks_button.rect().bottomLeft()))

    def navigate_to_bookmark(self, url):
        current_browser = self.tab_widget.currentWidget()
        if current_browser:
            current_browser.setUrl(QUrl(url))

    def _detect_shell(self) -> str:
        if sys.platform == "win32":
            return "cmd.exe"
        else:
            return "bash"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    victors_lab_window = VictorsLabMode()
    victors_lab_window.show()
    sys.exit(app.exec())