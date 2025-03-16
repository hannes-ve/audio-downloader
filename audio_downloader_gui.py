#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import audio_downloader

class DownloadThread(QThread):
    """Thread for handling downloads without freezing the GUI"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path
        
    def run(self):
        try:
            # Redirect stdout to capture progress messages
            original_stdout = sys.stdout
            
            class StdoutRedirector:
                def __init__(self, signal):
                    self.signal = signal
                    self.buffer = ""
                
                def write(self, text):
                    self.buffer += text
                    if '\n' in self.buffer:
                        lines = self.buffer.split('\n')
                        for line in lines[:-1]:
                            self.signal.emit(line)
                        self.buffer = lines[-1]
                
                def flush(self):
                    if self.buffer:
                        self.signal.emit(self.buffer)
                        self.buffer = ""
            
            sys.stdout = StdoutRedirector(self.progress_signal)
            
            # Perform the download
            result = audio_downloader.download_audio(self.url, self.output_path)
            
            # Restore stdout
            sys.stdout = original_stdout
            
            if result:
                self.finished_signal.emit(f"Download completed: {result}")
            else:
                self.finished_signal.emit("Download completed!")
                
        except Exception as e:
            # Restore stdout in case of error
            sys.stdout = sys.__stdout__
            self.error_signal.emit(f"Error: {str(e)}")

class AudioDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Audio Downloader')
        self.setGeometry(300, 300, 600, 200)
        
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
        
        # Progress display
        self.progress_text = QLabel('Ready')
        main_layout.addWidget(self.progress_text)
        
        # Download button
        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.start_download)
        main_layout.addWidget(self.download_button)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
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
        self.progress_text.setText(message)
    
    def download_finished(self, message):
        self.progress_text.setText(message)
        self.download_button.setEnabled(True)
        QMessageBox.information(self, "Download Complete", message)
    
    def download_error(self, error_message):
        self.progress_text.setText(error_message)
        self.download_button.setEnabled(True)
        QMessageBox.critical(self, "Download Error", error_message)
    
    def start_download(self):
        url = self.url_input.text().strip()
        output_path = self.output_path.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a URL")
            return
        
        # If no output path is specified, we'll let the downloader handle it
        
        # Disable the download button during download
        self.download_button.setEnabled(False)
        self.progress_text.setText("Starting download...")
        
        # Start the download thread
        self.download_thread = DownloadThread(url, output_path if output_path else None)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        self.download_thread.start()

def main():
    app = QApplication(sys.argv)
    window = AudioDownloaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
