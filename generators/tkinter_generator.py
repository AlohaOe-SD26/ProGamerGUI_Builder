"""
Tkinter Generator - Code generator for Tkinter framework
"""

from typing import Dict, Any, List
from .base_generator import BaseGenerator, register_generator


class TkinterGenerator(BaseGenerator):
    """Code generator for Tkinter framework."""
    
    def __init__(self):
        super().__init__("Tkinter")
        self.supported_widgets = {
            "Button", "Label", "Entry", "Text", "Checkbox", "RadioButton",
            "ComboBox", "ListBox", "Frame", "Tabs", "Slider", "ProgressBar",
            "SpinBox", "ScrollArea"
        }
        self.dependencies = set()  # Tkinter is built into Python
        
        # Widget type mappings
        self.widget_class_map = {
            "Button": "tk.Button",
            "Label": "tk.Label", 
            "Entry": "tk.Entry",
            "Text": "tk.Text",
            "Checkbox": "tk.Checkbutton",
            "RadioButton": "tk.Radiobutton",
            "ComboBox": "ttk.Combobox",
            "ListBox": "tk.Listbox",
            "Frame": "tk.Frame",
            "Tabs": "ttk.Notebook",
            "Slider": "tk.Scale",
            "ProgressBar": "ttk.Progressbar",
            "SpinBox": "tk.Spinbox",
            "ScrollArea": "tk.Frame"  # Custom implementation needed
        }
    
    def get_file_extension(self) -> str:
        return ".py"
    
    def generate_imports(self, project_data: Dict[str, Any]) -> str:
        """Generate Tkinter import statements."""
        # Check if ttk widgets are used
        widgets = project_data.get("widgets", [])
        uses_ttk = any(widget.get("type") in ["ComboBox", "ProgressBar", "Tabs"] for widget in widgets)
        
        imports = [
            "import tkinter as tk",
            "from tkinter import messagebox"
        ]
        
        if uses_ttk:
            imports.append("from tkinter import ttk")
        
        return "\n".join(imports)
    
    def generate_main_file(self, project_data: Dict[str, Any]) -> str:
        """Generate the main Tkinter application file."""
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
        colors = properties.get("colors", {})
        
        # Class header
        code = [
            f"class {class_name}:",
            '    """Main application window."""',
            "",
            "    def __init__(self):",
            "        self.root = tk.Tk()",
            f'        self.root.title("{title}")',
            f"        self.root.geometry(\"{geometry[2]}x{geometry[3]}+{geometry[0]}+{geometry[1]}\")",
            ""
        ]
        
        # Background color
        if colors.get("background"):
            code.append(f'        self.root.configure(bg="{colors["background"]}")')
        
        code.extend([
            "        self.setup_ui()",
            "",
            "    def setup_ui(self):",
            '        """Initialize the user interface."""'
        ])
        
        # Generate widget creation code
        for widget in widgets:
            widget_id = widget.get("id", "")
            if widget_id in var_names:
                var_name = var_names[widget_id]
                widget_code = self.generate_widget_code(widget, "self")
                # Add proper indentation
                indented_code = self.format_code(widget_code, 2)
                code.extend(["", indented_code])
        
        # Generate event handlers
        event_handlers = self.generate_event_handlers(widgets, var_names)
        if event_handlers:
            code.extend(["", event_handlers])
        
        # Add run method
        code.extend([
            "",
            "    def run(self):",
            '        """Start the main event loop."""',
            "        self.root.mainloop()"
        ])
        
        return "\n".join(code)
    
    def generate_widget_code(self, widget_data: Dict[str, Any], parent_var: str = "self") -> str:
        """Generate code for a single Tkinter widget."""
        widget_type = widget_data.get("type", "")
        properties = widget_data.get("properties", {})
        
        # Get Tkinter class name
        tk_class = self.widget_class_map.get(widget_type, "tk.Widget")
        var_name = self.sanitize_name(properties.get("name", "widget"))
        
        code_parts = []
        
        # Widget creation with common options
        options = []
        
        # Text property
        if widget_type in ["Button", "Label", "Checkbox", "RadioButton"] and "text" in properties:
            text = properties["text"].replace('"', '\\"')
            options.append(f'text="{text}"')
        
        # Colors
        colors = properties.get("colors", {})
        if colors.get("background"):
            options.append(f'bg="{colors["background"]}"')
        if colors.get("foreground"):
            options.append(f'fg="{colors["foreground"]}"')
        
        # Font
        font_data = properties.get("font", {})
        if font_data:
            family = font_data.get("family", "Arial")
            size = font_data.get("size", 9)
            weight = "bold" if font_data.get("bold", False) else "normal"
            slant = "italic" if font_data.get("italic", False) else "roman"
            options.append(f'font=("{family}", {size}, "{weight}", "{slant}")')
        
        # Widget-specific options
        widget_options = self.generate_widget_specific_options(widget_type, widget_data)
        options.extend(widget_options)
        
        # Create widget
        parent_ref = f"{parent_var}.root" if parent_var == "self" else parent_var
        options_str = ", ".join(options)
        if options_str:
            code_parts.append(f'{parent_var}.{var_name} = {tk_class}({parent_ref}, {options_str})')
        else:
            code_parts.append(f'{parent_var}.{var_name} = {tk_class}({parent_ref})')
        
        # Geometry (place method for absolute positioning)
        geometry = properties.get("geometry", [0, 0, 100, 50])
        x, y, width, height = geometry
        code_parts.append(f'{parent_var}.{var_name}.place(x={x}, y={y}, width={width}, height={height})')
        
        # Widget-specific post-creation code
        post_code = self.generate_widget_post_creation_code(widget_type, widget_data, f'{parent_var}.{var_name}')
        if post_code:
            code_parts.append(post_code)
        
        # Enabled state
        if not properties.get("enabled", True):
            code_parts.append(f'{parent_var}.{var_name}.configure(state="disabled")')
        
        return "\n".join(code_parts)
    
    def generate_widget_specific_options(self, widget_type: str, widget_data: Dict[str, Any]) -> List[str]:
        """Generate widget-type specific options."""
        properties = widget_data.get("properties", {})
        options = []
        
        if widget_type == "Entry":
            if "placeholder" in properties:
                # Tkinter doesn't have built-in placeholder, we'll add it later
                pass
            if properties.get("readonly", False):
                options.append('state="readonly"')
        
        elif widget_type == "Text":
            if properties.get("readonly", False):
                options.append('state="disabled"')
            if not properties.get("word_wrap", True):
                options.append('wrap="none"')
        
        elif widget_type == "Checkbox":
            if properties.get("checked", False):
                # We'll handle this in post-creation code
                pass
        
        elif widget_type == "RadioButton":
            group = properties.get("group", "default")
            options.append(f'variable=self.{group}_var')
            if properties.get("checked", False):
                # We'll handle this in post-creation code
                pass
        
        elif widget_type == "Button":
            action = properties.get("action", {})
            if action.get("type") != "none":
                var_name = self.sanitize_name(properties.get("name", "widget"))
                options.append(f'command=self.on_{var_name}_clicked')
        
        elif widget_type == "Slider":
            minimum = properties.get("minimum", 0)
            maximum = properties.get("maximum", 100)
            value = properties.get("value", 50)
            orientation = properties.get("orientation", "horizontal")
            
            options.extend([
                f'from_={minimum}',
                f'to={maximum}',
                f'orient="{orientation}"',
                f'length=200'
            ])
        
        elif widget_type == "SpinBox":
            minimum = properties.get("minimum", 0)
            maximum = properties.get("maximum", 99)
            value = properties.get("value", 0)
            
            options.extend([
                f'from_={minimum}',
                f'to={maximum}',
                f'value={value}'
            ])
        
        return options
    
    def generate_widget_post_creation_code(self, widget_type: str, widget_data: Dict[str, Any], var_ref: str) -> str:
        """Generate post-creation code for widgets."""
        properties = widget_data.get("properties", {})
        code_parts = []
        
        if widget_type == "Entry" and "placeholder" in properties:
            placeholder = properties["placeholder"].replace('"', '\\"')
            code_parts.extend([
                f'{var_ref}.insert(0, "{placeholder}")',
                f'{var_ref}.configure(fg="grey")',
                f'{var_ref}.bind("<FocusIn>", lambda e: self.clear_placeholder({var_ref}, "{placeholder}"))',
                f'{var_ref}.bind("<FocusOut>", lambda e: self.restore_placeholder({var_ref}, "{placeholder}"))'
            ])
        
        elif widget_type in ["ComboBox", "ListBox"]:
            items = properties.get("items", [])
            if items and widget_type == "ComboBox":
                items_str = ", ".join(f'"{item}"' for item in items)
                code_parts.append(f'{var_ref}["values"] = ({items_str})')
            elif items and widget_type == "ListBox":
                for item in items:
                    code_parts.append(f'{var_ref}.insert("end", "{item}")')
        
        elif widget_type == "Checkbox" and properties.get("checked", False):
            code_parts.append(f'{var_ref}.select()')
        
        elif widget_type == "RadioButton":
            group = properties.get("group", "default")
            # Create StringVar for radio group if not exists
            code_parts.append(f'if not hasattr(self, "{group}_var"): self.{group}_var = tk.StringVar()')
            if properties.get("checked", False):
                var_name = self.sanitize_name(properties.get("name", "widget"))
                code_parts.append(f'self.{group}_var.set("{var_name}")')
        
        elif widget_type == "Tabs":
            tab_data = properties.get("tab_data", [])
            for i, tab_info in enumerate(tab_data):
                tab_title = tab_info.get("title", f"Tab {i+1}").replace('"', '\\"')
                code_parts.append(f'tab_{i} = tk.Frame({var_ref})')
                code_parts.append(f'{var_ref}.add(tab_{i}, text="{tab_title}")')
        
        elif widget_type == "ProgressBar":
            minimum = properties.get("minimum", 0)
            maximum = properties.get("maximum", 100)
            value = properties.get("value", 0)
            
            code_parts.extend([
                f'{var_ref}["maximum"] = {maximum}',
                f'{var_ref}["value"] = {value}'
            ])
        
        return "\n".join(code_parts)
    
    def generate_layout_code(self, container_data: Dict[str, Any], child_widgets: List[Dict[str, Any]]) -> str:
        """Generate layout management code for Tkinter."""
        # Tkinter uses place() for absolute positioning by default
        # Could implement pack() or grid() layouts here
        return ""
    
    def generate_event_handlers(self, widgets: List[Dict[str, Any]], var_names: Dict[str, str]) -> str:
        """Generate event handler methods."""
        handlers = []
        
        # Add placeholder handlers
        has_placeholder = any(
            widget.get("type") == "Entry" and "placeholder" in widget.get("properties", {})
            for widget in widgets
        )
        
        if has_placeholder:
            handlers.extend([
                "    def clear_placeholder(self, entry, placeholder):",
                "        if entry.get() == placeholder:",
                "            entry.delete(0, 'end')",
                "            entry.configure(fg='black')",
                "",
                "    def restore_placeholder(self, entry, placeholder):",
                "        if not entry.get():",
                "            entry.insert(0, placeholder)",
                "            entry.configure(fg='grey')"
            ])
        
        # Button handlers
        for widget in widgets:
            widget_type = widget.get("type", "")
            properties = widget.get("properties", {})
            widget_id = widget.get("id", "")
            
            if widget_id in var_names and widget_type == "Button":
                var_name = var_names[widget_id]
                action = properties.get("action", {})
                if action.get("type") != "none":
                    handler = self.generate_button_handler(var_name, action)
                    if handlers:
                        handlers.append("")
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
            code.append(f'        messagebox.showinfo("Message", "{target}")')
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
    app = {class_name}()
    app.run()


if __name__ == '__main__':
    main()"""
    
    def generate_color_code(self, color: str) -> str:
        """Generate Tkinter color code."""
        return f'"{color}"'
    
    def generate_font_code(self, font_data: Dict[str, Any]) -> str:
        """Generate Tkinter font code."""
        family = font_data.get("family", "Arial")
        size = font_data.get("size", 9)
        weight = "bold" if font_data.get("bold", False) else "normal"
        slant = "italic" if font_data.get("italic", False) else "roman"
        return f'("{family}", {size}, "{weight}", "{slant}")'
    
    def generate_geometry_code(self, geometry: List[int]) -> str:
        """Generate Tkinter geometry code."""
        x, y, width, height = geometry
        return f"{width}x{height}+{x}+{y}"


# Register the Tkinter generator
register_generator("Tkinter", TkinterGenerator())