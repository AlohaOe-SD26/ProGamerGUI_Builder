"""
Container Widgets - Specialized container widgets for layout management
"""

from typing import Dict, Any, List
from .base_widget import ContainerWidget


class MainWindowWidget(ContainerWidget):
    """Main window container widget."""
    
    def __init__(self):
        super().__init__("MainWindow")
        self.supported_frameworks = ["PyQt6", "PyQt5", "Tkinter", "CustomTkinter"]
    
    def get_default_properties(self) -> Dict[str, Any]:
        return {
            "title": "My Application",
            "geometry": [100, 100, 800, 600],
            "resizable": True,
            "center_on_screen": True,
            "icon": "",  # Path to icon file
            "colors": {
                "background": "#F0F0F0",
                "title_bar": "#E0E0E0"
            },
            "menu_bar": {
                "enabled": False,
                "menus": []
            },
            "status_bar": {
                "enabled": False,
                "text": "Ready"
            },
            "toolbar": {
                "enabled": False,
                "tools": []
            }
        }
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "title": {
                "type": "string",
                "label": "Window Title",
                "description": "Text shown in the window title bar",
                "required": True
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry",
                "description": "Window position and size [x, y, width, height]"
            },
            "resizable": {
                "type": "bool",
                "label": "Resizable",
                "description": "Allow window to be resized",
                "default": True
            },
            "center_on_screen": {
                "type": "bool",
                "label": "Center on Screen",
                "description": "Center window on screen when opened",
                "default": True
            },
            "icon": {
                "type": "file",
                "label": "Window Icon",
                "description": "Icon file for the window",
                "filter": "Image Files (*.png *.jpg *.jpeg *.ico)"
            },
            "colors": {
                "type": "group",
                "label": "Colors",
                "children": {
                    "background": {
                        "type": "color",
                        "label": "Background",
                        "default": "#F0F0F0"
                    },
                    "title_bar": {
                        "type": "color",
                        "label": "Title Bar",
                        "default": "#E0E0E0"
                    }
                }
            },
            "menu_bar": {
                "type": "group",
                "label": "Menu Bar",
                "children": {
                    "enabled": {
                        "type": "bool",
                        "label": "Enable Menu Bar",
                        "default": False
                    },
                    "menus": {
                        "type": "menu_list",
                        "label": "Menus",
                        "description": "Menu bar menus",
                        "default": []
                    }
                }
            },
            "status_bar": {
                "type": "group",
                "label": "Status Bar",
                "children": {
                    "enabled": {
                        "type": "bool",
                        "label": "Enable Status Bar",
                        "default": False
                    },
                    "text": {
                        "type": "string",
                        "label": "Status Text",
                        "default": "Ready"
                    }
                }
            },
            "toolbar": {
                "type": "group",
                "label": "Toolbar",
                "children": {
                    "enabled": {
                        "type": "bool",
                        "label": "Enable Toolbar",
                        "default": False
                    },
                    "tools": {
                        "type": "tool_list",
                        "label": "Tools",
                        "description": "Toolbar tools",
                        "default": []
                    }
                }
            }
        }
    
    def get_category(self) -> str:
        return "Main"


class ScrollAreaWidget(ContainerWidget):
    """Scrollable area container widget."""
    
    def __init__(self):
        super().__init__("ScrollArea")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = {
            "name": "scroll_area_1",
            "geometry": [100, 100, 300, 200],
            "enabled": True,
            "visible": True,
            "layer": 2,
            "colors": {
                "background": "#FFFFFF",
                "border": "#CCCCCC"
            },
            "scroll_policy": {
                "horizontal": "auto",  # auto, always, never
                "vertical": "auto"
            },
            "widget_resizable": True,  # Content widget resizes with scroll area
            "content_size": [280, 180],  # Size of scrollable content
            "scroll_position": [0, 0]  # Initial scroll position
        }
        props.update(self.get_layout_properties())
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        base_defs = {
            "name": {
                "type": "string",
                "label": "Name",
                "required": True
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry"
            },
            "enabled": {
                "type": "bool",
                "label": "Enabled",
                "default": True
            },
            "visible": {
                "type": "bool",
                "label": "Visible",
                "default": True
            },
            "layer": {
                "type": "int",
                "label": "Layer",
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
                    "border": {
                        "type": "color",
                        "label": "Border",
                        "default": "#CCCCCC"
                    }
                }
            },
            "scroll_policy": {
                "type": "group",
                "label": "Scroll Policy",
                "children": {
                    "horizontal": {
                        "type": "choice",
                        "label": "Horizontal",
                        "options": ["auto", "always", "never"],
                        "default": "auto"
                    },
                    "vertical": {
                        "type": "choice",
                        "label": "Vertical",
                        "options": ["auto", "always", "never"],
                        "default": "auto"
                    }
                }
            },
            "widget_resizable": {
                "type": "bool",
                "label": "Widget Resizable",
                "description": "Content widget resizes with scroll area",
                "default": True
            },
            "content_size": {
                "type": "size",
                "label": "Content Size",
                "description": "Size of scrollable content [width, height]",
                "default": [280, 180]
            },
            "scroll_position": {
                "type": "position",
                "label": "Scroll Position",
                "description": "Initial scroll position [x, y]",
                "default": [0, 0]
            }
        }
        base_defs.update(self.get_layout_property_definitions())
        return base_defs
    
    def get_category(self) -> str:
        return "Container"


class GroupBoxWidget(ContainerWidget):
    """Group box container widget with title."""
    
    def __init__(self):
        super().__init__("GroupBox")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = {
            "name": "group_box_1",
            "title": "Group Box",
            "geometry": [100, 100, 200, 150],
            "enabled": True,
            "visible": True,
            "layer": 2,
            "colors": {
                "background": "#F0F0F0",
                "border": "#CCCCCC",
                "title": "#000000"
            },
            "font": {
                "family": "Arial",
                "size": 9,
                "bold": True,
                "italic": False
            },
            "checkable": False,  # Can be checked/unchecked to enable/disable contents
            "checked": True,
            "flat": False  # Flat appearance without 3D border
        }
        props.update(self.get_layout_properties())
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        base_defs = {
            "name": {
                "type": "string",
                "label": "Name",
                "required": True
            },
            "title": {
                "type": "string",
                "label": "Title",
                "description": "Title text shown on the group box border",
                "default": "Group Box"
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry"
            },
            "enabled": {
                "type": "bool",
                "label": "Enabled",
                "default": True
            },
            "visible": {
                "type": "bool",
                "label": "Visible",
                "default": True
            },
            "layer": {
                "type": "int",
                "label": "Layer",
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
                        "default": "#F0F0F0"
                    },
                    "border": {
                        "type": "color",
                        "label": "Border",
                        "default": "#CCCCCC"
                    },
                    "title": {
                        "type": "color",
                        "label": "Title Text",
                        "default": "#000000"
                    }
                }
            },
            "font": {
                "type": "group",
                "label": "Title Font",
                "children": {
                    "family": {
                        "type": "choice",
                        "label": "Family",
                        "options": ["Arial", "Helvetica", "Times New Roman", "Courier New"],
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
                        "default": True
                    },
                    "italic": {
                        "type": "bool",
                        "label": "Italic",
                        "default": False
                    }
                }
            },
            "checkable": {
                "type": "bool",
                "label": "Checkable",
                "description": "Add checkbox to enable/disable contents",
                "default": False
            },
            "checked": {
                "type": "bool",
                "label": "Checked",
                "description": "Initial checked state",
                "default": True
            },
            "flat": {
                "type": "bool",
                "label": "Flat",
                "description": "Flat appearance without 3D border",
                "default": False
            }
        }
        base_defs.update(self.get_layout_property_definitions())
        return base_defs
    
    def get_category(self) -> str:
        return "Container"


class SplitterWidget(ContainerWidget):
    """Splitter container widget for resizable panes."""
    
    def __init__(self):
        super().__init__("Splitter")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = {
            "name": "splitter_1",
            "geometry": [100, 100, 400, 300],
            "enabled": True,
            "visible": True,
            "layer": 2,
            "orientation": "horizontal",  # horizontal, vertical
            "colors": {
                "background": "#F0F0F0",
                "handle": "#CCCCCC"
            },
            "handle_width": 5,  # Width of the splitter handle
            "collapsible": True,  # Allow panes to be collapsed
            "sizes": [200, 200],  # Initial sizes of panes
            "stretch_factors": [1, 1]  # Stretch factors for panes
        }
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "name": {
                "type": "string",
                "label": "Name",
                "required": True
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry"
            },
            "enabled": {
                "type": "bool",
                "label": "Enabled",
                "default": True
            },
            "visible": {
                "type": "bool",
                "label": "Visible",
                "default": True
            },
            "layer": {
                "type": "int",
                "label": "Layer",
                "min": 1,
                "max": 10,
                "default": 2
            },
            "orientation": {
                "type": "choice",
                "label": "Orientation",
                "options": ["horizontal", "vertical"],
                "default": "horizontal"
            },
            "colors": {
                "type": "group",
                "label": "Colors",
                "children": {
                    "background": {
                        "type": "color",
                        "label": "Background",
                        "default": "#F0F0F0"
                    },
                    "handle": {
                        "type": "color",
                        "label": "Handle",
                        "default": "#CCCCCC"
                    }
                }
            },
            "handle_width": {
                "type": "int",
                "label": "Handle Width",
                "description": "Width of the splitter handle",
                "min": 1,
                "max": 20,
                "default": 5
            },
            "collapsible": {
                "type": "bool",
                "label": "Collapsible",
                "description": "Allow panes to be collapsed",
                "default": True
            },
            "sizes": {
                "type": "int_list",
                "label": "Pane Sizes",
                "description": "Initial sizes of panes",
                "default": [200, 200]
            },
            "stretch_factors": {
                "type": "int_list",
                "label": "Stretch Factors",
                "description": "Stretch factors for panes when resizing",
                "default": [1, 1]
            }
        }
    
    def get_category(self) -> str:
        return "Container"


class StackedWidget(ContainerWidget):
    """Stacked widget container for multiple pages."""
    
    def __init__(self):
        super().__init__("StackedWidget")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = {
            "name": "stacked_widget_1",
            "geometry": [100, 100, 300, 200],
            "enabled": True,
            "visible": True,
            "layer": 2,
            "colors": {
                "background": "#F0F0F0",
                "border": "#CCCCCC"
            },
            "current_index": 0,  # Index of currently visible page
            "pages": [
                {"name": "page_1", "title": "Page 1"},
                {"name": "page_2", "title": "Page 2"}
            ],
            "transition": {
                "enabled": False,
                "type": "slide",  # slide, fade, none
                "duration": 300  # milliseconds
            }
        }
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "name": {
                "type": "string",
                "label": "Name",
                "required": True
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry"
            },
            "enabled": {
                "type": "bool",
                "label": "Enabled",
                "default": True
            },
            "visible": {
                "type": "bool",
                "label": "Visible",
                "default": True
            },
            "layer": {
                "type": "int",
                "label": "Layer",
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
                        "default": "#F0F0F0"
                    },
                    "border": {
                        "type": "color",
                        "label": "Border",
                        "default": "#CCCCCC"
                    }
                }
            },
            "current_index": {
                "type": "int",
                "label": "Current Page",
                "description": "Index of initially visible page",
                "min": 0,
                "default": 0
            },
            "pages": {
                "type": "page_list",
                "label": "Pages",
                "description": "List of pages in the stack",
                "default": [
                    {"name": "page_1", "title": "Page 1"},
                    {"name": "page_2", "title": "Page 2"}
                ]
            },
            "transition": {
                "type": "group",
                "label": "Transition",
                "children": {
                    "enabled": {
                        "type": "bool",
                        "label": "Enable Transitions",
                        "default": False
                    },
                    "type": {
                        "type": "choice",
                        "label": "Transition Type",
                        "options": ["slide", "fade", "none"],
                        "default": "slide"
                    },
                    "duration": {
                        "type": "int",
                        "label": "Duration (ms)",
                        "description": "Transition duration in milliseconds",
                        "min": 100,
                        "max": 2000,
                        "default": 300
                    }
                }
            }
        }
    
    def get_category(self) -> str:
        return "Container"


# Container widget registry
CONTAINER_WIDGETS = {
    "MainWindow": MainWindowWidget(),
    "ScrollArea": ScrollAreaWidget(),
    "GroupBox": GroupBoxWidget(),
    "Splitter": SplitterWidget(),
    "StackedWidget": StackedWidget()
}


def get_available_container_widgets(framework: str = None) -> List[Dict[str, Any]]:
    """Get list of available container widgets for the specified framework."""
    widgets = []
    
    for widget_name, widget_class in CONTAINER_WIDGETS.items():
        if framework is None or widget_class.supports_framework(framework):
            widgets.append({
                "type": widget_name,
                "display_name": widget_class.get_display_name(),
                "description": widget_class.get_description(),
                "category": widget_class.get_category(),
                "supported_frameworks": widget_class.get_supported_frameworks()
            })
    
    return widgets


def get_container_widget_class(widget_type: str):
    """Get the container widget class for a specific widget type."""
    return CONTAINER_WIDGETS.get(widget_type)