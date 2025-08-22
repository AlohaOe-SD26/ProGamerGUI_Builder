"""
State Manager - Central state management for the GUI Builder
"""

import copy
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from PyQt6.QtCore import QObject, pyqtSignal

def setup_logging():
    """Setup logging configuration."""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")),
            logging.StreamHandler()
        ]
    )

class StateManager(QObject):
    """
    Central state manager for the GUI Builder application.
    Manages project state, undo/redo, and coordinates between components.
    """
    
    # Signals
    state_changed = pyqtSignal()
    selection_changed = pyqtSignal(str)  # widget_id or None
    widget_added = pyqtSignal(str)  # widget_id
    widget_removed = pyqtSignal(str)  # widget_id
    widget_modified = pyqtSignal(str)  # widget_id
    project_loaded = pyqtSignal()
    framework_changed = pyqtSignal(str)  # framework_name
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Project state
        self.project_data: Dict[str, Any] = {}
        self.project_path: Optional[str] = None
        self.target_framework: str = "PyQt6"
        
        # Widget management
        self.widgets: Dict[str, Dict[str, Any]] = {}
        self.widget_counter: int = 0
        self.selected_widget_id: Optional[str] = None
        
        # Undo/Redo system
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.max_undo_levels: int = 50
        self.unsaved_changes: bool = False
        
        # Canvas settings
        self.canvas_settings: Dict[str, Any] = {
            "grid_size": 20,
            "grid_visible": True,
            "snap_enabled": True,
            "zoom_level": 1.0
        }
        
        # Layer management
        self.layer_config: Dict[str, Any] = {
            "total_layers": 5,
            "layer_names": ["Background", "Content", "Controls", "Overlays", "Debug"]
        }
        
        # Initialize with default project
        self.new_project()
        self.logger.info("StateManager initialized")
    
    def new_project(self):
        """Create a new project with default settings."""
        self.project_data = {
            "name": "New Project",
            "framework": self.target_framework,
            "version": "1.0",
            "main_window": {
                "id": "main_window",
                "type": "MainWindow",
                "properties": {
                    "title": "My Application",
                    "geometry": [100, 100, 800, 600],
                    "resizable": True,
                    "colors": {
                        "background": "#F0F0F0",
                        "text": "#000000"
                    }
                }
            },
            "widgets": {},
            "canvas_settings": self.canvas_settings.copy(),
            "layer_config": self.layer_config.copy()
        }
        
        self.widgets.clear()
        self.widget_counter = 0
        self.selected_widget_id = None
        self.project_path = None
        self.unsaved_changes = False
        
        # Clear undo/redo stacks
        self.undo_stack.clear()
        self.redo_stack.clear()
        
        self.save_initial_state()
        self.state_changed.emit()
        self.logger.info("New project created")
    
    def save_initial_state(self):
        """Save the initial state without marking as unsaved changes."""
        state = self.get_current_state()
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)
    
    def save_state(self):
        """Save the current state for undo/redo."""
        state = self.get_current_state()
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Clear redo stack when new action is performed
        
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)
        
        self.unsaved_changes = True
        self.state_changed.emit()
        self.logger.debug("State saved for undo/redo")
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get the current complete state."""
        return {
            "project_data": copy.deepcopy(self.project_data),
            "widgets": copy.deepcopy(self.widgets),
            "widget_counter": self.widget_counter,
            "selected_widget_id": self.selected_widget_id,
            "canvas_settings": copy.deepcopy(self.canvas_settings),
            "layer_config": copy.deepcopy(self.layer_config)
        }
    
    def restore_state(self, state: Dict[str, Any]):
        """Restore state from saved state."""
        self.project_data = copy.deepcopy(state["project_data"])
        self.widgets = copy.deepcopy(state["widgets"])
        self.widget_counter = state["widget_counter"]
        self.selected_widget_id = state.get("selected_widget_id")
        self.canvas_settings = copy.deepcopy(state.get("canvas_settings", self.canvas_settings))
        self.layer_config = copy.deepcopy(state.get("layer_config", self.layer_config))
        
        self.state_changed.emit()
        if self.selected_widget_id:
            self.selection_changed.emit(self.selected_widget_id)
    
    def undo(self):
        """Undo the last action."""
        if len(self.undo_stack) > 1:  # Keep at least one state
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            
            # Restore previous state
            previous_state = self.undo_stack[-1]
            self.restore_state(previous_state)
            
            self.unsaved_changes = True
            self.logger.debug("Undo performed")
    
    def redo(self):
        """Redo the last undone action."""
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.restore_state(state)
            
            self.unsaved_changes = True
            self.logger.debug("Redo performed")
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 1
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self.unsaved_changes
    
    def mark_as_saved(self):
        """Mark the project as saved."""
        self.unsaved_changes = False
    
    def set_target_framework(self, framework: str):
        """Set the target framework."""
        if framework != self.target_framework:
            self.target_framework = framework
            self.project_data["framework"] = framework
            self.save_state()
            self.framework_changed.emit(framework)
            self.logger.info(f"Target framework changed to: {framework}")
    
    def get_target_framework(self) -> str:
        """Get the current target framework."""
        return self.target_framework
    
    def add_widget(self, widget_data: Dict[str, Any]) -> str:
        """Add a new widget and return its ID."""
        self.save_state()
        
        self.widget_counter += 1
        widget_id = f"widget_{self.widget_counter}"
        
        # Ensure widget has required properties
        widget_data = widget_data.copy()
        widget_data["id"] = widget_id
        
        if "properties" not in widget_data:
            widget_data["properties"] = {}
        
        # Set default properties
        properties = widget_data["properties"]
        if "name" not in properties:
            properties["name"] = f"{widget_data['type'].lower()}_{self.widget_counter}"
        if "geometry" not in properties:
            properties["geometry"] = [100, 100, 200, 100]  # x, y, width, height
        if "layer" not in properties:
            properties["layer"] = 2  # Default to content layer
        
        self.widgets[widget_id] = widget_data
        self.selected_widget_id = widget_id
        
        self.widget_added.emit(widget_id)
        self.selection_changed.emit(widget_id)
        self.logger.info(f"Widget added: {widget_id} ({widget_data['type']})")
        
        return widget_id
    
    def remove_widget(self, widget_id: str) -> bool:
        """Remove a widget."""
        if widget_id in self.widgets:
            self.save_state()
            
            widget_data = self.widgets[widget_id]
            del self.widgets[widget_id]
            
            # Clear selection if this widget was selected
            if self.selected_widget_id == widget_id:
                self.selected_widget_id = None
                self.selection_changed.emit(None)
            
            self.widget_removed.emit(widget_id)
            self.logger.info(f"Widget removed: {widget_id} ({widget_data['type']})")
            return True
        
        return False
    
    def get_widget(self, widget_id: str) -> Optional[Dict[str, Any]]:
        """Get widget data by ID."""
        return self.widgets.get(widget_id)
    
    def update_widget(self, widget_id: str, updates: Dict[str, Any]):
        """Update widget properties."""
        if widget_id in self.widgets:
            # Deep update of properties
            if "properties" in updates:
                if "properties" not in self.widgets[widget_id]:
                    self.widgets[widget_id]["properties"] = {}
                self.widgets[widget_id]["properties"].update(updates["properties"])
            
            # Update other fields
            for key, value in updates.items():
                if key != "properties":
                    self.widgets[widget_id][key] = value
            
            self.widget_modified.emit(widget_id)
            self.logger.debug(f"Widget updated: {widget_id}")
    
    def get_all_widgets(self) -> Dict[str, Dict[str, Any]]:
        """Get all widgets."""
        return self.widgets.copy()
    
    def set_selected_widget(self, widget_id: Optional[str]):
        """Set the currently selected widget."""
        if widget_id != self.selected_widget_id:
            self.selected_widget_id = widget_id
            self.selection_changed.emit(widget_id)
            self.logger.debug(f"Selection changed to: {widget_id}")
    
    def get_selected_widget(self) -> Optional[str]:
        """Get the currently selected widget ID."""
        return self.selected_widget_id
    
    def get_main_window_data(self) -> Dict[str, Any]:
        """Get main window data."""
        return self.project_data.get("main_window", {})
    
    def update_main_window(self, updates: Dict[str, Any]):
        """Update main window properties."""
        if "main_window" not in self.project_data:
            self.project_data["main_window"] = {}
        
        if "properties" in updates:
            if "properties" not in self.project_data["main_window"]:
                self.project_data["main_window"]["properties"] = {}
            self.project_data["main_window"]["properties"].update(updates["properties"])
        
        for key, value in updates.items():
            if key != "properties":
                self.project_data["main_window"][key] = value
        
        self.state_changed.emit()
    
    def get_project_data(self) -> Dict[str, Any]:
        """Get complete project data for export."""
        return {
            **self.project_data,
            "widgets": list(self.widgets.values()),
            "canvas_settings": self.canvas_settings,
            "layer_config": self.layer_config
        }
    
    def load_project_data(self, project_data: Dict[str, Any]):
        """Load project data from file."""
        self.project_data = project_data.copy()
        
        # Convert widgets list back to dictionary
        if "widgets" in project_data:
            self.widgets = {}
            for widget in project_data["widgets"]:
                if "id" in widget:
                    self.widgets[widget["id"]] = widget
            
            # Update widget counter
            if self.widgets:
                max_id = max([
                    int(w_id.split("_")[-1]) 
                    for w_id in self.widgets.keys() 
                    if w_id.startswith("widget_")
                ])
                self.widget_counter = max_id
        
        # Load settings
        if "canvas_settings" in project_data:
            self.canvas_settings.update(project_data["canvas_settings"])
        
        if "layer_config" in project_data:
            self.layer_config.update(project_data["layer_config"])
        
        if "framework" in project_data:
            self.target_framework = project_data["framework"]
        
        self.selected_widget_id = None
        self.unsaved_changes = False
        
        # Clear and reset undo/redo
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.save_initial_state()
        
        self.project_loaded.emit()
        self.state_changed.emit()
        self.logger.info("Project data loaded")
    
    def set_project_path(self, path: str):
        """Set the current project file path."""
        self.project_path = path
    
    def get_project_path(self) -> Optional[str]:
        """Get the current project file path."""
        return self.project_path
    
    def update_canvas_settings(self, settings: Dict[str, Any]):
        """Update canvas settings."""
        self.canvas_settings.update(settings)
        self.state_changed.emit()
    
    def get_canvas_settings(self) -> Dict[str, Any]:
        """Get canvas settings."""
        return self.canvas_settings.copy()
    
    def update_layer_config(self, config: Dict[str, Any]):
        """Update layer configuration."""
        self.layer_config.update(config)
        self.save_state()
    
    def get_layer_config(self) -> Dict[str, Any]:
        """Get layer configuration."""
        return self.layer_config.copy()