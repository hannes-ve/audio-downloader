#!/usr/bin/env python3
import sys
import os
import threading
import queue
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QMessageBox, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import audio_downloader

class DownloadSignals(QObject):
    """Signal holder for download process"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class AudioDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.message_queue = queue.Queue()
        self.signals = DownloadSignals()
        self.initUI()
        
        # Setup timer for checking messages from the thread
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_messages)
        self.timer.start(100)  # Check every 100ms
        
    def initUI(self):
        self.setWindowTitle('Audio Downloader')
        self.setGeometry(300, 300, 600, 400)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel('URL:')
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        main_layout.addLayout(url_layout)
        
        # Output location
        output_layout = QHBoxLayout()
        output_label = QLabel('Save to:')
        self.output_path = QLineEdit()
        self.output_path.setReadOnly(True)
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_location)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_button)
        main_layout.addLayout(output_layout)
        
        # Progress display - using a text edit for better log display
        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)
        self.progress_text.setMinimumHeight(150)
        main_layout.addWidget(self.progress_text)
        
        # Download button
        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.download_finished)
        self.signals.error.connect(self.download_error)
        
    def browse_location(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Audio File", 
            os.path.expanduser("~/Downloads"), 
            "Audio Files (*.mp3);;All Files (*)", 
            options=options
        )
        
        if file_path:
            self.output_path.setText(file_path)
    
    def update_progress(self, message):
        self.progress_text.append(message)
        # Scroll to the bottom
        scrollbar = self.progress_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def download_finished(self, message):
        self.update_progress(message)
        self.download_button.setEnabled(True)
        QMessageBox.information(self, "Download Complete", message)
    
    def download_error(self, error_message):
        self.update_progress(f"ERROR: {error_message}")
        self.download_button.setEnabled(True)
        QMessageBox.critical(self, "Download Error", error_message)
    
    def check_messages(self):
        """Check for messages from the download thread"""
        try:
            while True:
                message_type, message = self.message_queue.get_nowait()
                if message_type == "progress":
                    self.signals.progress.emit(message)
                elif message_type == "finished":
                    self.signals.finished.emit(message)
                elif message_type == "error":
                    self.signals.error.emit(message)
                self.message_queue.task_done()
        except queue.Empty:
            pass
    
    def download_worker(self, url, output_path):
        """Worker function that runs in a separate thread"""
        try:
            # Custom print function to send messages to the main thread
            def thread_print(message):
                self.message_queue.put(("progress", message))
            
            # Store the original print function
            original_print = print
            
            # Replace the global print function
            import builtins
            builtins.print = thread_print
            
            try:
                # Perform the download
                result = audio_downloader.download_audio(url, output_path)
                
                if result:
                    self.message_queue.put(("finished", f"Download completed: {result}"))
                else:
                    self.message_queue.put(("finished", "Download completed!"))
            finally:
                # Restore the original print function
                builtins.print = original_print
                
        except Exception as e:
            self.message_queue.put(("error", str(e)))
    
    def start_download(self):
        url = self.url_input.text().strip()
        output_path = self.output_path.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL")
            return
        
        # Disable the download button during download
        self.download_button.setEnabled(False)
        self.update_progress("Starting download...")
        
        # Start the download in a separate thread
        self.download_thread = threading.Thread(
            target=self.download_worker,
            args=(url, output_path if output_path else None)
        )
        self.download_thread.daemon = True  # Thread will exit when main thread exits
        self.download_thread.start()

    def closeEvent(self, event):
        # The daemon thread will be automatically terminated when the app closes
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = AudioDownloaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
