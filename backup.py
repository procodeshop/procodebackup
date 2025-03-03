import os
import zipfile
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QRadioButton, \
    QButtonGroup, QProgressBar
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG


class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Backup Data")
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

        self.label_source = QLabel("Source Folder: Not Selected")
        layout.addWidget(self.label_source)
        self.btn_source = QPushButton("Select Source Folder")
        self.btn_source.clicked.connect(self.select_source_folder)
        layout.addWidget(self.btn_source)

        self.label_destination = QLabel("Destination Folder: Not Selected")
        layout.addWidget(self.label_destination)
        self.btn_destination = QPushButton("Select Destination Folder")
        self.btn_destination.clicked.connect(self.select_destination_folder)
        layout.addWidget(self.btn_destination)

        self.radio_single = QRadioButton("Single ZIP")
        self.radio_separate = QRadioButton("Separate ZIPs")
        self.radio_single.setChecked(True)
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_single)
        self.radio_group.addButton(self.radio_separate)
        layout.addWidget(self.radio_single)
        layout.addWidget(self.radio_separate)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.btn_backup = QPushButton("Start Backup")
        self.btn_backup.clicked.connect(self.start_backup_thread)
        layout.addWidget(self.btn_backup)

        self.setLayout(layout)

    def select_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.label_source.setText(f"Source Folder: {folder}")
            self.source_folder = folder

    def select_destination_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.label_destination.setText(f"Destination Folder: {folder}")
            self.destination_folder = folder

    def zip_folder(self, source_folder, zip_path):
        """Compress a folder into a zip file with progress."""
        file_list = []
        for root, _, files in os.walk(source_folder):
            for file in files:
                file_list.append(os.path.join(root, file))

        total_files = len(file_list)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, file in enumerate(file_list):
                zipf.write(file, os.path.relpath(file, source_folder))
                progress = int((idx + 1) / total_files * 100)
                QMetaObject.invokeMethod(self.progress_bar, "setValue", Q_ARG(int, progress))

    def start_backup_thread(self):
        self.btn_backup.setEnabled(False)
        self.progress_bar.setValue(0)
        QMetaObject.invokeMethod(self.status_label, "setText", Q_ARG(str, "Backup in progress..."))
        QMetaObject.invokeMethod(self.status_label, "setStyleSheet", Q_ARG(str, "color: blue;"))
        backup_thread = threading.Thread(target=self.backup_data, daemon=True)
        backup_thread.start()

    def backup_data(self):
        try:
            source_folder = getattr(self, 'source_folder', None)
            destination_folder = getattr(self, 'destination_folder', None)
            zip_mode = 'single' if self.radio_single.isChecked() else 'separate'

            if not source_folder or not destination_folder:
                QMetaObject.invokeMethod(self.status_label, "setText",
                                         Q_ARG(str, "Error: Please select both source and destination folders."))
                QMetaObject.invokeMethod(self.status_label, "setStyleSheet", Q_ARG(str, "color: red;"))
                QMetaObject.invokeMethod(self.btn_backup, "setEnabled", Q_ARG(bool, True))
                return

            os.makedirs(destination_folder, exist_ok=True)

            if zip_mode == 'single':
                zip_name = os.path.join(destination_folder, "backup.zip")
                self.zip_folder(source_folder, zip_name)
                QMetaObject.invokeMethod(self.status_label, "setText", Q_ARG(str, f"Backup saved as: {zip_name}"))
            else:
                subfolders = [f for f in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, f))]
                total_folders = len(subfolders)

                for idx, folder_name in enumerate(subfolders):
                    folder_path = os.path.join(source_folder, folder_name)
                    zip_name = os.path.join(destination_folder, f"{folder_name}.zip")
                    self.zip_folder(folder_path, zip_name)
                    progress = int((idx + 1) / total_folders * 100)
                    QMetaObject.invokeMethod(self.progress_bar, "setValue", Q_ARG(int, progress))

                QMetaObject.invokeMethod(self.status_label, "setText",
                                         Q_ARG(str, "Backup process completed with separate ZIPs."))

            QMetaObject.invokeMethod(self.status_label, "setStyleSheet", Q_ARG(str, "color: green;"))
        except Exception as e:
            QMetaObject.invokeMethod(self.status_label, "setText", Q_ARG(str, f"Error: {str(e)}"))
            QMetaObject.invokeMethod(self.status_label, "setStyleSheet", Q_ARG(str, "color: red;"))
        finally:
            QMetaObject.invokeMethod(self.btn_backup, "setEnabled", Q_ARG(bool, True))
            QMetaObject.invokeMethod(self.progress_bar, "setValue", Q_ARG(int, 100))


if __name__ == "__main__":
    app = QApplication([])
    window = BackupApp()
    window.show()
    app.exec_()
