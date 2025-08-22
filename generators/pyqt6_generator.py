"""
PyQt6 Generator - Code generator for PyQt6 framework
"""

from typing import Dict, Any, List, Set
from .base_generator import BaseGenerator, WidgetCodeGenerator, register_generator


class PyQt6Generator(BaseGenerator):
    """Code generator for PyQt6 framework."""
    
    def __init__(self):
        super().__init__("PyQt6")
        self.supported_widgets = {
            "Button", "Label", "Entry", "Text", "Checkbox", "RadioButton",
            "ComboBox", "ListBox", "Frame", "Tabs", "Slider", "ProgressBar",
            "SpinBox", "ScrollArea", "GroupBox", "Splitter", "StackedWidget"
        }
        self.dependencies = {"PyQt6"}
        
        # Widget type mappings
        self.widget_class_map = {
            "Button": "QPushButton",
            "Label": "QLabel", 
            "Entry": "QLineEdit",
            "Text": "QTextEdit",
            "Checkbox": "QCheckBox",
            "RadioButton": "QRadioButton",
            "ComboBox": "QComboBox",
            "ListBox": "QListWidget",
            "Frame": "QFrame",
            "Tabs": "QTabWidget",
            "Slider": "QSlider",
            "ProgressBar": "QProgressBar",
            "SpinBox": "QSpinBox",
            "ScrollArea": "QScrollArea",
            "GroupBox": "QGroupBox",
            "Splitter": "QSplitter",
            "StackedWidget": "QStackedWidget"
        }
    
    def get_file_extension(self) -> str:
        return ".py"
    
    def generate_imports(self, project_data: Dict[str, Any]) -> str:
        """Generate PyQt6 import statements."""
        # Analyze used widgets to determine required imports
        widgets = project_data.get("widgets", [])
        used_widgets = set(widget.get("type") for widget in widgets)
        
        # Base imports
        imports = [
            "import sys",
            "from PyQt6.QtWidgets import ("
        ]
        
        # Required widget classes
        widget_classes = {"QApplication", "QMainWindow", "QWidget"}
        
        for widget_type in used_widgets:
            qt_class = self.widget_class_map.get(widget_type)
            if qt_class:
                widget_classes.add(qt_class)
        
        # Layout classes
        widget_classes.update({"QVBoxLayout", "QHBoxLayout", "QGridLayout"})
        
        # Sort and format widget imports
        sorted_classes = sorted(widget_classes)
        for i, class_name in enumerate(sorted_classes):
            prefix = "    " if i == 0 else "    "
            suffix = "," if i < len(sorted_classes) - 1 else ""
            imports.append(f"{prefix}{class_name}{suffix}")
        
        imports.append(")")
        
        # Additional imports
        imports.extend([
            "from PyQt6.QtCore import Qt",
            "from PyQt6.QtGui import QFont, QColor"
        ])
        
        return "\n".join(imports)
    
    def generate_main_file(self, project_data: Dict[str, Any]) -> str:
        """Generate the main PyQt6 application file."""
        project_name = project_data.get("name", "MyApplication").replace(" ", "")
        main_window_data = project_data.get("main_window", {})
        widgets = project_data.get("widgets", [])
        
        # Resolve variable names
        var_names = self.resolve_variable_names(widgets)
        
        # Generate code sections
        imports = self.generate_imports(project_data)
        class_def = self.generate_class_definition(project_name, main_window_data, widgets, var_names)
        main_function = self.generate_main_function(project_name)
        
        return f"""{imports}


{class_def}


{main_function}"""
    
    def generate_class_definition(self, class_name: str, main_window_data: Dict[str, Any], 
                                widgets: List[Dict[str, Any]], var_names: Dict[str, str]) -> str:
        """Generate the main window class definition."""
        properties = main_window_data.get("properties", {})
        title = properties.get("title", "My Application")
        geometry = properties.get("geometry", [100, 100, 800, 600])
        
        # Class header
        code = [
            f"class {class_name}(QMainWindow):",
            '    """Main application window."""',
            "",
            "    def __init__(self):",
            "        super().__init__()",
            f'        self.setWindowTitle("{title}")',
            f"        self.setGeometry({self.generate_geometry_code(geometry)})",
            "",
            "        # Setup central widget",
            "        self.central_widget = QWidget()",
            "        self.setCentralWidget(self.central_widget)",
            "",
            "        self.setup_ui()",
            "",
            "    def setup_ui(self):",
            '        """Initialize the user interface."""'
        ]
        
        # Generate widget creation code
        for widget in widgets:
            widget_id = widget.get("id", "")
            if widget_id in var_names:
                var_name = var_names[widget_id]
                widget_code = self.generate_widget_code(widget, "self")
                # Add proper indentation
                indented_code = self.format_code(widget_code, 2)
                code.extend(["", indented_code])
        
        # Generate layout code if needed
        layout_code = self.generate_main_layout_code(widgets, var_names)
        if layout_code:
            code.extend(["", "        # Setup layout", layout_code])
        
        # Generate event handlers
        event_handlers = self.generate_event_handlers(widgets, var_names)
        if event_handlers:
            code.extend(["", event_handlers])
        
        return "\n".join(code)
    
    def generate_widget_code(self, widget_data: Dict[str, Any], parent_var: str = "self") -> str:
        """Generate code for a single PyQt6 widget."""
        widget_type = widget_data.get("type", "")
        properties = widget_data.get("properties", {})
        
        # Get Qt class name
        qt_class = self.widget_class_map.get(widget_type, "QWidget")
        var_name = self.sanitize_name(properties.get("name", "widget"))
        
        code_parts = []
        
        # Widget creation
        if widget_type in ["Button", "Label", "Checkbox", "RadioButton", "GroupBox"]:
            text = properties.get("text", "")
            code_parts.append(f'{parent_var}.{var_name} = {qt_class}("{text}", {parent_var}.central_widget)')
        else:
            code_parts.append(f'{parent_var}.{var_name} = {qt_class}({parent_var}.central_widget)')
        
        # Geometry
        geometry = properties.get("geometry", [0, 0, 100, 50])
        code_parts.append(f'{parent_var}.{var_name}.setGeometry({self.generate_geometry_code(geometry)})')
        
        # Widget-specific properties
        widget_specific_code = self.generate_widget_specific_code(widget_type, widget_data, f'{parent_var}.{var_name}')
        if widget_specific_code:
            code_parts.append(widget_specific_code)
        
        # Common properties
        common_code = self.generate_common_properties_code(widget_data, f'{parent_var}.{var_name}')
        if common_code:
            code_parts.append(common_code)
        
        return "\n".join(code_parts)
    
    def generate_widget_specific_code(self, widget_type: str, widget_data: Dict[str, Any], var_ref: str) -> str:
        """Generate widget-type specific property code."""
        properties = widget_data.get("properties", {})
        code_parts = []
        
        if widget_type == "Entry":
            if "placeholder" in properties:
                placeholder = properties["placeholder"].replace('"', '\\"')
                code_parts.append(f'{var_ref}.setPlaceholderText("{placeholder}")')
            if properties.get("readonly", False):
                code_parts.append(f'{var_ref}.setReadOnly(True)')
        
        elif widget_type == "Text":
            if properties.get("readonly", False):
                code_parts.append(f'{var_ref}.setReadOnly(True)')
            if not properties.get("word_wrap", True):
                code_parts.append(f'{var_ref}.setWordWrapMode(QTextOption.WrapMode.NoWrap)')
        
        elif widget_type in ["Checkbox", "RadioButton"]:
            if properties.get("checked", False):
                code_parts.append(f'{var_ref}.setChecked(True)')
        
        elif widget_type in ["ComboBox", "ListBox"]:
            items = properties.get("items", [])
            if items:
                items_str = ", ".join(f'"{item}"' for item in items)
                code_parts.append(f'{var_ref}.addItems([{items_str}])')
        
        elif widget_type == "Slider":
            minimum = properties.get("minimum", 0)
            maximum = properties.get("maximum", 100)
            value = properties.get("value", 50)
            orientation = properties.get("orientation", "horizontal")
            
            qt_orientation = "Qt.Orientation.Horizontal" if orientation == "horizontal" else "Qt.Orientation.Vertical"
            code_parts.append(f'{var_ref}.setOrientation({qt_orientation})')
            code_parts.append(f'{var_ref}.setMinimum({minimum})')
            code_parts.append(f'{var_ref}.setMaximum({maximum})')
            code_parts.append(f'{var_ref}.setValue({value})')
        
        elif widget_type == "ProgressBar":
            minimum = properties.get("minimum", 0)
            maximum = properties.get("maximum", 100)
            value = properties.get("value", 0)
            
            code_parts.append(f'{var_ref}.setMinimum({minimum})')
            code_parts.append(f'{var_ref}.setMaximum({maximum})')
            code_parts.append(f'{var_ref}.setValue({value})')
        
        elif widget_type == "SpinBox":
            minimum = properties.get("minimum", 0)
            maximum = properties.get("maximum", 99)
            value = properties.get("value", 0)
            
            code_parts.append(f'{var_ref}.setMinimum({minimum})')
            code_parts.append(f'{var_ref}.setMaximum({maximum})')
            code_parts.append(f'{var_ref}.setValue({value})')
        
        elif widget_type == "Tabs":
            tab_data = properties.get("tab_data", [])
            for i, tab_info in enumerate(tab_data):
                tab_title = tab_info.get("title", f"Tab {i+1}").replace('"', '\\"')
                code_parts.append(f'tab_{i} = QWidget()')
                code_parts.append(f'{var_ref}.addTab(tab_{i}, "{tab_title}")')
        
        return "\n".join(code_parts)
    
    def generate_common_properties_code(self, widget_data: Dict[str, Any], var_ref: str) -> str:
        """Generate code for common widget properties."""
        properties = widget_data.get("properties", {})
        code_parts = []
        
        # Enabled state
        if not properties.get("enabled", True):
            code_parts.append(f'{var_ref}.setEnabled(False)')
        
        # Visible state
        if not properties.get("visible", True):
            code_parts.append(f'{var_ref}.setVisible(False)')
        
        # Font
        font_data = properties.get("font", {})
        if font_data:
            font_code = self.generate_font_code(font_data)
            code_parts.append(f'{var_ref}_font = QFont({font_code})')
            if font_data.get("bold", False):
                code_parts.append(f'{var_ref}_font.setBold(True)')
            if font_data.get("italic", False):
                code_parts.append(f'{var_ref}_font.setItalic(True)')
            code_parts.append(f'{var_ref}.setFont({var_ref}_font)')
        
        # Colors (using stylesheet)
        colors = properties.get("colors", {})
        if colors:
            style_parts = []
            if "background" in colors:
                style_parts.append(f"background-color: {colors['background']}")
            if "foreground" in colors:
                style_parts.append(f"color: {colors['foreground']}")
            if "border" in colors:
                style_parts.append(f"border: 1px solid {colors['border']}")
            
            if style_parts:
                style_str = "; ".join(style_parts) + ";"
                code_parts.append(f'{var_ref}.setStyleSheet("{style_str}")')
        
        return "\n".join(code_parts)
    
    def generate_layout_code(self, container_data: Dict[str, Any], child_widgets: List[Dict[str, Any]]) -> str:
        """Generate layout management code for PyQt6."""
        layout_info = container_data.get("properties", {}).get("layout", {})
        layout_type = layout_info.get("type", "absolute")
        
        if layout_type == "grid":
            return self.generate_grid_layout_code(container_data, child_widgets)
        elif layout_type == "flow":
            return self.generate_flow_layout_code(container_data, child_widgets)
        else:
            # Absolute positioning - no layout manager needed
            return ""
    
    def generate_grid_layout_code(self, container_data: Dict[str, Any], child_widgets: List[Dict[str, Any]]) -> str:
        """Generate QGridLayout code."""
        container_name = self.sanitize_name(container_data.get("properties", {}).get("name", "container"))
        
        code = [
            f'{container_name}_layout = QGridLayout({container_name})',
            f'{container_name}.setLayout({container_name}_layout)'
        ]
        
        # Add widgets to grid
        for i, widget in enumerate(child_widgets):
            widget_name = self.sanitize_name(widget.get("properties", {}).get("name", f"widget_{i}"))
            row = i // 2  # Simple grid arrangement
            col = i % 2
            code.append(f'{container_name}_layout.addWidget({widget_name}, {row}, {col})')
        
        return "\n".join(code)
    
    def generate_flow_layout_code(self, container_data: Dict[str, Any], child_widgets: List[Dict[str, Any]]) -> str:
        """Generate QVBoxLayout or QHBoxLayout code."""
        container_name = self.sanitize_name(container_data.get("properties", {}).get("name", "container"))
        
        # Use vertical layout by default
        code = [
            f'{container_name}_layout = QVBoxLayout({container_name})',
            f'{container_name}.setLayout({container_name}_layout)'
        ]
        
        # Add widgets to layout
        for widget in child_widgets:
            widget_name = self.sanitize_name(widget.get("properties", {}).get("name", "widget"))
            code.append(f'{container_name}_layout.addWidget({widget_name})')
        
        return "\n".join(code)
    
    def generate_main_layout_code(self, widgets: List[Dict[str, Any]], var_names: Dict[str, str]) -> str:
        """Generate main window layout code if using layout managers."""
        # For now, assume absolute positioning
        return ""
    
    def generate_event_handlers(self, widgets: List[Dict[str, Any]], var_names: Dict[str, str]) -> str:
        """Generate event handler methods."""
        handlers = []
        
        for widget in widgets:
            widget_type = widget.get("type", "")
            properties = widget.get("properties", {})
            widget_id = widget.get("id", "")
            
            if widget_id in var_names:
                var_name = var_names[widget_id]
                
                if widget_type == "Button":
                    action = properties.get("action", {})
                    if action.get("type") != "none":
                        handler = self.generate_button_handler(var_name, action)
                        handlers.append(handler)
        
        return "\n".join(handlers)
    
    def generate_button_handler(self, button_name: str, action: Dict[str, Any]) -> str:
        """Generate button click handler."""
        method_name = f"on_{button_name}_clicked"
        action_type = action.get("type", "none")
        
        code = [
            f"    def {method_name}(self):",
            f'        """Handle {button_name} click event."""'
        ]
        
        if action_type == "message":
            target = action.get("target", "Hello!")
            code.append(f'        from PyQt6.QtWidgets import QMessageBox')
            code.append(f'        QMessageBox.information(self, "Message", "{target}")')
        elif action_type == "function":
            target = action.get("target", "custom_function")
            code.append(f'        self.{target}()')
        else:
            code.append(f'        # TODO: Implement {action_type} action')
            code.append(f'        pass')
        
        return "\n".join(code)
    
    def generate_main_function(self, class_name: str) -> str:
        """Generate the main function."""
        return f"""def main():
    '''Main function to run the application.'''
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = {class_name}()
    window.show()
    
    # Run the application event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()"""
    
    def generate_color_code(self, color: str) -> str:
        """Generate PyQt6 color code."""
        return f'QColor("{color}")'
    
    def generate_font_code(self, font_data: Dict[str, Any]) -> str:
        """Generate PyQt6 font code."""
        family = font_data.get("family", "Arial")
        size = font_data.get("size", 9)
        return f'"{family}", {size}'
    
    def generate_geometry_code(self, geometry: List[int]) -> str:
        """Generate PyQt6 geometry code."""
        x, y, width, height = geometry
        return f"{x}, {y}, {width}, {height}"


# Register the PyQt6 generator
register_generator("PyQt6", PyQt6Generator())