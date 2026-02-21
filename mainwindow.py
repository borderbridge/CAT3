# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, 
    QWidget, QLabel, QGridLayout, QGroupBox, QTextEdit, QPushButton,
    QLineEdit, QComboBox, QFrame, QListWidget, QStackedWidget,
    QFileDialog, QSizePolicy, QScrollArea, QDialog, QDateEdit, QTimeEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon, QPainter, QColor, QBrush

from ui_CAT3_Mainwindow import Ui_MainWindow
from simbad_search_dialog import SimbadButton
from simbad_client import SimbadObject
import db


TYPE_DISPLAY = {
    "": "",
    "galaxy": "Galaxie", "nebula": "Nebel", 
    "planetary_nebula": "Planetarischer Nebel",
    "supernova_remnant": "Supernova-Überrest",
    "open_cluster": "Offener Sternhaufen",
    "globular_cluster": "Kugelsternhaufen",
    "star": "Stern", "planet": "Planet",
    "comet": "Komet", "asteroid": "Asteroid",
    "moon": "Mond", "sun": "Sonne"
}
TYPE_REVERSE = {v: k for k, v in TYPE_DISPLAY.items()}


class ObservationDialog(QDialog):
    def __init__(self, parent=None, observation=None):
        super().__init__(parent)
        self.observation = observation
        if observation:
            self.setWindowTitle("Beobachtung bearbeiten")
        else:
            self.setWindowTitle("Beobachtung hinzufügen")
        self.setMinimumWidth(500)
        self._setup_ui()
        if observation:
            self._load_data()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        dt_layout = QHBoxLayout()
        dt_layout.addWidget(QLabel("Datum:"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        dt_layout.addWidget(self.date_edit)
        dt_layout.addWidget(QLabel("Start:"))
        self.time_start = QTimeEdit()
        self.time_start.setTime(QTime.currentTime())
        dt_layout.addWidget(self.time_start)
        dt_layout.addWidget(QLabel("Ende:"))
        self.time_end = QTimeEdit()
        dt_layout.addWidget(self.time_end)
        layout.addLayout(dt_layout)
        
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(QLabel("Ort:"))
        self.edit_location = QLineEdit()
        self.edit_location.setPlaceholderText("z.B. Garten")
        loc_layout.addWidget(self.edit_location)
        layout.addLayout(loc_layout)
        
        eq_group = QGroupBox("Equipment")
        eq_layout = QGridLayout()
        eq_layout.addWidget(QLabel("Teleskop:"), 0, 0)
        self.edit_telescope = QLineEdit()
        self.edit_telescope.setPlaceholderText('z.B. 8" Dobson')
        eq_layout.addWidget(self.edit_telescope, 0, 1)
        eq_layout.addWidget(QLabel("Okular:"), 0, 2)
        self.edit_eyepiece = QLineEdit()
        self.edit_eyepiece.setPlaceholderText("z.B. 25mm")
        eq_layout.addWidget(self.edit_eyepiece, 0, 3)
        eq_layout.addWidget(QLabel("Kamera:"), 1, 0)
        self.edit_camera = QLineEdit()
        self.edit_camera.setPlaceholderText("z.B. ASI294MC")
        eq_layout.addWidget(self.edit_camera, 1, 1)
        eq_layout.addWidget(QLabel("Filter:"), 1, 2)
        self.edit_filter = QLineEdit()
        self.edit_filter.setPlaceholderText("z.B. UHC")
        eq_layout.addWidget(self.edit_filter, 1, 3)
        eq_group.setLayout(eq_layout)
        layout.addWidget(eq_group)
        
        cond_layout = QHBoxLayout()
        cond_layout.addWidget(QLabel("Seeing:"))
        self.combo_seeing = QComboBox()
        self.combo_seeing.addItems(["", "Excellent", "Good", "Fair", "Poor", "Terrible"])
        cond_layout.addWidget(self.combo_seeing)
        cond_layout.addWidget(QLabel("Transparenz:"))
        self.combo_transparency = QComboBox()
        self.combo_transparency.addItems(["", "Excellent", "Good", "Fair", "Poor"])
        cond_layout.addWidget(self.combo_transparency)
        layout.addLayout(cond_layout)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Datenpfad:"))
        self.edit_data_path = QLineEdit()
        self.edit_data_path.setPlaceholderText("Pfad zu FITS/Rohdaten...")
        path_layout.addWidget(self.edit_data_path)
        btn_browse = QPushButton("Durchsuchen...")
        btn_browse.clicked.connect(self._browse_data_path)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)
        
        layout.addWidget(QLabel("Notizen:"))
        self.te_notes = QTextEdit()
        self.te_notes.setMaximumHeight(100)
        layout.addWidget(self.te_notes)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_cancel = QPushButton("Abbrechen")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        btn_save = QPushButton("Speichern")
        btn_save.clicked.connect(self.accept)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)
        
    def _browse_data_path(self):
        path = QFileDialog.getExistingDirectory(self, "Daten-Verzeichnis auswählen")
        if path:
            self.edit_data_path.setText(path)
            
    def get_data(self):
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'start_time': self.time_start.time().toString("HH:mm"),
            'end_time': self.time_end.time().toString("HH:mm") if self.time_end.time() != QTime(0,0) else None,
            'location_name': self.edit_location.text() or None,
            'telescope': self.edit_telescope.text() or None,
            'camera': self.edit_camera.text() or None,
            'eyepiece': self.edit_eyepiece.text() or None,
            'filter': self.edit_filter.text() or None,
            'seeing': self.combo_seeing.currentText() or None,
            'transparency': self.combo_transparency.currentText() or None,
            'data_path': self.edit_data_path.text() or None,
            'notes': self.te_notes.toPlainText() or None,
        }
    
    def _load_data(self):
        """Load existing observation data into dialog"""
        if not self.observation:
            return
        # Set date
        date_str = self.observation.get('date', '')
        if date_str:
            self.date_edit.setDate(QDate.fromString(date_str, "yyyy-MM-dd"))
        # Set times
        start_str = self.observation.get('start_time', '')
        if start_str:
            self.time_start.setTime(QTime.fromString(start_str, "HH:mm"))
        end_str = self.observation.get('end_time', '')
        if end_str:
            self.time_end.setTime(QTime.fromString(end_str, "HH:mm"))
        # Set location
        if self.observation.get('location_name'):
            self.edit_location.setText(self.observation['location_name'])
        # Set equipment
        if self.observation.get('telescope'):
            self.edit_telescope.setText(self.observation['telescope'])
        if self.observation.get('camera'):
            self.edit_camera.setText(self.observation['camera'])
        if self.observation.get('eyepiece'):
            self.edit_eyepiece.setText(self.observation['eyepiece'])
        if self.observation.get('filter'):
            self.edit_filter.setText(self.observation['filter'])
        # Set conditions
        if self.observation.get('seeing'):
            idx = self.combo_seeing.findText(self.observation['seeing'])
            if idx >= 0:
                self.combo_seeing.setCurrentIndex(idx)
        if self.observation.get('transparency'):
            idx = self.combo_transparency.findText(self.observation['transparency'])
            if idx >= 0:
                self.combo_transparency.setCurrentIndex(idx)
        # Set notes
        if self.observation.get('general_notes'):
            self.te_notes.setPlainText(self.observation['general_notes'])
        # Set data path
        if self.observation.get('data_path'):
            self.edit_data_path.setText(self.observation['data_path'])


class ObjectEditorWidget(QWidget):
    go_back = Signal()
    object_created = Signal(int)
    object_deleted = Signal(int)
    
    def __init__(self, parent=None, mode="view"):
        super().__init__(parent)
        self.mode = mode
        self.current_obj_id = None
        self.current_image_path = None
        self.current_directory = None
        self._setup_ui()
        self.set_mode(mode)
        self._apply_styles()
        
    def _apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #1a1a2e; color: #eaeaea; font-family: 'Segoe UI', sans-serif; font-size: 13px; }
            QGroupBox { border: 1px solid #16213e; border-radius: 8px; margin-top: 10px; padding-top: 10px; font-weight: bold; color: #4fbdba; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QTextEdit, QLineEdit { background-color: #16213e; border: 1px solid #0f3460; border-radius: 6px; padding: 6px; color: #eaeaea; }
            QTextEdit:focus, QLineEdit:focus { border: 1px solid #4fbdba; }
            QPushButton { background-color: #0f3460; border: none; border-radius: 6px; padding: 8px 16px; color: #eaeaea; font-weight: bold; }
            QPushButton:hover { background-color: #4fbdba; color: #1a1a2e; }
            QLabel { color: #b8b8b8; }
            QComboBox { background-color: #16213e; border: 1px solid #0f3460; border-radius: 6px; padding: 6px; color: #eaeaea; }
            QTableWidget { background-color: #16213e; border: 1px solid #0f3460; border-radius: 6px; gridline-color: #0f3460; }
            QTableWidget::item:selected { background-color: #4fbdba; color: #1a1a2e; }
            QHeaderView::section { background-color: #0f3460; color: #eaeaea; padding: 6px; border: none; }
        """)
        
    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        top_section = QHBoxLayout()
        top_section.setSpacing(16)
        
        img_container = QVBoxLayout()
        self.thumbnail_frame = QFrame()
        self.thumbnail_frame.setFixedSize(300, 300)
        self.thumbnail_frame.setStyleSheet("background-color: #16213e; border-radius: 8px;")
        thumb_layout = QVBoxLayout(self.thumbnail_frame)
        thumb_layout.setContentsMargins(4, 4, 4, 4)
        
        self.lbl_thumbnail = QLabel("📷\nKein Bild")
        self.lbl_thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_thumbnail.setStyleSheet("font-size: 48px; color: #4a4a6a; background: transparent;")
        self.lbl_thumbnail.setMinimumSize(290, 260)
        thumb_layout.addWidget(self.lbl_thumbnail)
        
        self.btn_change_image = QPushButton("🖼️ Bild auswählen...")
        self.btn_change_image.setVisible(False)
        self.btn_change_image.setStyleSheet("font-size: 11px; padding: 6px;")
        self.btn_change_image.clicked.connect(self._change_image)
        thumb_layout.addWidget(self.btn_change_image)
        
        self.lbl_image_path = QLabel("")
        self.lbl_image_path.setWordWrap(True)
        self.lbl_image_path.setStyleSheet("font-size: 9px; color: #666;")
        self.lbl_image_path.setVisible(False)
        thumb_layout.addWidget(self.lbl_image_path)
        
        img_container.addWidget(self.thumbnail_frame)
        img_container.addStretch()
        top_section.addLayout(img_container)
        
        right_container = QVBoxLayout()
        right_container.setSpacing(10)
        
        name_header = QLabel("🌟 OBJEKT NAME")
        name_header.setStyleSheet("font-size: 11px; color: #4fbdba; font-weight: bold;")
        right_container.addWidget(name_header)
        
        self.te_name = QTextEdit()
        self.te_name.setMaximumHeight(50)
        self.te_name.setPlaceholderText("z.B. Orionnebel, M31, etc.")
        self.te_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        right_container.addWidget(self.te_name)
        
        info_grid = QGridLayout()
        info_grid.setSpacing(8)
        
        info_items = [
            ("📋 Katalog:", "catalog"), ("🌌 Typ:", "type"),
            ("⭐ Sternbild:", "constellation"), ("💡 Magnitude:", "magnitude"),
            ("📐 Größe:", "size"), ("🎯 RA:", "ra"), ("🎯 Dec:", "dec"),
        ]
        
        for i, (label_text, field_name) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2
            label = QLabel(label_text)
            label.setStyleSheet("color: #888; font-size: 11px;")
            info_grid.addWidget(label, row, col)
            lbl = QLabel("-")
            lbl.setObjectName(f"lbl_{field_name}")
            lbl.setStyleSheet("font-weight: bold; color: #eaeaea;")
            info_grid.addWidget(lbl, row, col + 1)
            if field_name == "type":
                edit = QComboBox()
                edit.addItems([""] + list(TYPE_DISPLAY.values()))
            else:
                edit = QLineEdit()
            edit.setObjectName(f"edit_{field_name}")
            edit.setVisible(False)
            info_grid.addWidget(edit, row, col + 1)
        
        right_container.addLayout(info_grid)
        
        # SIMBAD Search Button (for filling fields from SIMBAD)
        self.btn_simbad = SimbadButton()
        self.btn_simbad.object_selected.connect(self._fill_from_simbad)
        self.btn_simbad.setVisible(False)  # Only visible in edit/create mode
        right_container.addWidget(self.btn_simbad)
        
        dir_layout = QHBoxLayout()
        dir_label = QLabel("📁 Daten:")
        dir_label.setStyleSheet("color: #888;")
        dir_layout.addWidget(dir_label)
        
        self.lbl_directory = QLabel("Kein Verzeichnis gesetzt")
        self.lbl_directory.setObjectName("lbl_directory")
        self.lbl_directory.setStyleSheet("color: #4fbdba; text-decoration: underline;")
        self.lbl_directory.setWordWrap(True)
        dir_layout.addWidget(self.lbl_directory, stretch=1)
        
        self.edit_directory = QLineEdit()
        self.edit_directory.setObjectName("edit_directory")
        self.edit_directory.setVisible(False)
        self.edit_directory.setPlaceholderText("Pfad zum Daten-Verzeichnis...")
        dir_layout.addWidget(self.edit_directory, stretch=1)
        
        self.btn_browse_dir = QPushButton("📂 Durchsuchen...")
        self.btn_browse_dir.setVisible(False)
        self.btn_browse_dir.clicked.connect(self._browse_directory)
        dir_layout.addWidget(self.btn_browse_dir)
        
        self.btn_open_dir = QPushButton("👁️ Öffnen")
        self.btn_open_dir.setStyleSheet("background-color: #533483;")
        self.btn_open_dir.clicked.connect(self._open_directory)
        dir_layout.addWidget(self.btn_open_dir)
        
        right_container.addLayout(dir_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.btn_back = QPushButton("← Zurück zur Liste")
        self.btn_back.setStyleSheet("background-color: #533483;")
        self.btn_back.clicked.connect(self._go_back)
        btn_layout.addWidget(self.btn_back)
        btn_layout.addStretch()
        
        self.btn_edit = QPushButton("✏️ Bearbeiten")
        self.btn_edit.setStyleSheet("background-color: #e94560;")
        self.btn_edit.clicked.connect(self._toggle_edit_mode)
        btn_layout.addWidget(self.btn_edit)
        
        self.btn_save = QPushButton("💾 Speichern")
        self.btn_save.setStyleSheet("background-color: #4fbdba; color: #1a1a2e;")
        self.btn_save.clicked.connect(self._save)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_create = QPushButton("➕ Erstellen")
        self.btn_create.setStyleSheet("background-color: #4fbdba; color: #1a1a2e;")
        self.btn_create.clicked.connect(self._create)
        btn_layout.addWidget(self.btn_create)
        
        self.btn_delete = QPushButton("🗑️ Löschen")
        self.btn_delete.setStyleSheet("background-color: #e94560;")
        self.btn_delete.clicked.connect(self._delete)
        btn_layout.addWidget(self.btn_delete)
        
        right_container.addLayout(btn_layout)
        right_container.addStretch()
        top_section.addLayout(right_container, stretch=1)
        main_layout.addLayout(top_section)
        
        desc_notes_layout = QHBoxLayout()
        desc_group = QGroupBox("📝 Beschreibung")
        desc_vlayout = QVBoxLayout()
        desc_vlayout.setContentsMargins(8, 8, 8, 8)
        self.te_description = QTextEdit()
        self.te_description.setMaximumHeight(120)
        self.te_description.setPlaceholderText("Katalogbeschreibung...")
        desc_vlayout.addWidget(self.te_description)
        desc_group.setLayout(desc_vlayout)
        desc_notes_layout.addWidget(desc_group)
        
        notes_group = QGroupBox("📓 Persönliche Notizen")
        notes_vlayout = QVBoxLayout()
        notes_vlayout.setContentsMargins(8, 8, 8, 8)
        self.te_notes = QTextEdit()
        self.te_notes.setMaximumHeight(120)
        self.te_notes.setPlaceholderText("Deine Beobachtungstipps...")
        notes_vlayout.addWidget(self.te_notes)
        notes_group.setLayout(notes_vlayout)
        desc_notes_layout.addWidget(notes_group)
        main_layout.addLayout(desc_notes_layout)
        
        obs_group = QGroupBox("🔭 Beobachtungen")
        obs_layout = QVBoxLayout()
        obs_layout.setContentsMargins(8, 8, 8, 8)
        
        self.obs_table = QTableWidget()
        self.obs_table.setColumnCount(8)
        self.obs_table.setHorizontalHeaderLabels(["ID", "Datum", "Ort", "Teleskop/Kamera", "Filter", "Seeing", "📂", "Notizen"])
        self.obs_table.setColumnHidden(0, True)
        # Configure column widths: Date, Location, Scope/Camera, Filter, Seeing, Data fixed, Notes takes rest
        header = self.obs_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Datum
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Ort
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Teleskop/Kamera
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Filter
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Seeing
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Daten Button
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Notizen (takes remaining)
        self.obs_table.setColumnWidth(1, 100)  # Datum
        self.obs_table.setColumnWidth(2, 120)  # Ort
        self.obs_table.setColumnWidth(3, 150)  # Teleskop/Kamera
        self.obs_table.setColumnWidth(4, 80)   # Filter
        self.obs_table.setColumnWidth(5, 80)   # Seeing
        self.obs_table.setColumnWidth(6, 40)   # Daten Button (📂)
        self.obs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.obs_table.setMinimumHeight(200)
        self.obs_table.itemDoubleClicked.connect(self._edit_observation)
        self.obs_table.itemClicked.connect(self._on_obs_item_clicked)
        obs_layout.addWidget(self.obs_table, stretch=1)
        
        obs_btn_layout = QHBoxLayout()
        obs_btn_layout.addStretch()
        self.btn_add_obs = QPushButton("➕ Beobachtung hinzufügen")
        self.btn_add_obs.setStyleSheet("background-color: #4fbdba; color: #1a1a2e;")
        self.btn_add_obs.clicked.connect(self._add_observation)
        obs_btn_layout.addWidget(self.btn_add_obs)
        obs_layout.addLayout(obs_btn_layout)
        obs_group.setLayout(obs_layout)
        main_layout.addWidget(obs_group)
        
        scroll.setWidget(container)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)
        
    def _browse_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Daten-Verzeichnis auswählen")
        if path:
            self.edit_directory.setText(path)
            
    def _open_directory(self):
        path = self.current_directory if hasattr(self, 'current_directory') and self.current_directory else self.edit_directory.text()
        if path and os.path.exists(path):
            try:
                if sys.platform == "linux" or sys.platform == "linux2":
                    subprocess.run(["xdg-open", path])
                elif sys.platform == "darwin":
                    subprocess.run(["open", path])
                elif sys.platform == "win32":
                    subprocess.run(["explorer", path])
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Konnte Verzeichnis nicht öffnen: {e}")
        else:
            QMessageBox.information(self, "Info", "Kein Verzeichnis gesetzt oder Pfad existiert nicht.")
            
    def _add_observation(self):
        if not self.current_obj_id:
            QMessageBox.warning(self, "Fehler", "Objekt muss zuerst gespeichert sein.")
            return
        dialog = ObservationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                obs_id = db.insert_observation(
                    date=data['date'],
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    location_name=data['location_name'],
                    telescope=data['telescope'],
                    camera=data['camera'],
                    eyepiece=data['eyepiece'],
                    filter_used=data['filter'],
                    data_path=data.get('data_path'),
                    seeing=data['seeing'],
                    transparency=data['transparency'],
                    general_notes=data['notes']
                )
                db.add_object_to_observation(obs_id, self.current_obj_id)
                self._load_observations()
                # Status shown in table update, no popup needed
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
                
    def _load_observations(self):
        if not self.current_obj_id:
            return
        observations = db.fetch_observations_for_object(self.current_obj_id)
        self.obs_table.setRowCount(len(observations))
        for i, obs in enumerate(observations):
            equip_parts = []
            if obs.get('telescope'):
                equip_parts.append(obs['telescope'])
            if obs.get('camera'):
                equip_parts.append(obs['camera'])
            equipment = " + ".join(equip_parts) if equip_parts else "-"
            self.obs_table.setItem(i, 0, QTableWidgetItem(str(obs.get('id', ''))))
            self.obs_table.setItem(i, 1, QTableWidgetItem(obs.get('date', '')))
            self.obs_table.setItem(i, 2, QTableWidgetItem(obs.get('location_name', '')))
            self.obs_table.setItem(i, 3, QTableWidgetItem(equipment))
            self.obs_table.setItem(i, 4, QTableWidgetItem(obs.get('filter', '')))
            self.obs_table.setItem(i, 5, QTableWidgetItem(obs.get('seeing', '')))
            # Data path button column - show 📂 if path exists, · if no path
            data_item = QTableWidgetItem()
            if obs.get('data_path'):
                data_item.setText("📂")
                data_item.setData(Qt.ItemDataRole.UserRole, obs['data_path'])
                data_item.setToolTip(f"Klicken zum Öffnen:\n{obs['data_path']}")
                data_item.setForeground(QColor("#4fbdba"))  # Turquoise for clickable
            else:
                data_item.setText("·")  # Small dot indicates no path
                data_item.setToolTip("Kein Datenpfad gesetzt\n(Klicken tut nichts)")
                data_item.setForeground(QColor("#4a4a6a"))  # Gray for inactive
            data_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            data_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.obs_table.setItem(i, 6, data_item)
            self.obs_table.setItem(i, 7, QTableWidgetItem(obs.get('general_notes', '')[:50]))
        
    def _on_obs_item_clicked(self, item):
        """Handle clicks on observation table - open data path if 📂 column clicked"""
        if not item:
            return
        column = item.column()
        if column == 6:  # 📂 column
            path = item.data(Qt.ItemDataRole.UserRole)
            if path and os.path.exists(path):
                try:
                    if sys.platform == "linux" or sys.platform == "linux2":
                        subprocess.run(["xdg-open", path])
                    elif sys.platform == "darwin":
                        subprocess.run(["open", path])
                    elif sys.platform == "win32":
                        subprocess.run(["explorer", path])
                except Exception as e:
                    QMessageBox.warning(self, "Fehler", f"Konnte Verzeichnis nicht öffnen: {e}")
            elif path:
                QMessageBox.information(self, "Info", f"Pfad existiert nicht:\n{path}")
        
    def _edit_observation(self, item):
        """Edit an existing observation"""
        row = item.row()
        obs_id_item = self.obs_table.item(row, 0)
        if not obs_id_item:
            return
        obs_id = int(obs_id_item.text())
        
        # Get full observation data from database
        obs = db.fetch_observation_by_id(obs_id)
        if not obs:
            return
            
        # Open dialog with existing data
        dialog = ObservationDialog(self, observation=obs)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                # Update observation - need to add update function to db.py
                self._update_observation(obs_id, data)
                self._load_observations()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
                
    def _update_observation(self, obs_id, data):
        """Helper to update observation in database"""
        conn = db.get_conn()
        with conn:
            conn.execute("""
                UPDATE observations SET
                    date = ?, start_time = ?, end_time = ?,
                    location_name = ?, telescope = ?, camera = ?, eyepiece = ?, filter = ?,
                    data_path = ?, seeing = ?, transparency = ?, general_notes = ?
                WHERE id = ?
            """, (
                data['date'], data['start_time'], data['end_time'],
                data['location_name'], data['telescope'], data['camera'], data['eyepiece'], data['filter'],
                data.get('data_path'), data['seeing'], data['transparency'], data['notes'],
                obs_id
            ))
        
    def set_mode(self, mode):
        self.mode = mode
        self.btn_back.setVisible(mode in ("view", "edit"))
        self.btn_edit.setVisible(mode == "view")
        self.btn_save.setVisible(mode == "edit")
        self.btn_create.setVisible(mode == "create")
        self.btn_delete.setVisible(mode in ("view", "edit"))
        self.btn_add_obs.setVisible(mode in ("view", "edit"))
        self.te_name.setReadOnly(mode == "view")
        self.te_description.setReadOnly(mode == "view")
        self.te_notes.setReadOnly(mode == "view")
        self.btn_change_image.setVisible(mode in ("edit", "create"))
        
        fields = ["catalog", "type", "constellation", "magnitude", "ra", "dec", "size"]
        for field in fields:
            lbl = self.findChild(QLabel, f"lbl_{field}")
            edit = self.findChild(QLineEdit, f"edit_{field}")
            if not edit:
                edit = self.findChild(QComboBox, f"edit_{field}")
            if lbl and edit:
                lbl.setVisible(mode == "view")
                edit.setVisible(mode in ("edit", "create"))
        
        self.lbl_directory.setVisible(mode == "view")
        self.btn_open_dir.setVisible(mode == "view")
        self.edit_directory.setVisible(mode in ("edit", "create"))
        self.btn_browse_dir.setVisible(mode in ("edit", "create"))
        
        # SIMBAD button only visible in edit/create mode
        if hasattr(self, 'btn_simbad'):
            self.btn_simbad.setVisible(mode in ("edit", "create"))
                
    def _toggle_edit_mode(self):
        if self.mode == "view":
            self.set_mode("edit")
            for field in ["catalog", "constellation", "magnitude"]:
                lbl = self.findChild(QLabel, f"lbl_{field}")
                edit = self.findChild(QLineEdit, f"edit_{field}")
                if lbl and edit:
                    val = lbl.text()
                    edit.setText(val if val != "-" else "")
            lbl_size = self.findChild(QLabel, "lbl_size")
            edit_size = self.findChild(QLineEdit, "edit_size")
            if lbl_size and edit_size:
                val = lbl_size.text()
                edit_size.setText(val.replace(" arcmin", "").replace("'", "") if val != "-" else "")
            for field in ["ra", "dec"]:
                lbl = self.findChild(QLabel, f"lbl_{field}")
                edit = self.findChild(QLineEdit, f"edit_{field}")
                if lbl and edit:
                    val = lbl.text()
                    if val != "-":
                        clean = val.replace("h ", " ").replace("m ", " ").replace("s", "").replace("° ", " ").replace("' ", " ").replace("''", "")
                        edit.setText(clean)
            lbl_type = self.findChild(QLabel, "lbl_type")
            edit_type = self.findChild(QComboBox, "edit_type")
            if lbl_type and edit_type:
                current = lbl_type.text()
                idx = edit_type.findText(current)
                edit_type.setCurrentIndex(idx if idx >= 0 else 0)
            if hasattr(self, 'current_directory'):
                self.edit_directory.setText(self.current_directory)
        else:
            self.set_mode("view")
            
    def _change_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Bild auswählen", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp *.tif *.tiff)")
        if file_path:
            self.current_image_path = file_path
            self._load_thumbnail(file_path)
            self.lbl_image_path.setText(file_path)
            self.lbl_image_path.setVisible(True)
            
    def _load_thumbnail(self, path):
        if not path or not os.path.exists(path):
            self.lbl_thumbnail.setText("📷\nKein Bild")
            self.lbl_thumbnail.setPixmap(QPixmap())
            return
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.lbl_thumbnail.setText("❌\nUngültig")
            return
        scaled = pixmap.scaled(290, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_thumbnail.setPixmap(scaled)
        self.lbl_thumbnail.setText("")
        
    def _collect_data(self):
        data = {
            'name': self.te_name.toPlainText().strip(),
            'description': self.te_description.toPlainText().strip() or None,
            'notes': self.te_notes.toPlainText().strip() or None,
        }
        if self.mode in ("edit", "create"):
            edits = {}
            for field in ['catalog', 'constellation', 'magnitude', 'size', 'ra', 'dec']:
                edits[field] = self.findChild(QLineEdit, f"edit_{field}")
            edit_type = self.findChild(QComboBox, "edit_type")
            data['catalog_id'] = edits['catalog'].text().strip() or None if edits['catalog'] else None
            data['constellation'] = edits['constellation'].text().strip() or None if edits['constellation'] else None
            data['object_type'] = TYPE_REVERSE.get(edit_type.currentText()) if edit_type else None
            data['data_directory'] = self.edit_directory.text().strip() or None
            mag_text = edits['magnitude'].text().strip() if edits['magnitude'] else ""
            try:
                data['magnitude'] = float(mag_text) if mag_text else None
            except ValueError:
                data['magnitude'] = None
            size_text = edits['size'].text().strip() if edits['size'] else ""
            try:
                data['size_arcmin'] = float(size_text) if size_text else None
            except ValueError:
                data['size_arcmin'] = None
            for coord, keys in [('ra', ['ra_hours', 'ra_minutes', 'ra_seconds']), ('dec', ['dec_degrees', 'dec_minutes', 'dec_seconds'])]:
                text = edits[coord].text().strip() if edits[coord] else ""
                if text:
                    try:
                        parts = text.replace(':', ' ').split()
                        if len(parts) >= 1:
                            data[keys[0]] = int(parts[0])
                        if len(parts) >= 2:
                            data[keys[1]] = int(parts[1])
                        if len(parts) >= 3:
                            data[keys[2]] = float(parts[2])
                    except (ValueError, IndexError):
                        pass
        return data
        
    def _save(self):
        if not self.current_obj_id:
            return
        data = self._collect_data()
        if not data['name']:
            QMessageBox.warning(self, "Fehler", "Name darf nicht leer sein.")
            return
        try:
            db.update_object(self.current_obj_id, **data)
            if self.current_image_path:
                db.insert_image(file_path=self.current_image_path, object_id=self.current_obj_id, is_primary=True)
            # Update status bar or show minimal feedback only
            if self.parent():
                main_win = self.window()
                if hasattr(main_win, 'statusBar'):
                    main_win.statusBar().showMessage("✓ Gespeichert", 2000)
            self.set_mode("view")
            obj = db.fetch_object_by_id(self.current_obj_id)
            if obj:
                self.set_data(obj)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern: {e}")
            
    def _create(self):
        data = self._collect_data()
        if not data['name']:
            QMessageBox.warning(self, "Fehler", "Name darf nicht leer sein.")
            return
        try:
            new_id = db.insert_object(**data)
            self.current_obj_id = new_id
            if self.current_image_path:
                db.insert_image(file_path=self.current_image_path, object_id=new_id, is_primary=True)
            # No popup - just update status via signal
            obj = db.fetch_object_by_id(new_id)
            if obj:
                self.set_data(obj)
                self.set_mode("view")
            self.object_created.emit(new_id)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Erstellen: {e}")
            
    def _delete(self):
        if not self.current_obj_id:
            return
        name = self.te_name.toPlainText()
        reply = QMessageBox.question(self, "Löschen bestätigen", f'Möchtest du "{name}" wirklich löschen?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                deleted_id = self.current_obj_id
                db.delete_object(self.current_obj_id)
                # No popup needed - signal updates the list
                self.object_deleted.emit(deleted_id)
                self.clear_data()
                self.current_obj_id = None
                self._go_back()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Löschen: {e}")

    def _fill_from_simbad(self, obj: SimbadObject):
        """Fill form fields from SIMBAD object data"""
        # Set name if empty
        if not self.te_name.toPlainText().strip():
            self.te_name.setPlainText(obj.name)

        # Set catalog ID
        edit_catalog = self.findChild(QLineEdit, "edit_catalog")
        if edit_catalog:
            edit_catalog.setText(obj.main_id)

        # Set coordinates
        edit_ra = self.findChild(QLineEdit, "edit_ra")
        if edit_ra:
            edit_ra.setText(f"{obj.ra_hours} {obj.ra_minutes} {obj.ra_seconds:.2f}")

        edit_dec = self.findChild(QLineEdit, "edit_dec")
        if edit_dec:
            edit_dec.setText(f"{obj.dec_degrees} {obj.dec_minutes} {obj.dec_seconds:.2f}")

        # Set magnitude
        if obj.magnitude_v:
            edit_magnitude = self.findChild(QLineEdit, "edit_magnitude")
            if edit_magnitude:
                edit_magnitude.setText(f"{obj.magnitude_v:.1f}")

        # Set size
        if obj.size_arcmin:
            edit_size = self.findChild(QLineEdit, "edit_size")
            if edit_size:
                edit_size.setText(f"{obj.size_arcmin:.1f}")

        # Set object type
        edit_type = self.findChild(QComboBox, "edit_type")
        if edit_type:
            display_type = TYPE_DISPLAY.get(obj.object_type, "")
            idx = edit_type.findText(display_type)
            if idx >= 0:
                edit_type.setCurrentIndex(idx)

        # Set description from morphology if available
        if obj.morphology and not self.te_description.toPlainText().strip():
            self.te_description.setPlainText(f"Typ: {obj.morphology}")

        # Show status
        if self.parent():
            main_win = self.window()
            if hasattr(main_win, 'statusBar'):
                main_win.statusBar().showMessage(f"✓ Daten aus SIMBAD übernommen: {obj.main_id}", 3000)

    def _go_back(self):
        self.go_back.emit()
            
    def clear_data(self):
        self.current_obj_id = None
        self.current_image_path = None
        self.current_directory = None
        self.te_name.clear()
        self.te_description.clear()
        self.te_notes.clear()
        self.lbl_thumbnail.setText("📷\nKein Bild")
        self.lbl_thumbnail.setPixmap(QPixmap())
        self.lbl_image_path.clear()
        self.lbl_image_path.setVisible(False)
        self.lbl_directory.setText("Kein Verzeichnis gesetzt")
        self.edit_directory.clear()
        self.obs_table.setRowCount(0)
        for field in ["catalog", "type", "constellation", "magnitude", "ra", "dec", "size"]:
            lbl = self.findChild(QLabel, f"lbl_{field}")
            if lbl:
                lbl.setText("-")
                
    def set_data(self, obj: dict):
        self.current_obj_id = obj.get("id")
        self.current_directory = obj.get("data_directory")
        self.te_name.setPlainText(obj.get("name", ""))
        fields = {
            'catalog': obj.get("catalog_id") or "-",
            'type': TYPE_DISPLAY.get(obj.get("object_type"), obj.get("object_type")) or "-",
            'constellation': obj.get("constellation") or "-",
            'magnitude': f"{obj.get('magnitude'):.1f}" if obj.get("magnitude") is not None else "-",
            'size': f"{obj.get('size_arcmin'):.1f} arcmin" if obj.get("size_arcmin") is not None else "-",
        }
        ra_h, ra_m, ra_s = obj.get("ra_hours"), obj.get("ra_minutes"), obj.get("ra_seconds")
        if all(v is not None for v in [ra_h, ra_m, ra_s]):
            fields['ra'] = f"{ra_h:02d}h {ra_m:02d}m {ra_s:05.2f}s"
        else:
            fields['ra'] = "-"
        dec_d, dec_m, dec_s = obj.get("dec_degrees"), obj.get("dec_minutes"), obj.get("dec_seconds")
        if all(v is not None for v in [dec_d, dec_m, dec_s]):
            fields['dec'] = f"{dec_d:+d}° {abs(dec_m):02d}' {abs(dec_s):04.1f}''"
        else:
            fields['dec'] = "-"
        for field, value in fields.items():
            lbl = self.findChild(QLabel, f"lbl_{field}")
            if lbl:
                lbl.setText(value)
        if self.current_directory:
            self.lbl_directory.setText(self.current_directory)
            self.lbl_directory.setStyleSheet("color: #4fbdba; text-decoration: underline;")
        else:
            self.lbl_directory.setText("Kein Verzeichnis gesetzt")
            self.lbl_directory.setStyleSheet("color: #666; font-style: italic;")
        self.te_description.setPlainText(obj.get("description", ""))
        self.te_notes.setPlainText(obj.get("notes", ""))
        self._load_object_image(obj.get("id"))
        self._load_observations()
        
    def _load_object_image(self, obj_id):
        if not obj_id:
            return
        image = db.fetch_primary_image(obj_id)
        if image:
            path = image.get("file_path")
            self.current_image_path = path
            self._load_thumbnail(path)
            self.lbl_image_path.setText(path)
            self.lbl_image_path.setVisible(True)
        else:
            self.lbl_thumbnail.setText("📷\nKein Bild")
            self.lbl_thumbnail.setPixmap(QPixmap())
            self.current_image_path = None
            self.lbl_image_path.clear()
            self.lbl_image_path.setVisible(False)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._apply_main_styles()
        self._init_database()
        self._setup_pages()
        self.ui.NavigationListWidget.currentRowChanged.connect(self.on_nav_changed)
        self.ui.objectsList.itemClicked.connect(self.show_object_details)
        self.ui.filterInput.textChanged.connect(self.refresh_objects)
        self.setWindowTitle("CAT 3 - Catalog of Astronomical Things")
        self._show_statistics()
        
    def _apply_main_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a2e; }
            QListWidget {
                background-color: #16213e;
                border: none;
                border-radius: 8px;
                padding: 4px;
                color: #eaeaea;
            }
            QListWidget::item {
                padding: 2px 4px;
                border-radius: 3px;
                margin: 1px 0;
                min-height: 32px;
            }
            QListWidget::item:selected {
                background-color: #4fbdba;
                color: #1a1a2e;
            }
            QListWidget::item:hover {
                background-color: #0f3460;
            }
            QLineEdit {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 8px;
                color: #eaeaea;
            }
        """)
        from PySide6.QtCore import QSize
        self.ui.objectsList.setIconSize(QSize(32, 32))
        self.ui.objectsList.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ui.objectsList.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
    def _setup_pages(self):
        existing_layout = self.ui.NewEntry.layout()
        if existing_layout:
            while existing_layout.count():
                item = existing_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            existing_layout.setContentsMargins(0, 0, 0, 0)
            new_entry_layout = existing_layout
        else:
            new_entry_layout = QVBoxLayout(self.ui.NewEntry)
            new_entry_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_new = ObjectEditorWidget(self.ui.NewEntry, mode="create")
        self.editor_new.object_created.connect(self._on_object_created)
        new_entry_layout.addWidget(self.editor_new)
        
        if hasattr(self.ui, 'ObjectDetails'):
            layout = self.ui.ObjectDetails.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                layout = QVBoxLayout(self.ui.ObjectDetails)
                layout.setContentsMargins(0, 0, 0, 0)
            self.editor_details = ObjectEditorWidget(self.ui.ObjectDetails, mode="view")
            self.editor_details.go_back.connect(self.show_object_list)
            self.editor_details.object_deleted.connect(self._on_object_deleted)
            layout.addWidget(self.editor_details)
        
    def _init_database(self):
        stats = db.get_statistics()
        # Auto-import disabled - user wants clean database for own observations only
        # if stats['total_objects'] == 0:
        #     from catalog_imports import import_all_catalogs
        #     import_all_catalogs()
        #     stats = db.get_statistics()
        print(f"Database ready: {stats['total_objects']} objects")
        
    def _show_statistics(self):
        stats = db.get_statistics()
        info = f"Objekte: {stats['total_objects']} | Beobachtungen: {stats['total_observations']} | Bilder: {stats['total_images']}"
        self.statusBar().showMessage(info)
        
    def _on_object_created(self, obj_id):
        self._show_statistics()
        
    def _on_object_deleted(self, obj_id):
        self._show_statistics()
        self.refresh_objects()
        
    def on_nav_changed(self, index: int):
        current_index = self.ui.DisplayedWindwoWidget.currentIndex()
        if current_index == 3 and index == 1:
            self.show_object_list()
            return
        if index == 0:
            self.editor_new.clear_data()
            self.editor_new.set_mode("create")
        elif index == 1:
            self.refresh_objects()
        self.ui.DisplayedWindwoWidget.setCurrentIndex(index)
        
    def refresh_objects(self, filter_text: str = ""):
        self.ui.objectsList.clear()
        if not filter_text and hasattr(self.ui, 'filterInput'):
            filter_text = self.ui.filterInput.text()
        objects = db.fetch_objects(filter_text, search_all_fields=True)
        for obj_id, name, catalog_id, obj_type in objects:
            display_text = f"{obj_id}: {name}"
            if catalog_id:
                display_text += f"  [{catalog_id}]"
            self.ui.objectsList.addItem(display_text)
            item = self.ui.objectsList.item(self.ui.objectsList.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, obj_id)
            thumb_loaded = False
            try:
                image = db.fetch_primary_image(obj_id)
                if image and image.get('file_path'):
                    path = image['file_path']
                    if os.path.exists(path):
                        pixmap = QPixmap(path)
                        if not pixmap.isNull():
                            scaled = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            item.setIcon(QIcon(scaled))
                            thumb_loaded = True
            except Exception:
                pass
            if not thumb_loaded:
                placeholder = QPixmap(32, 32)
                placeholder.fill(QColor("#2a2a3e"))
                painter = QPainter(placeholder)
                painter.setBrush(QColor("#4a4a6a"))
                painter.setPen(QColor("#4a4a6a"))
                painter.drawEllipse(12, 12, 8, 8)
                painter.end()
                item.setIcon(QIcon(placeholder))
            
    def show_object_details(self, item):
        obj_id = item.data(Qt.ItemDataRole.UserRole)
        if not obj_id:
            try:
                obj_id = int(item.text().split(":", 1)[0])
            except (ValueError, AttributeError):
                return
        obj = db.fetch_object_by_id(obj_id)
        if not obj:
            QMessageBox.warning(self, "Fehler", "Objekt nicht gefunden.")
            return
        self.editor_details.set_data(obj)
        self.editor_details.set_mode("view")
        self.ui.DisplayedWindwoWidget.setCurrentIndex(3)
        
    def show_object_list(self):
        self.refresh_objects()
        self.ui.NavigationListWidget.setCurrentRow(1)
        self.ui.DisplayedWindwoWidget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
