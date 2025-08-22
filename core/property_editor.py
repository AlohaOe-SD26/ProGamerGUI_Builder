"""
Property Editor - Dynamic property editing panel
"""

import logging
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
    QPushButton, QColorDialog, QFontDialog, QGroupBox, QScrollArea,
    QWidget, QTextEdit, QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette

class PropertyEditor(QFrame):
    """
    Dynamic property editor that shows and allows editing of widget properties.
    """
    
    # Signals
    property_changed = pyqtSignal(str, str, object)  # widget_id, property_path, value
    
    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.current_widget_id: Optional[str] = None
        self.property_widgets: Dict[str, QWidget] = {}
        self.updating_properties = False  # Prevent recursive updates
        
        self.setup_ui()
        self.connect_signals()
        
        self.logger.info("PropertyEditor initialized")
    
    def setup_ui(self):
        """Setup the property editor UI."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedWidth(350)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        self.title_label = QLabel("Properties")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        main_layout.addWidget(self.title_label)
        
        # Scroll area for properties
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Properties container widget
        self.properties_widget = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_widget)
        self.properties_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.properties_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.properties_widget)
        main_layout.addWidget(self.scroll_area)
        
        # Show default state
        self.show_no_selection()
    
    def connect_signals(self):
        """Connect to state manager signals."""
        self.state_manager.selection_changed.connect(self.set_selected_widget)
        self.state_manager.widget_modified.connect(self.refresh_properties)
        self.property_changed.connect(self.on_property_changed)
    
    def set_selected_widget(self, widget_id: Optional[str]):
        """Set the currently selected widget to edit."""
        if widget_id != self.current_widget_id:
            self.current_widget_id = widget_id
            self.rebuild_properties()
    
    def rebuild_properties(self):
        """Rebuild the entire property editor for the current widget."""
        # Clear existing widgets
        self.clear_properties()
        
        if not self.current_widget_id:
            self.show_no_selection()
            return
        
        # Get widget data
        if self.current_widget_id == "main_window":
            widget_data = self.state_manager.get_main_window_data()
            self.title_label.setText("Main Window Properties")
        else:
            widget_data = self.state_manager.get_widget(self.current_widget_id)
            if not widget_data:
                self.show_no_selection()
                return
            
            widget_type = widget_data.get("type", "Widget")
            self.title_label.setText(f"{widget_type} Properties")
        
        # Build property groups
        self.build_basic_properties(widget_data)
        self.build_geometry_properties(widget_data)
        self.build_appearance_properties(widget_data)
        self.build_font_properties(widget_data)
        self.build_specific_properties(widget_data)
        
        if self.current_widget_id != "main_window":
            self.build_layer_properties(widget_data)
            self.build_widget_actions()
    
    def clear_properties(self):
        """Clear all property widgets."""
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.property_widgets.clear()
    
    def show_no_selection(self):
        """Show the no selection state."""
        self.title_label.setText("Properties")
        
        no_selection_label = QLabel("No widget selected")
        no_selection_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_selection_label.setStyleSheet("color: #666666; font-style: italic; padding: 20px;")
        
        self.properties_layout.addWidget(no_selection_label)
    
    def create_property_group(self, title: str) -> QFormLayout:
        """Create a property group with a title."""
        group_box = QGroupBox(title)
        group_layout = QFormLayout(group_box)
        group_layout.setSpacing(5)
        
        self.properties_layout.addWidget(group_box)
        return group_layout
    
    def build_basic_properties(self, widget_data: Dict[str, Any]):
        """Build basic properties section."""
        layout = self.create_property_group("Basic")
        properties = widget_data.get("properties", {})
        
        # Widget name/ID
        if self.current_widget_id != "main_window":
            name_edit = QLineEdit(properties.get("name", ""))
            name_edit.textChanged.connect(
                lambda text: self.emit_property_change("properties.name", text)
            )
            layout.addRow("Name:", name_edit)
            self.property_widgets["name"] = name_edit
        
        # Title (for main window) or Text (for other widgets)
        if self.current_widget_id == "main_window":
            title_edit = QLineEdit(properties.get("title", ""))
            title_edit.textChanged.connect(
                lambda text: self.emit_property_change("properties.title", text)
            )
            layout.addRow("Title:", title_edit)
            self.property_widgets["title"] = title_edit
        else:
            text_edit = QLineEdit(properties.get("text", ""))
            text_edit.textChanged.connect(
                lambda text: self.emit_property_change("properties.text", text)
            )
            layout.addRow("Text:", text_edit)
            self.property_widgets["text"] = text_edit
        
        # Enabled state
        enabled_check = QCheckBox()
        enabled_check.setChecked(properties.get("enabled", True))
        enabled_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.enabled", checked)
        )
        layout.addRow("Enabled:", enabled_check)
        self.property_widgets["enabled"] = enabled_check
        
        # Visible state
        visible_check = QCheckBox()
        visible_check.setChecked(properties.get("visible", True))
        visible_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.visible", checked)
        )
        layout.addRow("Visible:", visible_check)
        self.property_widgets["visible"] = visible_check
    
    def build_geometry_properties(self, widget_data: Dict[str, Any]):
        """Build geometry properties section."""
        layout = self.create_property_group("Geometry")
        properties = widget_data.get("properties", {})
        geometry = properties.get("geometry", [0, 0, 100, 50])
        
        # X position
        x_spin = QSpinBox()
        x_spin.setRange(-9999, 9999)
        x_spin.setValue(geometry[0])
        x_spin.valueChanged.connect(
            lambda value: self.update_geometry_property(0, value)
        )
        layout.addRow("X:", x_spin)
        self.property_widgets["x"] = x_spin
        
        # Y position
        y_spin = QSpinBox()
        y_spin.setRange(-9999, 9999)
        y_spin.setValue(geometry[1])
        y_spin.valueChanged.connect(
            lambda value: self.update_geometry_property(1, value)
        )
        layout.addRow("Y:", y_spin)
        self.property_widgets["y"] = y_spin
        
        # Width
        width_spin = QSpinBox()
        width_spin.setRange(1, 9999)
        width_spin.setValue(geometry[2])
        width_spin.valueChanged.connect(
            lambda value: self.update_geometry_property(2, value)
        )
        layout.addRow("Width:", width_spin)
        self.property_widgets["width"] = width_spin
        
        # Height
        height_spin = QSpinBox()
        height_spin.setRange(1, 9999)
        height_spin.setValue(geometry[3])
        height_spin.valueChanged.connect(
            lambda value: self.update_geometry_property(3, value)
        )
        layout.addRow("Height:", height_spin)
        self.property_widgets["height"] = height_spin
    
    def build_appearance_properties(self, widget_data: Dict[str, Any]):
        """Build appearance properties section."""
        layout = self.create_property_group("Appearance")
        properties = widget_data.get("properties", {})
        colors = properties.get("colors", {})
        
        # Background color
        bg_color = colors.get("background", "#FFFFFF")
        bg_button = QPushButton()
        bg_button.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #ccc; min-height: 25px;")
        bg_button.setText(bg_color)
        bg_button.clicked.connect(
            lambda: self.choose_color("properties.colors.background", bg_color)
        )
        layout.addRow("Background:", bg_button)
        self.property_widgets["bg_color"] = bg_button
        
        # Foreground color
        fg_color = colors.get("foreground", "#000000")
        fg_button = QPushButton()
        fg_button.setStyleSheet(f"background-color: {fg_color}; border: 1px solid #ccc; min-height: 25px;")
        fg_button.setText(fg_color)
        fg_button.clicked.connect(
            lambda: self.choose_color("properties.colors.foreground", fg_color)
        )
        layout.addRow("Foreground:", fg_button)
        self.property_widgets["fg_color"] = fg_button
        
        # Border color
        border_color = colors.get("border", "#CCCCCC")
        border_button = QPushButton()
        border_button.setStyleSheet(f"background-color: {border_color}; border: 1px solid #ccc; min-height: 25px;")
        border_button.setText(border_color)
        border_button.clicked.connect(
            lambda: self.choose_color("properties.colors.border", border_color)
        )
        layout.addRow("Border:", border_button)
        self.property_widgets["border_color"] = border_button
    
    def build_font_properties(self, widget_data: Dict[str, Any]):
        """Build font properties section."""
        widget_type = widget_data.get("type", "")
        
        # Only show font properties for widgets that support text
        text_widgets = ["Button", "Label", "Entry", "Text", "Checkbox", "RadioButton"]
        if widget_type not in text_widgets and self.current_widget_id != "main_window":
            return
        
        layout = self.create_property_group("Font")
        properties = widget_data.get("properties", {})
        font_info = properties.get("font", {})
        
        # Font family
        family_combo = QComboBox()
        families = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Georgia"]
        family_combo.addItems(families)
        current_family = font_info.get("family", "Arial")
        if current_family in families:
            family_combo.setCurrentText(current_family)
        family_combo.currentTextChanged.connect(
            lambda text: self.emit_property_change("properties.font.family", text)
        )
        layout.addRow("Family:", family_combo)
        self.property_widgets["font_family"] = family_combo
        
        # Font size
        size_spin = QSpinBox()
        size_spin.setRange(6, 72)
        size_spin.setValue(font_info.get("size", 9))
        size_spin.valueChanged.connect(
            lambda value: self.emit_property_change("properties.font.size", value)
        )
        layout.addRow("Size:", size_spin)
        self.property_widgets["font_size"] = size_spin
        
        # Bold
        bold_check = QCheckBox()
        bold_check.setChecked(font_info.get("bold", False))
        bold_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.font.bold", checked)
        )
        layout.addRow("Bold:", bold_check)
        self.property_widgets["font_bold"] = bold_check
        
        # Italic
        italic_check = QCheckBox()
        italic_check.setChecked(font_info.get("italic", False))
        italic_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.font.italic", checked)
        )
        layout.addRow("Italic:", italic_check)
        self.property_widgets["font_italic"] = italic_check
    
    def build_specific_properties(self, widget_data: Dict[str, Any]):
        """Build widget-type specific properties."""
        widget_type = widget_data.get("type", "")
        properties = widget_data.get("properties", {})
        
        if widget_type == "Entry":
            self.build_entry_properties(properties)
        elif widget_type in ["Checkbox", "RadioButton"]:
            self.build_boolean_properties(properties)
        elif widget_type == "RadioButton":
            self.build_radio_properties(properties)
        elif widget_type in ["ComboBox", "ListBox"]:
            self.build_list_properties(properties)
        elif widget_type == "Text":
            self.build_text_properties(properties)
    
    def build_entry_properties(self, properties: Dict[str, Any]):
        """Build Entry widget specific properties."""
        layout = self.create_property_group("Entry Settings")
        
        # Placeholder text
        placeholder_edit = QLineEdit(properties.get("placeholder", ""))
        placeholder_edit.textChanged.connect(
            lambda text: self.emit_property_change("properties.placeholder", text)
        )
        layout.addRow("Placeholder:", placeholder_edit)
        self.property_widgets["placeholder"] = placeholder_edit
        
        # Read only
        readonly_check = QCheckBox()
        readonly_check.setChecked(properties.get("readonly", False))
        readonly_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.readonly", checked)
        )
        layout.addRow("Read Only:", readonly_check)
        self.property_widgets["readonly"] = readonly_check
    
    def build_boolean_properties(self, properties: Dict[str, Any]):
        """Build Checkbox/RadioButton specific properties."""
        layout = self.create_property_group("State")
        
        # Checked state
        checked_check = QCheckBox()
        checked_check.setChecked(properties.get("checked", False))
        checked_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.checked", checked)
        )
        layout.addRow("Checked:", checked_check)
        self.property_widgets["checked"] = checked_check
    
    def build_radio_properties(self, properties: Dict[str, Any]):
        """Build RadioButton specific properties."""
        layout = self.create_property_group("Radio Group")
        
        # Group name
        group_edit = QLineEdit(properties.get("group", "default"))
        group_edit.textChanged.connect(
            lambda text: self.emit_property_change("properties.group", text)
        )
        layout.addRow("Group:", group_edit)
        self.property_widgets["group"] = group_edit
    
    def build_list_properties(self, properties: Dict[str, Any]):
        """Build ComboBox/ListBox specific properties."""
        layout = self.create_property_group("Items")
        
        # Items list
        items_widget = QListWidget()
        items_widget.setMaximumHeight(150)
        
        # Load existing items
        items = properties.get("items", [])
        for item in items:
            items_widget.addItem(str(item))
        
        layout.addRow("Items:", items_widget)
        self.property_widgets["items_list"] = items_widget
        
        # Buttons for managing items
        buttons_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_list_item(items_widget))
        buttons_layout.addWidget(add_button)
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_list_item(items_widget))
        buttons_layout.addWidget(remove_button)
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.edit_list_item(items_widget))
        buttons_layout.addWidget(edit_button)
        
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        layout.addRow("", buttons_widget)
        
        # Connect list changes
        items_widget.itemChanged.connect(
            lambda: self.update_list_items(items_widget)
        )
    
    def build_text_properties(self, properties: Dict[str, Any]):
        """Build Text widget specific properties."""
        layout = self.create_property_group("Text Settings")
        
        # Word wrap
        wrap_check = QCheckBox()
        wrap_check.setChecked(properties.get("word_wrap", True))
        wrap_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.word_wrap", checked)
        )
        layout.addRow("Word Wrap:", wrap_check)
        self.property_widgets["word_wrap"] = wrap_check
        
        # Read only
        readonly_check = QCheckBox()
        readonly_check.setChecked(properties.get("readonly", False))
        readonly_check.toggled.connect(
            lambda checked: self.emit_property_change("properties.readonly", checked)
        )
        layout.addRow("Read Only:", readonly_check)
        self.property_widgets["text_readonly"] = readonly_check
    
    def build_layer_properties(self, widget_data: Dict[str, Any]):
        """Build layer properties section."""
        layout = self.create_property_group("Layer")
        properties = widget_data.get("properties", {})
        
        # Current layer
        layer_config = self.state_manager.get_layer_config()
        total_layers = layer_config.get("total_layers", 5)
        layer_names = layer_config.get("layer_names", [])
        
        layer_combo = QComboBox()
        for i in range(1, total_layers + 1):
            layer_name = layer_names[i-1] if i-1 < len(layer_names) else f"Layer {i}"
            layer_combo.addItem(f"{i}. {layer_name}")
        
        current_layer = properties.get("layer", 2)
        layer_combo.setCurrentIndex(current_layer - 1)
        layer_combo.currentIndexChanged.connect(
            lambda index: self.emit_property_change("properties.layer", index + 1)
        )
        layout.addRow("Layer:", layer_combo)
        self.property_widgets["layer"] = layer_combo
    
    def build_widget_actions(self):
        """Build widget action buttons."""
        layout = self.create_property_group("Actions")
        
        # Delete button
        delete_button = QPushButton("Delete Widget")
        delete_button.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        delete_button.clicked.connect(self.delete_current_widget)
        layout.addRow(delete_button)
        
        # Duplicate button
        duplicate_button = QPushButton("Duplicate Widget")
        duplicate_button.setStyleSheet("background-color: #4ecdc4; color: white; font-weight: bold;")
        duplicate_button.clicked.connect(self.duplicate_current_widget)
        layout.addRow(duplicate_button)
    
    def emit_property_change(self, property_path: str, value: Any):
        """Emit a property change signal."""
        if not self.updating_properties and self.current_widget_id:
            self.property_changed.emit(self.current_widget_id, property_path, value)
    
    def update_geometry_property(self, index: int, value: int):
        """Update a specific geometry property."""
        if self.current_widget_id:
            if self.current_widget_id == "main_window":
                widget_data = self.state_manager.get_main_window_data()
            else:
                widget_data = self.state_manager.get_widget(self.current_widget_id)
            
            if widget_data:
                geometry = widget_data.get("properties", {}).get("geometry", [0, 0, 100, 50]).copy()
                geometry[index] = value
                self.emit_property_change("properties.geometry", geometry)
    
    def choose_color(self, property_path: str, current_color: str):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(current_color), self)
        if color.isValid():
            color_hex = color.name()
            self.emit_property_change(property_path, color_hex)
            
            # Update button appearance
            button_key = property_path.split(".")[-1] + "_color"
            if button_key in self.property_widgets:
                button = self.property_widgets[button_key]
                button.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #ccc; min-height: 25px;")
                button.setText(color_hex)
    
    def add_list_item(self, list_widget: QListWidget):
        """Add a new item to the list."""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(self, "Add Item", "Enter item text:")
        if ok and text:
            list_widget.addItem(text)
            self.update_list_items(list_widget)
    
    def remove_list_item(self, list_widget: QListWidget):
        """Remove selected item from the list."""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            list_widget.takeItem(current_row)
            self.update_list_items(list_widget)
    
    def edit_list_item(self, list_widget: QListWidget):
        """Edit the selected list item."""
        current_item = list_widget.currentItem()
        if current_item:
            from PyQt6.QtWidgets import QInputDialog
            
            text, ok = QInputDialog.getText(self, "Edit Item", "Enter item text:", text=current_item.text())
            if ok:
                current_item.setText(text)
                self.update_list_items(list_widget)
    
    def update_list_items(self, list_widget: QListWidget):
        """Update the items property from the list widget."""
        items = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item:
                items.append(item.text())
        
        self.emit_property_change("properties.items", items)
    
    def delete_current_widget(self):
        """Delete the current widget."""
        if self.current_widget_id and self.current_widget_id != "main_window":
            self.state_manager.remove_widget(self.current_widget_id)
    
    def duplicate_current_widget(self):
        """Duplicate the current widget."""
        if self.current_widget_id and self.current_widget_id != "main_window":
            widget_data = self.state_manager.get_widget(self.current_widget_id)
            if widget_data:
                import copy
                
                # Create a copy with offset position
                new_data = copy.deepcopy(widget_data)
                geometry = new_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
                geometry[0] += 20
                geometry[1] += 20
                new_data["properties"]["geometry"] = geometry
                
                # Add the duplicate
                self.state_manager.add_widget(new_data)
    
    def on_property_changed(self, widget_id: str, property_path: str, value: Any):
        """Handle property change."""
        if widget_id == "main_window":
            # Update main window
            path_parts = property_path.split(".")
            if len(path_parts) >= 2 and path_parts[0] == "properties":
                if len(path_parts) == 2:
                    # Simple property
                    self.state_manager.update_main_window({
                        "properties": {path_parts[1]: value}
                    })
                elif len(path_parts) == 3:
                    # Nested property
                    current_data = self.state_manager.get_main_window_data()
                    nested_data = current_data.get("properties", {}).get(path_parts[1], {})
                    nested_data[path_parts[2]] = value
                    self.state_manager.update_main_window({
                        "properties": {path_parts[1]: nested_data}
                    })
        else:
            # Update widget
            path_parts = property_path.split(".")
            if len(path_parts) >= 2 and path_parts[0] == "properties":
                if len(path_parts) == 2:
                    # Simple property
                    self.state_manager.update_widget(widget_id, {
                        "properties": {path_parts[1]: value}
                    })
                elif len(path_parts) == 3:
                    # Nested property
                    current_data = self.state_manager.get_widget(widget_id)
                    if current_data:
                        nested_data = current_data.get("properties", {}).get(path_parts[1], {})
                        nested_data[path_parts[2]] = value
                        self.state_manager.update_widget(widget_id, {
                            "properties": {path_parts[1]: nested_data}
                        })
    
    def refresh_properties(self):
        """Refresh property values from the current widget data."""
        if not self.current_widget_id or self.updating_properties:
            return
        
        self.updating_properties = True
        
        try:
            if self.current_widget_id == "main_window":
                widget_data = self.state_manager.get_main_window_data()
            else:
                widget_data = self.state_manager.get_widget(self.current_widget_id)
            
            if not widget_data:
                return
            
            properties = widget_data.get("properties", {})
            
            # Update geometry properties
            geometry = properties.get("geometry", [0, 0, 100, 50])
            if "x" in self.property_widgets:
                self.property_widgets["x"].setValue(geometry[0])
            if "y" in self.property_widgets:
                self.property_widgets["y"].setValue(geometry[1])
            if "width" in self.property_widgets:
                self.property_widgets["width"].setValue(geometry[2])
            if "height" in self.property_widgets:
                self.property_widgets["height"].setValue(geometry[3])
            
            # Update other properties as needed
            # (Could be expanded to update all properties, but geometry is most common)
            
        finally:
            self.updating_properties = False