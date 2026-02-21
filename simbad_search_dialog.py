"""
SIMBAD Search Dialog for CAT3
Search astronomical objects and auto-fill coordinates
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal
from simbad_client import search_by_name, SimbadObject, test_connection


class SimbadSearchThread(QThread):
    """Background thread for SIMBAD searches"""
    results_ready = Signal(list)
    error = Signal(str)
    
    def __init__(self, query: str):
        super().__init__()
        self.query = query
        
    def run(self):
        try:
            results = search_by_name(self.query, limit=20)
            self.results_ready.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class SimbadSearchDialog(QDialog):
    """Dialog for searching SIMBAD and selecting objects"""
    
    object_selected = Signal(SimbadObject)
    
    def __init__(self, parent=None, initial_query: str = ""):
        super().__init__(parent)
        self.setWindowTitle("SIMBAD Suche - Objekt aus Katalog")
        self.setMinimumSize(700, 500)
        self.selected_object = None
        self.search_thread = None
        
        self._setup_ui()
        
        if initial_query:
            self.query_input.setText(initial_query)
            self._do_search()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Info label
        info = QLabel("Suche im SIMBAD Astronomical Database (Strasbourg)")
        info.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info)
        
        # Search row
        search_layout = QHBoxLayout()
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("z.B. M31, Andromeda, Orionnebel, NGC7000...")
        self.query_input.returnPressed.connect(self._do_search)
        search_layout.addWidget(self.query_input, stretch=1)
        
        self.search_btn = QPushButton("🔍 Suchen")
        self.search_btn.clicked.connect(self._do_search)
        search_layout.addWidget(self.search_btn)
        
        layout.addLayout(search_layout)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Typ", "Rektaszension", "Deklination", "Helligkeit (V)", "Größe ('')"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SingleSelection)
        self.results_table.doubleClicked.connect(self._on_double_click)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Klicke 'Suchen' um SIMBAD zu durchsuchen")
        self.status_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.use_btn = QPushButton("✓ Übernehmen")
        self.use_btn.setEnabled(False)
        self.use_btn.clicked.connect(self._accept_selection)
        btn_layout.addWidget(self.use_btn)
        
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _do_search(self):
        query = self.query_input.text().strip()
        if not query:
            return
        
        self.search_btn.setEnabled(False)
        self.use_btn.setEnabled(False)
        self.status_label.setText(f"Suche nach '{query}' in SIMBAD...")
        self.results_table.setRowCount(0)
        
        # Start background search
        self.search_thread = SimbadSearchThread(query)
        self.search_thread.results_ready.connect(self._on_results)
        self.search_thread.error.connect(self._on_error)
        self.search_thread.finished.connect(lambda: self.search_btn.setEnabled(True))
        self.search_thread.start()
    
    def _on_results(self, results: list):
        self.results_table.setRowCount(len(results))
        
        for i, obj in enumerate(results):
            self.results_table.setItem(i, 0, QTableWidgetItem(obj.main_id))
            self.results_table.setItem(i, 1, QTableWidgetItem(obj.object_type))
            self.results_table.setItem(i, 2, QTableWidgetItem(obj.ra_display))
            self.results_table.setItem(i, 3, QTableWidgetItem(obj.dec_display))
            
            mag_str = f"{obj.magnitude_v:.1f}" if obj.magnitude_v else "-"
            self.results_table.setItem(i, 4, QTableWidgetItem(mag_str))
            
            size_str = f"{obj.size_arcmin:.1f}" if obj.size_arcmin else "-"
            self.results_table.setItem(i, 5, QTableWidgetItem(size_str))
            
            # Store full object in first column
            self.results_table.item(i, 0).setData(Qt.UserRole, obj)
        
        self.status_label.setText(f"{len(results)} Treffer gefunden")
        if len(results) > 0:
            self.use_btn.setEnabled(True)
    
    def _on_error(self, error_msg: str):
        self.status_label.setText(f"Fehler: {error_msg}")
        QMessageBox.warning(self, "SIMBAD Fehler", 
                          f"Konnte SIMBAD nicht erreichen:\n{error_msg}")
    
    def _on_double_click(self):
        self._accept_selection()
    
    def _accept_selection(self):
        current_row = self.results_table.currentRow()
        if current_row < 0:
            return
        
        item = self.results_table.item(current_row, 0)
        obj = item.data(Qt.UserRole)
        
        if obj:
            self.selected_object = obj
            self.object_selected.emit(obj)
            self.accept()
    
    def get_selected_object(self) -> SimbadObject:
        return self.selected_object


class SimbadButton(QPushButton):
    """Button that opens SIMBAD search and emits selected object"""
    object_selected = Signal(SimbadObject)
    
    def __init__(self, parent=None):
        super().__init__("🔍 Aus SIMBAD", parent)
        self.clicked.connect(self._open_search)
        self.setToolTip("Koordinaten und Helligkeit aus SIMBAD übernehmen")
        
        # Check if SIMBAD is available
        if not test_connection():
            self.setEnabled(False)
            self.setToolTip("SIMBAD nicht erreichbar (keine Internetverbindung?)")
    
    def _open_search(self):
        dialog = SimbadSearchDialog(self)
        dialog.object_selected.connect(self.object_selected.emit)
        dialog.exec()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = SimbadSearchDialog(initial_query="M31")
    
    if dialog.exec() == QDialog.Accepted:
        obj = dialog.get_selected_object()
        print(f"Selected: {obj.main_id}")
        print(f"  RA: {obj.ra_display}")
        print(f"  Dec: {obj.dec_display}")
        print(f"  Mag V: {obj.magnitude_v}")
    
    sys.exit(0)