"""
Base Generator - Abstract base class for framework-specific code generators
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
import re


class BaseGenerator(ABC):
    """
    Abstract base class for all code generators.
    Each framework (PyQt6, Tkinter, etc.) should have its own generator implementation.
    """
    
    def __init__(self, framework_name: str):
        self.framework_name = framework_name
        self.supported_widgets: Set[str] = set()
        self.dependencies: Set[str] = set()
        
    @abstractmethod
    def generate_main_file(self, project_data: Dict[str, Any]) -> str:
        """Generate the main application file content."""
        pass
    
    @abstractmethod
    def generate_widget_code(self, widget_data: Dict[str, Any], parent_var: str = "self") -> str:
        """Generate code for a single widget."""
        pass
    
    @abstractmethod
    def generate_layout_code(self, container_data: Dict[str, Any], child_widgets: List[Dict[str, Any]]) -> str:
        """Generate layout management code for a container."""
        pass
    
    @abstractmethod
    def generate_imports(self, project_data: Dict[str, Any]) -> str:
        """Generate import statements for the project."""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for generated files (e.g., '.py')."""
        pass
    
    def generate_project(self, project_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate complete project files.
        
        Returns:
            Dictionary mapping filenames to their content
        """
        files = {}
        
        # Generate main file
        main_filename = f"main{self.get_file_extension()}"
        files[main_filename] = self.generate_main_file(project_data)
        
        # Generate additional files if needed (styles, resources, etc.)
        additional_files = self.generate_additional_files(project_data)
        files.update(additional_files)
        
        return files
    
    def generate_additional_files(self, project_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate additional project files (styles, resources, etc.)."""
        return {}
    
    def get_dependencies(self) -> List[str]:
        """Get list of required dependencies for this framework."""
        return list(self.dependencies)
    
    def supports_widget(self, widget_type: str) -> bool:
        """Check if this generator supports a specific widget type."""
        return widget_type in self.supported_widgets
    
    def sanitize_name(self, name: str) -> str:
        """Sanitize a name to be a valid Python identifier."""
        # Remove invalid characters and ensure it starts with letter/underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        return sanitized or "widget"
    
    def resolve_variable_names(self, widgets: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Resolve variable names for all widgets, ensuring uniqueness.
        
        Returns:
            Dictionary mapping widget IDs to their resolved variable names
        """
        name_counts = {}
        resolved_names = {}
        
        for widget in widgets:
            widget_id = widget.get("id", "")
            base_name = widget.get("properties", {}).get("name", "widget")
            base_name = self.sanitize_name(base_name)
            
            # Ensure uniqueness
            if base_name in name_counts:
                name_counts[base_name] += 1
                final_name = f"{base_name}_{name_counts[base_name]}"
            else:
                name_counts[base_name] = 0
                final_name = base_name
            
            resolved_names[widget_id] = final_name
        
        return resolved_names
    
    def generate_color_code(self, color: str) -> str:
        """Generate framework-specific color code."""
        # Default implementation - override in specific generators
        return f'"{color}"'
    
    def generate_font_code(self, font_data: Dict[str, Any]) -> str:
        """Generate framework-specific font code."""
        # Default implementation - override in specific generators
        family = font_data.get("family", "Arial")
        size = font_data.get("size", 9)
        return f'"{family}", {size}'
    
    def generate_geometry_code(self, geometry: List[int]) -> str:
        """Generate framework-specific geometry code."""
        # Default implementation - override in specific generators
        x, y, width, height = geometry
        return f"{x}, {y}, {width}, {height}"
    
    def get_widget_creation_template(self, widget_type: str) -> str:
        """Get the template for creating a specific widget type."""
        # Override in specific generators
        return f"# Widget creation for {widget_type} not implemented"
    
    def format_code(self, code: str, indent_level: int = 0) -> str:
        """Format code with proper indentation."""
        lines = code.strip().split('\n')
        indent = "    " * indent_level
        return '\n'.join(f"{indent}{line}" if line.strip() else "" for line in lines)
    
    def generate_event_handler_stub(self, widget_name: str, event_type: str) -> str:
        """Generate a stub for an event handler."""
        method_name = f"on_{widget_name}_{event_type}"
        return f"""
def {method_name}(self):
    '''Handle {event_type} event for {widget_name}'''
    # TODO: Implement event handler
    pass
"""


class WidgetCodeGenerator(ABC):
    """
    Abstract base class for widget-specific code generators.
    Each widget type can have its own specialized generator.
    """
    
    def __init__(self, widget_type: str, framework_name: str):
        self.widget_type = widget_type
        self.framework_name = framework_name
    
    @abstractmethod
    def generate_creation_code(self, widget_data: Dict[str, Any], var_name: str, parent_var: str) -> str:
        """Generate code to create the widget."""
        pass
    
    @abstractmethod
    def generate_property_code(self, widget_data: Dict[str, Any], var_name: str) -> str:
        """Generate code to set widget properties."""
        pass
    
    def generate_complete_code(self, widget_data: Dict[str, Any], var_name: str, parent_var: str) -> str:
        """Generate complete widget code (creation + properties)."""
        code_parts = [
            self.generate_creation_code(widget_data, var_name, parent_var),
            self.generate_property_code(widget_data, var_name)
        ]
        return '\n'.join(part for part in code_parts if part.strip())


# Global registry of available generators
_GENERATORS_REGISTRY: Dict[str, BaseGenerator] = {}


def register_generator(framework_name: str, generator: BaseGenerator):
    """Register a generator for a specific framework."""
    _GENERATORS_REGISTRY[framework_name] = generator


def get_generator(framework_name: str) -> Optional[BaseGenerator]:
    """Get the generator for a specific framework."""
    return _GENERATORS_REGISTRY.get(framework_name)


def get_available_generators() -> Dict[str, BaseGenerator]:
    """Get all available generators."""
    return _GENERATORS_REGISTRY.copy()


def list_supported_frameworks() -> List[str]:
    """Get list of all supported frameworks."""
    return list(_GENERATORS_REGISTRY.keys())


class CodeTemplate:
    """
    Helper class for managing code templates with variable substitution.
    """
    
    def __init__(self, template: str):
        self.template = template
    
    def render(self, **kwargs) -> str:
        """Render the template with the provided variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    @classmethod
    def from_file(cls, filepath: str) -> 'CodeTemplate':
        """Load template from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls(f.read())


class LayoutManager(ABC):
    """
    Abstract base class for layout managers.
    Different frameworks may have different layout systems.
    """
    
    def __init__(self, layout_type: str):
        self.layout_type = layout_type
    
    @abstractmethod
    def generate_layout_code(self, container_var: str, widgets: List[Dict[str, Any]], 
                           widget_vars: Dict[str, str]) -> str:
        """Generate layout management code."""
        pass
    
    @abstractmethod
    def supports_framework(self, framework: str) -> bool:
        """Check if this layout manager supports the given framework."""
        pass


class GridLayoutManager(LayoutManager):
    """Grid layout manager implementation."""
    
    def __init__(self):
        super().__init__("grid")
    
    def generate_layout_code(self, container_var: str, widgets: List[Dict[str, Any]], 
                           widget_vars: Dict[str, str]) -> str:
        """Generate grid layout code."""
        # Base implementation - override in framework-specific generators
        return f"# Grid layout for {container_var} not implemented"
    
    def supports_framework(self, framework: str) -> bool:
        """Most frameworks support grid layout."""
        return True


class FlowLayoutManager(LayoutManager):
    """Flow/box layout manager implementation."""
    
    def __init__(self):
        super().__init__("flow")
    
    def generate_layout_code(self, container_var: str, widgets: List[Dict[str, Any]], 
                           widget_vars: Dict[str, str]) -> str:
        """Generate flow layout code."""
        # Base implementation - override in framework-specific generators
        return f"# Flow layout for {container_var} not implemented"
    
    def supports_framework(self, framework: str) -> bool:
        """Most frameworks support some form of flow layout."""
        return True


class AbsoluteLayoutManager(LayoutManager):
    """Absolute positioning layout manager."""
    
    def __init__(self):
        super().__init__("absolute")
    
    def generate_layout_code(self, container_var: str, widgets: List[Dict[str, Any]], 
                           widget_vars: Dict[str, str]) -> str:
        """Generate absolute positioning code."""
        # Base implementation - override in framework-specific generators
        return f"# Absolute layout for {container_var} not implemented"
    
    def supports_framework(self, framework: str) -> bool:
        """Most frameworks support absolute positioning."""
        return True


# Layout manager registry
_LAYOUT_MANAGERS: Dict[str, LayoutManager] = {
    "grid": GridLayoutManager(),
    "flow": FlowLayoutManager(),
    "absolute": AbsoluteLayoutManager()
}


def get_layout_manager(layout_type: str) -> Optional[LayoutManager]:
    """Get layout manager for a specific type."""
    return _LAYOUT_MANAGERS.get(layout_type)


def register_layout_manager(layout_type: str, manager: LayoutManager):
    """Register a layout manager."""
    _LAYOUT_MANAGERS[layout_type] = manager