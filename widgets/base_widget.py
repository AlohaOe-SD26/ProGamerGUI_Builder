"""
Base Widget - Abstract base class for all GUI widgets
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseWidget(ABC):
    """
    Abstract base class for all GUI widgets.
    Defines the common interface and properties that all widgets must implement.
    """
    
    def __init__(self, widget_type: str):
        self.widget_type = widget_type
        self.supported_frameworks: List[str] = []
        self.default_properties: Dict[str, Any] = {}
        self.property_definitions: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def get_default_properties(self) -> Dict[str, Any]:
        """Return the default properties for this widget type."""
        pass
    
    @abstractmethod
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Return property definitions for the property editor.
        
        Returns:
            Dict mapping property names to their definitions:
            {
                "property_name": {
                    "type": "string|int|bool|color|font|list",
                    "label": "Display Label",
                    "default": default_value,
                    "description": "Property description",
                    "options": [...] (for choice properties)
                }
            }
        """
        pass
    
    @abstractmethod
    def validate_properties(self, properties: Dict[str, Any]) -> bool:
        """Validate widget properties."""
        pass
    
    def get_supported_frameworks(self) -> List[str]:
        """Return list of supported frameworks for this widget."""
        return self.supported_frameworks
    
    def supports_framework(self, framework: str) -> bool:
        """Check if this widget supports the given framework."""
        return framework in self.supported_frameworks
    
    def get_display_name(self) -> str:
        """Get the display name for the widget palette."""
        return self.widget_type
    
    def get_description(self) -> str:
        """Get the widget description for tooltips."""
        return f"A {self.widget_type} widget"
    
    def get_category(self) -> str:
        """Get the widget category for grouping in palette."""
        return "Standard"
    
    def create_default_instance(self) -> Dict[str, Any]:
        """Create a default widget instance with all required properties."""
        return {
            "type": self.widget_type,
            "properties": self.get_default_properties()
        }
    
    def merge_properties(self, current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge property updates with current properties."""
        result = current.copy()
        
        for key, value in updates.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Deep merge for nested dictionaries
                result[key] = self.merge_properties(result[key], value)
            else:
                result[key] = value
        
        return result


class StandardWidget(BaseWidget):
    """
    Base class for standard widgets with common properties.
    """
    
    def __init__(self, widget_type: str):
        super().__init__(widget_type)
        self.supported_frameworks = ["PyQt6", "PyQt5", "Tkinter", "CustomTkinter"]
    
    def get_common_properties(self) -> Dict[str, Any]:
        """Get properties common to most standard widgets."""
        return {
            "name": f"{self.widget_type.lower()}_1",
            "text": self.widget_type,
            "geometry": [100, 100, 120, 40],
            "enabled": True,
            "visible": True,
            "layer": 2,
            "colors": {
                "background": "#FFFFFF",
                "foreground": "#000000",
                "border": "#CCCCCC"
            },
            "font": {
                "family": "Arial",
                "size": 9,
                "bold": False,
                "italic": False
            }
        }
    
    def get_common_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get property definitions common to most standard widgets."""
        return {
            "name": {
                "type": "string",
                "label": "Name",
                "description": "Variable name for the widget",
                "required": True
            },
            "text": {
                "type": "string",
                "label": "Text",
                "description": "Display text for the widget"
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry",
                "description": "Position and size [x, y, width, height]"
            },
            "enabled": {
                "type": "bool",
                "label": "Enabled",
                "description": "Whether the widget is enabled",
                "default": True
            },
            "visible": {
                "type": "bool",
                "label": "Visible",
                "description": "Whether the widget is visible",
                "default": True
            },
            "layer": {
                "type": "int",
                "label": "Layer",
                "description": "Display layer (1=background, higher=foreground)",
                "min": 1,
                "max": 10,
                "default": 2
            },
            "colors": {
                "type": "group",
                "label": "Colors",
                "children": {
                    "background": {
                        "type": "color",
                        "label": "Background",
                        "default": "#FFFFFF"
                    },
                    "foreground": {
                        "type": "color",
                        "label": "Foreground",
                        "default": "#000000"
                    },
                    "border": {
                        "type": "color",
                        "label": "Border",
                        "default": "#CCCCCC"
                    }
                }
            },
            "font": {
                "type": "group",
                "label": "Font",
                "children": {
                    "family": {
                        "type": "choice",
                        "label": "Family",
                        "options": ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana"],
                        "default": "Arial"
                    },
                    "size": {
                        "type": "int",
                        "label": "Size",
                        "min": 6,
                        "max": 72,
                        "default": 9
                    },
                    "bold": {
                        "type": "bool",
                        "label": "Bold",
                        "default": False
                    },
                    "italic": {
                        "type": "bool",
                        "label": "Italic",
                        "default": False
                    }
                }
            }
        }
    
    def validate_properties(self, properties: Dict[str, Any]) -> bool:
        """Validate standard widget properties."""
        try:
            # Check required properties
            if "name" not in properties or not properties["name"]:
                return False
            
            if "geometry" not in properties:
                return False
            
            geometry = properties["geometry"]
            if not isinstance(geometry, list) or len(geometry) != 4:
                return False
            
            # Check geometry values are positive
            if geometry[2] <= 0 or geometry[3] <= 0:  # width and height
                return False
            
            return True
            
        except Exception:
            return False


class ContainerWidget(BaseWidget):
    """
    Base class for container widgets that can hold other widgets.
    """
    
    def __init__(self, widget_type: str):
        super().__init__(widget_type)
        self.supported_frameworks = ["PyQt6", "PyQt5", "Tkinter", "CustomTkinter"]
        self.can_contain_widgets = True
    
    def get_layout_properties(self) -> Dict[str, Any]:
        """Get layout-specific properties for containers."""
        return {
            "layout": {
                "type": "grid",  # grid, flow, absolute
                "margins": [10, 10, 10, 10],  # top, right, bottom, left
                "spacing": 5
            }
        }
    
    def get_layout_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get layout property definitions for containers."""
        return {
            "layout": {
                "type": "group",
                "label": "Layout",
                "children": {
                    "type": {
                        "type": "choice",
                        "label": "Layout Type",
                        "options": ["grid", "flow", "absolute"],
                        "default": "grid"
                    },
                    "margins": {
                        "type": "margins",
                        "label": "Margins",
                        "description": "Layout margins [top, right, bottom, left]",
                        "default": [10, 10, 10, 10]
                    },
                    "spacing": {
                        "type": "int",
                        "label": "Spacing",
                        "description": "Space between child widgets",
                        "min": 0,
                        "max": 50,
                        "default": 5
                    }
                }
            }
        }


class InputWidget(StandardWidget):
    """
    Base class for input widgets (Entry, TextArea, etc.).
    """
    
    def __init__(self, widget_type: str):
        super().__init__(widget_type)
    
    def get_input_properties(self) -> Dict[str, Any]:
        """Get properties common to input widgets."""
        return {
            "placeholder": "",
            "readonly": False,
            "max_length": 0,  # 0 = unlimited
            "validation": {
                "type": "none",  # none, email, number, regex
                "pattern": "",
                "message": "Invalid input"
            }
        }
    
    def get_input_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get property definitions for input widgets."""
        return {
            "placeholder": {
                "type": "string",
                "label": "Placeholder",
                "description": "Placeholder text shown when empty"
            },
            "readonly": {
                "type": "bool",
                "label": "Read Only",
                "description": "Whether the input is read-only",
                "default": False
            },
            "max_length": {
                "type": "int",
                "label": "Max Length",
                "description": "Maximum number of characters (0 = unlimited)",
                "min": 0,
                "default": 0
            },
            "validation": {
                "type": "group",
                "label": "Validation",
                "children": {
                    "type": {
                        "type": "choice",
                        "label": "Validation Type",
                        "options": ["none", "email", "number", "regex"],
                        "default": "none"
                    },
                    "pattern": {
                        "type": "string",
                        "label": "Pattern",
                        "description": "Regex pattern for validation"
                    },
                    "message": {
                        "type": "string",
                        "label": "Error Message",
                        "default": "Invalid input"
                    }
                }
            }
        }


class SelectionWidget(StandardWidget):
    """
    Base class for selection widgets (Checkbox, RadioButton, etc.).
    """
    
    def __init__(self, widget_type: str):
        super().__init__(widget_type)
    
    def get_selection_properties(self) -> Dict[str, Any]:
        """Get properties common to selection widgets."""
        return {
            "checked": False,
            "group": "default"  # For radio buttons
        }
    
    def get_selection_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get property definitions for selection widgets."""
        return {
            "checked": {
                "type": "bool",
                "label": "Checked",
                "description": "Whether the widget is checked",
                "default": False
            },
            "group": {
                "type": "string",
                "label": "Group",
                "description": "Group name for radio buttons",
                "default": "default"
            }
        }


class ListWidget(StandardWidget):
    """
    Base class for list-based widgets (ComboBox, ListBox, etc.).
    """
    
    def __init__(self, widget_type: str):
        super().__init__(widget_type)
    
    def get_list_properties(self) -> Dict[str, Any]:
        """Get properties common to list widgets."""
        return {
            "items": ["Item 1", "Item 2", "Item 3"],
            "selected_index": 0,
            "multiple_selection": False
        }
    
    def get_list_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get property definitions for list widgets."""
        return {
            "items": {
                "type": "list",
                "label": "Items",
                "description": "List of items to display",
                "default": ["Item 1", "Item 2", "Item 3"]
            },
            "selected_index": {
                "type": "int",
                "label": "Selected Index",
                "description": "Index of initially selected item",
                "min": 0,
                "default": 0
            },
            "multiple_selection": {
                "type": "bool",
                "label": "Multiple Selection",
                "description": "Allow multiple items to be selected",
                "default": False
            }
        }