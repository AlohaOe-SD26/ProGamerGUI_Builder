"""
Core Application Window - Main GUI Builder Interface
"""

import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QFrame, QLabel, QPushButton, QComboBox, QMenuBar,
    QToolBar, QStatusBar, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from .canvas import Canvas
from .property_editor import PropertyEditor
from .state_manager import StateManager
from .project_manager import ProjectManager
from widgets.standard_widgets import get_available_widgets
from generators.base_generator import get_available_generators

class GuiBuilderApp(QMainWindow):
    """Main application window for the GUI Builder."""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Core components
        self.state_manager = StateManager()
        self.project_manager = ProjectManager(self.state_manager)
        
        # UI components
        self.canvas: Optional[Canvas] = None
        self.property_editor: Optional[PropertyEditor] = None
        self.widget_palette: Optional[QFrame] = None
        
        # Framework selection
        self.framework_selector: Optional[QComboBox] = None
        self.current_framework = "PyQt6"  # Default framework
        
        self.setup_ui()
        self.setup_connections()
        self.update_framework_widgets()
        
        self.logger.info("GuiBuilderApp initialized")
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ProGamerGUI Builder")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Setup toolbar
        self.setup_toolbar()
        
        # Setup central widget
        self.setup_central_widget()
        
        # Setup status bar
        self.setup_status_bar()
    
    def setup_menu_bar(self):
        """Create and setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Project", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export Code...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.export_code)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.state_manager.undo)
        edit_menu.addAction(undo_action)
        self.undo_action = undo_action
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.state_manager.redo)
        edit_menu.addAction(redo_action)
        self.redo_action = redo_action
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        self.grid_action = QAction("Show &Grid", self, checkable=True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(self.toggle_grid)
        view_menu.addAction(self.grid_action)
        
        self.snap_action = QAction("&Snap to Grid", self, checkable=True)
        self.snap_action.setChecked(True)
        self.snap_action.triggered.connect(self.toggle_snap)
        view_menu.addAction(self.snap_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Create and setup the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Framework selector
        toolbar.addWidget(QLabel("Framework:"))
        self.framework_selector = QComboBox()
        
        # Populate with available generators
        available_generators = get_available_generators()
        for gen_name in available_generators.keys():
            self.framework_selector.addItem(gen_name)
        
        self.framework_selector.setCurrentText(self.current_framework)
        self.framework_selector.currentTextChanged.connect(self.change_framework)
        toolbar.addWidget(self.framework_selector)
        
        toolbar.addSeparator()
        
        # Quick actions
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self.new_project)
        toolbar.addWidget(new_btn)
        
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_project)
        toolbar.addWidget(open_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_project)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        export_btn = QPushButton("Export Code")
        export_btn.clicked.connect(self.export_code)
        toolbar.addWidget(export_btn)
    
    def setup_central_widget(self):
        """Setup the main central widget with three panels."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        central_widget_layout = QHBoxLayout(central_widget)
        central_widget_layout.addWidget(main_splitter)
        
        # Left panel - Widget palette
        self.setup_widget_palette()
        main_splitter.addWidget(self.widget_palette)
        
        # Center panel - Canvas
        self.canvas = Canvas(self.state_manager)
        main_splitter.addWidget(self.canvas)
        
        # Right panel - Property editor
        self.property_editor = PropertyEditor(self.state_manager)
        main_splitter.addWidget(self.property_editor)
        
        # Set splitter sizes (left: 250px, center: expandable, right: 350px)
        main_splitter.setSizes([250, 800, 350])
        main_splitter.setCollapsible(0, False)  # Don't allow collapsing palette
        main_splitter.setCollapsible(2, False)  # Don't allow collapsing properties
    
    def setup_widget_palette(self):
        """Create the widget palette panel."""
        self.widget_palette = QFrame()
        self.widget_palette.setFrameShape(QFrame.Shape.StyledPanel)
        self.widget_palette.setFixedWidth(250)
        
        layout = QVBoxLayout(self.widget_palette)
        
        # Title
        title = QLabel("Widget Palette")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        layout.addWidget(title)
        
        # Scrollable area for widgets
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.widget_list_widget = QWidget()
        self.widget_list_layout = QVBoxLayout(self.widget_list_widget)
        self.widget_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.widget_list_widget)
        layout.addWidget(scroll_area)
        
        # Populate with widgets for current framework
        self.update_framework_widgets()
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_connections(self):
        """Setup signal connections between components."""
        # Connect state manager signals
        self.state_manager.state_changed.connect(self.on_state_changed)
        self.state_manager.selection_changed.connect(self.on_selection_changed)
        
        # Connect canvas signals to property editor
        if self.canvas:
            self.canvas.widget_selected.connect(self.property_editor.set_selected_widget)
            self.canvas.widget_modified.connect(self.state_manager.save_state)
    
    def update_framework_widgets(self):
        """Update the widget palette based on current framework."""
        # Clear existing widgets
        for i in reversed(range(self.widget_list_layout.count())):
            self.widget_list_layout.itemAt(i).widget().setParent(None)
        
        # Get widgets for current framework
        available_widgets = get_available_widgets(self.current_framework)
        
        for widget_info in available_widgets:
            btn = QPushButton(f"Add {widget_info['display_name']}")
            btn.setToolTip(widget_info.get('description', ''))
            btn.clicked.connect(
                lambda checked, w=widget_info: self.add_widget_to_canvas(w)
            )
            self.widget_list_layout.addWidget(btn)
    
    def add_widget_to_canvas(self, widget_info):
        """Add a widget to the canvas."""
        if self.canvas:
            self.canvas.add_widget(widget_info)
    
    def change_framework(self, framework_name: str):
        """Change the target framework."""
        if framework_name != self.current_framework:
            self.current_framework = framework_name
            self.state_manager.set_target_framework(framework_name)
            self.update_framework_widgets()
            self.logger.info(f"Framework changed to: {framework_name}")
    
    def toggle_grid(self, checked: bool):
        """Toggle grid visibility."""
        if self.canvas:
            self.canvas.set_grid_visible(checked)
    
    def toggle_snap(self, checked: bool):
        """Toggle snap to grid."""
        if self.canvas:
            self.canvas.set_snap_enabled(checked)
    
    def new_project(self):
        """Create a new project."""
        self.state_manager.new_project()
        self.status_bar.showMessage("New project created")
    
    def open_project(self):
        """Open an existing project."""
        success = self.project_manager.open_project()
        if success:
            self.status_bar.showMessage("Project opened successfully")
        else:
            self.status_bar.showMessage("Failed to open project")
    
    def save_project(self):
        """Save the current project."""
        success = self.project_manager.save_project()
        if success:
            self.status_bar.showMessage("Project saved successfully")
        else:
            self.status_bar.showMessage("Failed to save project")
    
    def save_project_as(self):
        """Save the current project with a new name."""
        success = self.project_manager.save_project_as()
        if success:
            self.status_bar.showMessage("Project saved successfully")
        else:
            self.status_bar.showMessage("Failed to save project")
    
    def export_code(self):
        """Export the current design to code."""
        success = self.project_manager.export_code()
        if success:
            self.status_bar.showMessage("Code exported successfully")
        else:
            self.status_bar.showMessage("Failed to export code")
    
    def on_state_changed(self):
        """Handle state manager state changes."""
        # Update undo/redo actions
        self.undo_action.setEnabled(self.state_manager.can_undo())
        self.redo_action.setEnabled(self.state_manager.can_redo())
        
        # Update canvas
        if self.canvas:
            self.canvas.update()
    
    def on_selection_changed(self, widget_id: Optional[str]):
        """Handle selection changes."""
        if self.property_editor:
            self.property_editor.set_selected_widget(widget_id)
    
    def show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, 
            "About ProGamerGUI Builder",
            "ProGamerGUI Builder v1.0\n\n"
            "A framework-agnostic GUI builder for Python applications.\n\n"
            "Built with PyQt6"
        )
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Check if project needs saving
        if self.state_manager.has_unsaved_changes():
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if not self.save_project():
                    event.ignore()
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        self.logger.info("Application closing")
        event.accept()