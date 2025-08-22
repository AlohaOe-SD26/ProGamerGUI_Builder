"""
Standard Widgets - Concrete implementations of common GUI widgets
"""

from typing import Dict, Any, List
from .base_widget import StandardWidget, ContainerWidget, InputWidget, SelectionWidget, ListWidget


class ButtonWidget(StandardWidget):
    """Button widget implementation."""
    
    def __init__(self):
        super().__init__("Button")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update({
            "text": "Button",
            "geometry": [100, 100, 100, 35],
            "action": {
                "type": "none",  # none, message, function, signal
                "target": "",
                "parameters": {}
            }
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update({
            "action": {
                "type": "group",
                "label": "Action",
                "children": {
                    "type": {
                        "type": "choice",
                        "label": "Action Type",
                        "options": ["none", "message", "function", "signal"],
                        "default": "none"
                    },
                    "target": {
                        "type": "string",
                        "label": "Target",
                        "description": "Function name or signal target"
                    },
                    "parameters": {
                        "type": "dict",
                        "label": "Parameters",
                        "description": "Action parameters"
                    }
                }
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class LabelWidget(StandardWidget):
    """Label widget implementation."""
    
    def __init__(self):
        super().__init__("Label")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update({
            "text": "Label",
            "geometry": [100, 100, 80, 25],
            "alignment": "left",  # left, center, right
            "word_wrap": False
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update({
            "alignment": {
                "type": "choice",
                "label": "Text Alignment",
                "options": ["left", "center", "right"],
                "default": "left"
            },
            "word_wrap": {
                "type": "bool",
                "label": "Word Wrap",
                "description": "Wrap text to multiple lines",
                "default": False
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Display"


class EntryWidget(InputWidget):
    """Single-line text entry widget."""
    
    def __init__(self):
        super().__init__("Entry")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update(self.get_input_properties())
        props.update({
            "text": "",
            "geometry": [100, 100, 200, 25],
            "password": False,
            "echo_mode": "normal"  # normal, password, no_echo
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update(self.get_input_property_definitions())
        defs.update({
            "password": {
                "type": "bool",
                "label": "Password Field",
                "description": "Hide input characters",
                "default": False
            },
            "echo_mode": {
                "type": "choice",
                "label": "Echo Mode",
                "options": ["normal", "password", "no_echo"],
                "default": "normal"
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class TextWidget(InputWidget):
    """Multi-line text widget."""
    
    def __init__(self):
        super().__init__("Text")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update(self.get_input_properties())
        props.update({
            "text": "Multi-line text",
            "geometry": [100, 100, 300, 150],
            "word_wrap": True,
            "scrollbars": "auto",  # auto, horizontal, vertical, both, none
            "tab_width": 4
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update(self.get_input_property_definitions())
        defs.update({
            "word_wrap": {
                "type": "bool",
                "label": "Word Wrap",
                "description": "Wrap text to widget width",
                "default": True
            },
            "scrollbars": {
                "type": "choice",
                "label": "Scrollbars",
                "options": ["auto", "horizontal", "vertical", "both", "none"],
                "default": "auto"
            },
            "tab_width": {
                "type": "int",
                "label": "Tab Width",
                "description": "Width of tab character in spaces",
                "min": 1,
                "max": 16,
                "default": 4
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class CheckboxWidget(SelectionWidget):
    """Checkbox widget implementation."""
    
    def __init__(self):
        super().__init__("Checkbox")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update(self.get_selection_properties())
        props.update({
            "text": "Checkbox",
            "geometry": [100, 100, 120, 25],
            "tristate": False  # Allow three states: checked, unchecked, partially checked
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update(self.get_selection_property_definitions())
        defs.update({
            "tristate": {
                "type": "bool",
                "label": "Tristate",
                "description": "Allow partially checked state",
                "default": False
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class RadioButtonWidget(SelectionWidget):
    """Radio button widget implementation."""
    
    def __init__(self):
        super().__init__("RadioButton")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update(self.get_selection_properties())
        props.update({
            "text": "Radio Button",
            "geometry": [100, 100, 120, 25],
            "exclusive": True  # Only one in group can be selected
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update(self.get_selection_property_definitions())
        defs.update({
            "exclusive": {
                "type": "bool",
                "label": "Exclusive",
                "description": "Only one radio button in group can be selected",
                "default": True
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class ComboBoxWidget(ListWidget):
    """Combo box (dropdown) widget implementation."""
    
    def __init__(self):
        super().__init__("ComboBox")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update(self.get_list_properties())
        props.update({
            "text": "ComboBox",
            "geometry": [100, 100, 150, 25],
            "editable": False,  # Allow user to type custom values
            "items_with_actions": []  # Advanced dropdown with actions per item
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update(self.get_list_property_definitions())
        defs.update({
            "editable": {
                "type": "bool",
                "label": "Editable",
                "description": "Allow typing custom values",
                "default": False
            },
            "items_with_actions": {
                "type": "advanced_list",
                "label": "Items with Actions",
                "description": "Items with associated actions",
                "default": []
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class ListBoxWidget(ListWidget):
    """List box widget implementation."""
    
    def __init__(self):
        super().__init__("ListBox")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update(self.get_list_properties())
        props.update({
            "text": "ListBox",
            "geometry": [100, 100, 200, 150],
            "multiple_selection": True,
            "sort_items": False
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update(self.get_list_property_definitions())
        defs.update({
            "sort_items": {
                "type": "bool",
                "label": "Sort Items",
                "description": "Automatically sort items alphabetically",
                "default": False
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class FrameWidget(ContainerWidget):
    """Frame container widget implementation."""
    
    def __init__(self):
        super().__init__("Frame")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = {
            "name": "frame_1",
            "geometry": [100, 100, 300, 200],
            "enabled": True,
            "visible": True,
            "layer": 1,  # Frames usually go in background
            "colors": {
                "background": "#F0F0F0",
                "border": "#CCCCCC"
            },
            "border": {
                "style": "solid",  # none, solid, dashed, dotted
                "width": 1,
                "radius": 0  # Border radius for rounded corners
            }
        }
        props.update(self.get_layout_properties())
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        return {
            "name": {
                "type": "string",
                "label": "Name",
                "description": "Variable name for the frame",
                "required": True
            },
            "geometry": {
                "type": "geometry",
                "label": "Geometry",
                "description": "Position and size [x, y, width, height]"
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
                "default": 1
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
            "border": {
                "type": "group",
                "label": "Border",
                "children": {
                    "style": {
                        "type": "choice",
                        "label": "Style",
                        "options": ["none", "solid", "dashed", "dotted"],
                        "default": "solid"
                    },
                    "width": {
                        "type": "int",
                        "label": "Width",
                        "min": 0,
                        "max": 10,
                        "default": 1
                    },
                    "radius": {
                        "type": "int",
                        "label": "Radius",
                        "description": "Border radius for rounded corners",
                        "min": 0,
                        "max": 50,
                        "default": 0
                    }
                }
            },
            **self.get_layout_property_definitions()
        }
    
    def get_category(self) -> str:
        return "Container"


class TabsWidget(ContainerWidget):
    """Tabbed widget implementation."""
    
    def __init__(self):
        super().__init__("Tabs")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = {
            "name": "tabs_1",
            "geometry": [100, 100, 400, 300],
            "enabled": True,
            "visible": True,
            "layer": 1,
            "colors": {
                "background": "#F0F0F0",
                "border": "#CCCCCC"
            },
            "tab_position": "top",  # top, bottom, left, right
            "tab_data": [
                {"title": "Tab 1", "color": "#FFFFFF"},
                {"title": "Tab 2", "color": "#FFFFFF"}
            ],
            "active_tab_index": 0,
            "closable_tabs": False,
            "movable_tabs": False
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
                "default": 1
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
            "tab_position": {
                "type": "choice",
                "label": "Tab Position",
                "options": ["top", "bottom", "left", "right"],
                "default": "top"
            },
            "tab_data": {
                "type": "tab_list",
                "label": "Tabs",
                "description": "List of tabs with titles and colors",
                "default": [
                    {"title": "Tab 1", "color": "#FFFFFF"},
                    {"title": "Tab 2", "color": "#FFFFFF"}
                ]
            },
            "active_tab_index": {
                "type": "int",
                "label": "Active Tab",
                "description": "Index of initially active tab",
                "min": 0,
                "default": 0
            },
            "closable_tabs": {
                "type": "bool",
                "label": "Closable Tabs",
                "description": "Allow tabs to be closed",
                "default": False
            },
            "movable_tabs": {
                "type": "bool",
                "label": "Movable Tabs",
                "description": "Allow tabs to be reordered",
                "default": False
            }
        }
    
    def get_category(self) -> str:
        return "Container"


class SliderWidget(StandardWidget):
    """Slider widget implementation."""
    
    def __init__(self):
        super().__init__("Slider")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update({
            "text": "",  # Sliders usually don't show text
            "geometry": [100, 100, 200, 25],
            "orientation": "horizontal",  # horizontal, vertical
            "minimum": 0,
            "maximum": 100,
            "value": 50,
            "step": 1,
            "tick_position": "below",  # none, above, below, both
            "tick_interval": 10
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update({
            "orientation": {
                "type": "choice",
                "label": "Orientation",
                "options": ["horizontal", "vertical"],
                "default": "horizontal"
            },
            "minimum": {
                "type": "int",
                "label": "Minimum",
                "default": 0
            },
            "maximum": {
                "type": "int",
                "label": "Maximum",
                "default": 100
            },
            "value": {
                "type": "int",
                "label": "Value",
                "default": 50
            },
            "step": {
                "type": "int",
                "label": "Step",
                "description": "Step size for value changes",
                "min": 1,
                "default": 1
            },
            "tick_position": {
                "type": "choice",
                "label": "Tick Position",
                "options": ["none", "above", "below", "both"],
                "default": "below"
            },
            "tick_interval": {
                "type": "int",
                "label": "Tick Interval",
                "description": "Interval between tick marks",
                "min": 1,
                "default": 10
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


class ProgressBarWidget(StandardWidget):
    """Progress bar widget implementation."""
    
    def __init__(self):
        super().__init__("ProgressBar")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update({
            "text": "",
            "geometry": [100, 100, 200, 25],
            "orientation": "horizontal",  # horizontal, vertical
            "minimum": 0,
            "maximum": 100,
            "value": 0,
            "show_text": True,
            "text_format": "%p%",  # %p = percentage, %v = value, %m = maximum
            "inverted": False  # Progress from right to left or bottom to top
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update({
            "orientation": {
                "type": "choice",
                "label": "Orientation",
                "options": ["horizontal", "vertical"],
                "default": "horizontal"
            },
            "minimum": {
                "type": "int",
                "label": "Minimum",
                "default": 0
            },
            "maximum": {
                "type": "int",
                "label": "Maximum",
                "default": 100
            },
            "value": {
                "type": "int",
                "label": "Value",
                "default": 0
            },
            "show_text": {
                "type": "bool",
                "label": "Show Text",
                "description": "Display progress text",
                "default": True
            },
            "text_format": {
                "type": "string",
                "label": "Text Format",
                "description": "%p=percentage, %v=value, %m=maximum",
                "default": "%p%"
            },
            "inverted": {
                "type": "bool",
                "label": "Inverted",
                "description": "Progress from opposite direction",
                "default": False
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Display"


class SpinBoxWidget(InputWidget):
    """Spin box widget implementation."""
    
    def __init__(self):
        super().__init__("SpinBox")
    
    def get_default_properties(self) -> Dict[str, Any]:
        props = self.get_common_properties()
        props.update({
            "text": "",
            "geometry": [100, 100, 100, 25],
            "minimum": 0,
            "maximum": 99,
            "value": 0,
            "step": 1,
            "prefix": "",
            "suffix": "",
            "wrapping": False  # Wrap around at min/max
        })
        return props
    
    def get_property_definitions(self) -> Dict[str, Dict[str, Any]]:
        defs = self.get_common_property_definitions()
        defs.update({
            "minimum": {
                "type": "int",
                "label": "Minimum",
                "default": 0
            },
            "maximum": {
                "type": "int",
                "label": "Maximum",
                "default": 99
            },
            "value": {
                "type": "int",
                "label": "Value",
                "default": 0
            },
            "step": {
                "type": "int",
                "label": "Step",
                "description": "Step size for value changes",
                "min": 1,
                "default": 1
            },
            "prefix": {
                "type": "string",
                "label": "Prefix",
                "description": "Text shown before the value"
            },
            "suffix": {
                "type": "string",
                "label": "Suffix",
                "description": "Text shown after the value"
            },
            "wrapping": {
                "type": "bool",
                "label": "Wrapping",
                "description": "Wrap around at minimum/maximum",
                "default": False
            }
        })
        return defs
    
    def get_category(self) -> str:
        return "Input"


# Widget registry
STANDARD_WIDGETS = {
    "Button": ButtonWidget(),
    "Label": LabelWidget(),
    "Entry": EntryWidget(),
    "Text": TextWidget(),
    "Checkbox": CheckboxWidget(),
    "RadioButton": RadioButtonWidget(),
    "ComboBox": ComboBoxWidget(),
    "ListBox": ListBoxWidget(),
    "Frame": FrameWidget(),
    "Tabs": TabsWidget(),
    "Slider": SliderWidget(),
    "ProgressBar": ProgressBarWidget(),
    "SpinBox": SpinBoxWidget()
}


def get_available_widgets(framework: str = None) -> List[Dict[str, Any]]:
    """Get list of available widgets for the specified framework."""
    widgets = []
    
    for widget_name, widget_class in STANDARD_WIDGETS.items():
        if framework is None or widget_class.supports_framework(framework):
            widgets.append({
                "type": widget_name,
                "display_name": widget_class.get_display_name(),
                "description": widget_class.get_description(),
                "category": widget_class.get_category(),
                "supported_frameworks": widget_class.get_supported_frameworks(),
                "default_text": widget_class.get_default_properties().get("text", widget_name)
            })
    
    # Sort by category, then by name
    widgets.sort(key=lambda x: (x["category"], x["display_name"]))
    return widgets


def get_widget_class(widget_type: str):
    """Get the widget class for a specific widget type."""
    return STANDARD_WIDGETS.get(widget_type)


def create_widget_instance(widget_type: str) -> Dict[str, Any]:
    """Create a default instance of the specified widget type."""
    widget_class = get_widget_class(widget_type)
    if widget_class:
        return widget_class.create_default_instance()
    else:
        # Return a basic widget instance
        return {
            "type": widget_type,
            "properties": {
                "name": f"{widget_type.lower()}_1",
                "geometry": [100, 100, 100, 50],
                "enabled": True,
                "visible": True
            }
        }