"""
Canvas - Visual design surface for the GUI Builder
"""

import logging
from typing import Dict, Optional, Tuple, List, Any
from PyQt6.QtWidgets import QFrame, QMenu
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

class Canvas(QFrame):
    """
    The main design canvas where widgets are visually arranged.
    Handles widget rendering, selection, dragging, resizing, and grid snapping.
    """
    
    # Signals
    widget_selected = pyqtSignal(str)  # widget_id
    widget_modified = pyqtSignal()
    
    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Canvas settings
        self.grid_visible = True
        self.snap_enabled = True
        self.grid_size = 20
        self.zoom_level = 1.0
        
        # Interaction state
        self.selected_widget_id: Optional[str] = None
        self.dragging = False
        self.resizing = False
        self.resize_handle: Optional[str] = None
        self.drag_start_pos: Optional[QPoint] = None
        self.last_mouse_pos: Optional[QPoint] = None
        
        # Visual settings
        self.selection_color = QColor(30, 144, 255)  # Dodger blue
        self.grid_color = QColor(220, 220, 220)
        self.handle_size = 8
        
        self.setup_canvas()
        self.connect_signals()
        
        self.logger.info("Canvas initialized")
    
    def setup_canvas(self):
        """Setup canvas properties."""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumSize(600, 400)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Load canvas settings from state manager
        settings = self.state_manager.get_canvas_settings()
        self.grid_size = settings.get("grid_size", 20)
        self.grid_visible = settings.get("grid_visible", True)
        self.snap_enabled = settings.get("snap_enabled", True)
        self.zoom_level = settings.get("zoom_level", 1.0)
    
    def connect_signals(self):
        """Connect to state manager signals."""
        self.state_manager.state_changed.connect(self.update)
        self.state_manager.selection_changed.connect(self.on_selection_changed)
        self.state_manager.widget_added.connect(self.on_widget_added)
        self.state_manager.widget_removed.connect(self.on_widget_removed)
    
    def set_grid_visible(self, visible: bool):
        """Set grid visibility."""
        self.grid_visible = visible
        self.state_manager.update_canvas_settings({"grid_visible": visible})
        self.update()
    
    def set_snap_enabled(self, enabled: bool):
        """Set snap to grid enabled."""
        self.snap_enabled = enabled
        self.state_manager.update_canvas_settings({"snap_enabled": enabled})
    
    def set_grid_size(self, size: int):
        """Set grid size."""
        self.grid_size = size
        self.state_manager.update_canvas_settings({"grid_size": size})
        self.update()
    
    def snap_to_grid(self, value: int) -> int:
        """Snap a coordinate value to the grid."""
        if self.snap_enabled and self.grid_size > 0:
            return round(value / self.grid_size) * self.grid_size
        return value
    
    def snap_point_to_grid(self, point: QPoint) -> QPoint:
        """Snap a point to the grid."""
        return QPoint(self.snap_to_grid(point.x()), self.snap_to_grid(point.y()))
    
    def add_widget(self, widget_info: Dict[str, Any]):
        """Add a new widget to the canvas."""
        # Calculate position based on canvas size and existing widgets
        canvas_rect = self.rect()
        main_window = self.state_manager.get_main_window_data()
        main_window_geom = main_window.get("properties", {}).get("geometry", [100, 100, 800, 600])
        
        # Position new widget inside main window area
        base_x = main_window_geom[0] + 20
        base_y = main_window_geom[1] + 60  # Account for title bar
        
        # Snap to grid
        new_x = self.snap_to_grid(base_x)
        new_y = self.snap_to_grid(base_y)
        
        # Default size based on widget type
        default_sizes = {
            "Button": (120, 40),
            "Label": (100, 30),
            "Entry": (200, 30),
            "Text": (300, 100),
            "Frame": (200, 150),
            "Checkbox": (120, 30),
            "RadioButton": (120, 30),
            "ComboBox": (150, 30),
            "ListBox": (200, 150),
            "Scrollbar": (20, 100),
        }
        
        widget_type = widget_info.get("type", "Widget")
        default_width, default_height = default_sizes.get(widget_type, (100, 50))
        
        # Create widget data
        widget_data = {
            "type": widget_type,
            "framework": self.state_manager.get_target_framework(),
            "properties": {
                "geometry": [new_x, new_y, default_width, default_height],
                "text": widget_info.get("default_text", widget_type),
                "name": f"{widget_type.lower()}_{self.state_manager.widget_counter + 1}",
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
                },
                "enabled": True,
                "visible": True,
                "layer": 2  # Default content layer
            }
        }
        
        # Add type-specific properties
        if widget_type == "Entry":
            widget_data["properties"]["placeholder"] = "Enter text..."
        elif widget_type == "Checkbox":
            widget_data["properties"]["checked"] = False
        elif widget_type == "RadioButton":
            widget_data["properties"]["checked"] = False
            widget_data["properties"]["group"] = "default"
        elif widget_type in ["ComboBox", "ListBox"]:
            widget_data["properties"]["items"] = ["Item 1", "Item 2", "Item 3"]
        
        # Add to state manager
        widget_id = self.state_manager.add_widget(widget_data)
        self.logger.info(f"Added widget {widget_id} of type {widget_type}")
    
    def paintEvent(self, event):
        """Paint the canvas."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw grid if enabled
        if self.grid_visible:
            self.draw_grid(painter)
        
        # Draw main window representation
        self.draw_main_window(painter)
        
        # Draw all widgets
        self.draw_widgets(painter)
        
        # Draw selection handles if a widget is selected
        if self.selected_widget_id:
            self.draw_selection_handles(painter)
    
    def draw_grid(self, painter: QPainter):
        """Draw the grid."""
        painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))
        
        rect = self.rect()
        
        # Vertical lines
        for x in range(0, rect.width(), self.grid_size):
            painter.drawLine(x, 0, x, rect.height())
        
        # Horizontal lines
        for y in range(0, rect.height(), self.grid_size):
            painter.drawLine(0, y, rect.width(), y)
    
    def draw_main_window(self, painter: QPainter):
        """Draw the main window representation."""
        main_window = self.state_manager.get_main_window_data()
        properties = main_window.get("properties", {})
        geometry = properties.get("geometry", [100, 100, 800, 600])
        title = properties.get("title", "My Application")
        colors = properties.get("colors", {})
        
        # Main window rectangle
        window_rect = QRect(geometry[0], geometry[1], geometry[2], geometry[3])
        
        # Title bar
        title_bar_height = 30
        title_bar_rect = QRect(window_rect.x(), window_rect.y(), window_rect.width(), title_bar_height)
        content_rect = QRect(window_rect.x(), window_rect.y() + title_bar_height, 
                           window_rect.width(), window_rect.height() - title_bar_height)
        
        # Draw title bar
        title_color = QColor(colors.get("title_bar", "#E0E0E0"))
        painter.setBrush(QBrush(title_color))
        painter.setPen(QPen(QColor("#999999"), 1))
        painter.drawRect(title_bar_rect)
        
        # Draw title text
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Arial", 10))
        painter.drawText(title_bar_rect.adjusted(10, 0, 0, 0), 
                        Qt.AlignmentFlag.AlignVCenter, title)
        
        # Draw content area
        bg_color = QColor(colors.get("background", "#F0F0F0"))
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#999999"), 1))
        painter.drawRect(content_rect)
        
        # Draw border highlight if main window is selected
        if self.selected_widget_id == "main_window":
            painter.setPen(QPen(self.selection_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(window_rect)
    
    def draw_widgets(self, painter: QPainter):
        """Draw all widgets on the canvas."""
        widgets = self.state_manager.get_all_widgets()
        
        # Sort widgets by layer for proper drawing order
        sorted_widgets = sorted(widgets.items(), 
                              key=lambda x: x[1].get("properties", {}).get("layer", 2))
        
        for widget_id, widget_data in sorted_widgets:
            self.draw_widget(painter, widget_id, widget_data)
    
    def draw_widget(self, painter: QPainter, widget_id: str, widget_data: Dict[str, Any]):
        """Draw a single widget."""
        properties = widget_data.get("properties", {})
        geometry = properties.get("geometry", [0, 0, 100, 50])
        widget_type = widget_data.get("type", "Widget")
        text = properties.get("text", "")
        colors = properties.get("colors", {})
        font_info = properties.get("font", {})
        enabled = properties.get("enabled", True)
        
        # Widget rectangle
        widget_rect = QRect(geometry[0], geometry[1], geometry[2], geometry[3])
        
        # Set up colors
        bg_color = QColor(colors.get("background", "#FFFFFF"))
        fg_color = QColor(colors.get("foreground", "#000000"))
        border_color = QColor(colors.get("border", "#CCCCCC"))
        
        if not enabled:
            bg_color = bg_color.darker(120)
            fg_color = fg_color.lighter(150)
        
        # Set up font
        font = QFont(font_info.get("family", "Arial"), font_info.get("size", 9))
        font.setBold(font_info.get("bold", False))
        font.setItalic(font_info.get("italic", False))
        painter.setFont(font)
        
        # Draw widget based on type
        if widget_type == "Button":
            self.draw_button(painter, widget_rect, text, bg_color, fg_color, border_color)
        elif widget_type == "Label":
            self.draw_label(painter, widget_rect, text, bg_color, fg_color, border_color)
        elif widget_type == "Entry":
            self.draw_entry(painter, widget_rect, text, bg_color, fg_color, border_color, properties)
        elif widget_type == "Text":
            self.draw_text(painter, widget_rect, text, bg_color, fg_color, border_color)
        elif widget_type == "Frame":
            self.draw_frame(painter, widget_rect, bg_color, border_color)
        elif widget_type == "Checkbox":
            self.draw_checkbox(painter, widget_rect, text, fg_color, properties.get("checked", False))
        elif widget_type == "RadioButton":
            self.draw_radiobutton(painter, widget_rect, text, fg_color, properties.get("checked", False))
        elif widget_type == "ComboBox":
            self.draw_combobox(painter, widget_rect, text, bg_color, fg_color, border_color)
        elif widget_type == "ListBox":
            self.draw_listbox(painter, widget_rect, bg_color, fg_color, border_color, properties.get("items", []))
        else:
            # Default widget rendering
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 1))
            painter.drawRect(widget_rect)
            painter.setPen(fg_color)
            painter.drawText(widget_rect, Qt.AlignmentFlag.AlignCenter, widget_type)
    
    def draw_button(self, painter: QPainter, rect: QRect, text: str, bg_color: QColor, fg_color: QColor, border_color: QColor):
        """Draw a button widget."""
        # Button background with slight gradient effect
        painter.setBrush(QBrush(bg_color.lighter(110)))
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(rect)
        
        # Button text
        painter.setPen(fg_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def draw_label(self, painter: QPainter, rect: QRect, text: str, bg_color: QColor, fg_color: QColor, border_color: QColor):
        """Draw a label widget."""
        # Label background (usually transparent)
        if bg_color != QColor("#FFFFFF"):  # Only draw background if not white
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 1, Qt.PenStyle.DashLine))
            painter.drawRect(rect)
        
        # Label text
        painter.setPen(fg_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
    
    def draw_entry(self, painter: QPainter, rect: QRect, text: str, bg_color: QColor, fg_color: QColor, border_color: QColor, properties: Dict):
        """Draw an entry widget."""
        # Entry background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(rect)
        
        # Entry text or placeholder
        display_text = text if text else properties.get("placeholder", "")
        text_color = fg_color if text else fg_color.lighter(150)
        painter.setPen(text_color)
        text_rect = rect.adjusted(5, 0, -5, 0)  # Add padding
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, display_text)
    
    def draw_text(self, painter: QPainter, rect: QRect, text: str, bg_color: QColor, fg_color: QColor, border_color: QColor):
        """Draw a text widget (multiline)."""
        # Text background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(rect)
        
        # Text content
        painter.setPen(fg_color)
        text_rect = rect.adjusted(5, 5, -15, -5)  # Add padding and space for scrollbar
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, text)
        
        # Draw scrollbar representation
        scrollbar_rect = QRect(rect.right() - 15, rect.top(), 15, rect.height())
        painter.setBrush(QBrush(QColor("#E0E0E0")))
        painter.setPen(QPen(QColor("#CCCCCC"), 1))
        painter.drawRect(scrollbar_rect)
    
    def draw_frame(self, painter: QPainter, rect: QRect, bg_color: QColor, border_color: QColor):
        """Draw a frame widget."""
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 2))
        painter.drawRect(rect)
        
        # Draw frame label
        painter.setPen(QColor("#666666"))
        painter.drawText(rect.adjusted(5, 5, 0, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, "Frame")
    
    def draw_checkbox(self, painter: QPainter, rect: QRect, text: str, fg_color: QColor, checked: bool):
        """Draw a checkbox widget."""
        # Checkbox box
        box_size = 16
        box_rect = QRect(rect.x() + 5, rect.center().y() - box_size // 2, box_size, box_size)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.drawRect(box_rect)
        
        # Checkmark if checked
        if checked:
            painter.setPen(QPen(QColor("#007ACC"), 2))
            # Draw checkmark
            painter.drawLine(box_rect.x() + 3, box_rect.center().y(),
                           box_rect.center().x(), box_rect.bottom() - 3)
            painter.drawLine(box_rect.center().x(), box_rect.bottom() - 3,
                           box_rect.right() - 2, box_rect.top() + 3)
        
        # Checkbox text
        painter.setPen(fg_color)
        text_rect = rect.adjusted(box_size + 10, 0, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
    
    def draw_radiobutton(self, painter: QPainter, rect: QRect, text: str, fg_color: QColor, checked: bool):
        """Draw a radio button widget."""
        # Radio button circle
        circle_size = 16
        circle_rect = QRect(rect.x() + 5, rect.center().y() - circle_size // 2, circle_size, circle_size)
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#666666"), 1))
        painter.drawEllipse(circle_rect)
        
        # Filled circle if checked
        if checked:
            inner_rect = circle_rect.adjusted(4, 4, -4, -4)
            painter.setBrush(QBrush(QColor("#007ACC")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(inner_rect)
        
        # Radio button text
        painter.setPen(fg_color)
        text_rect = rect.adjusted(circle_size + 10, 0, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
    
    def draw_combobox(self, painter: QPainter, rect: QRect, text: str, bg_color: QColor, fg_color: QColor, border_color: QColor):
        """Draw a combobox widget."""
        # Combobox background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(rect)
        
        # Combobox text
        painter.setPen(fg_color)
        text_rect = rect.adjusted(5, 0, -20, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, text)
        
        # Dropdown arrow
        arrow_rect = QRect(rect.right() - 20, rect.top(), 20, rect.height())
        painter.setPen(QPen(QColor("#666666"), 2))
        arrow_center = arrow_rect.center()
        painter.drawLine(arrow_center.x() - 5, arrow_center.y() - 2,
                        arrow_center.x(), arrow_center.y() + 3)
        painter.drawLine(arrow_center.x(), arrow_center.y() + 3,
                        arrow_center.x() + 5, arrow_center.y() - 2)
    
    def draw_listbox(self, painter: QPainter, rect: QRect, bg_color: QColor, fg_color: QColor, border_color: QColor, items: List[str]):
        """Draw a listbox widget."""
        # Listbox background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1))
        painter.drawRect(rect)
        
        # List items
        painter.setPen(fg_color)
        item_height = 20
        for i, item in enumerate(items[:rect.height() // item_height]):
            item_rect = QRect(rect.x() + 5, rect.y() + 5 + i * item_height, 
                            rect.width() - 25, item_height)
            painter.drawText(item_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, item)
        
        # Scrollbar representation
        if len(items) * item_height > rect.height():
            scrollbar_rect = QRect(rect.right() - 15, rect.top(), 15, rect.height())
            painter.setBrush(QBrush(QColor("#E0E0E0")))
            painter.setPen(QPen(QColor("#CCCCCC"), 1))
            painter.drawRect(scrollbar_rect)
    
    def draw_selection_handles(self, painter: QPainter):
        """Draw selection handles around the selected widget."""
        widget_data = self.state_manager.get_widget(self.selected_widget_id)
        if not widget_data:
            # Check if main window is selected
            if self.selected_widget_id == "main_window":
                main_window = self.state_manager.get_main_window_data()
                geometry = main_window.get("properties", {}).get("geometry", [100, 100, 800, 600])
            else:
                return
        else:
            geometry = widget_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
        
        widget_rect = QRect(geometry[0], geometry[1], geometry[2], geometry[3])
        
        # Draw selection border
        painter.setPen(QPen(self.selection_color, 2, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(widget_rect)
        
        # Draw resize handles
        handles = self.get_resize_handles(widget_rect)
        painter.setBrush(QBrush(self.selection_color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        
        for handle_rect in handles.values():
            painter.drawRect(handle_rect)
    
    def get_resize_handles(self, rect: QRect) -> Dict[str, QRect]:
        """Get resize handle rectangles for a widget."""
        hs = self.handle_size
        hsh = hs // 2
        
        return {
            "top_left": QRect(rect.topLeft() - QPoint(hsh, hsh), QPoint(rect.topLeft()) + QPoint(hsh, hsh)),
            "top_right": QRect(rect.topRight() - QPoint(hsh, hsh), QPoint(rect.topRight()) + QPoint(hsh, hsh)),
            "bottom_left": QRect(rect.bottomLeft() - QPoint(hsh, hsh), QPoint(rect.bottomLeft()) + QPoint(hsh, hsh)),
            "bottom_right": QRect(rect.bottomRight() - QPoint(hsh, hsh), QPoint(rect.bottomRight()) + QPoint(hsh, hsh)),
            "top": QRect(rect.center().x() - hsh, rect.top() - hsh, hs, hs),
            "bottom": QRect(rect.center().x() - hsh, rect.bottom() - hsh, hs, hs),
            "left": QRect(rect.left() - hsh, rect.center().y() - hsh, hs, hs),
            "right": QRect(rect.right() - hsh, rect.center().y() - hsh, hs, hs)
        }
    
    def get_widget_at_position(self, pos: QPoint) -> Optional[str]:
        """Get the widget ID at the given position."""
        # Check main window first
        main_window = self.state_manager.get_main_window_data()
        main_geometry = main_window.get("properties", {}).get("geometry", [100, 100, 800, 600])
        main_rect = QRect(main_geometry[0], main_geometry[1], main_geometry[2], main_geometry[3])
        
        if main_rect.contains(pos):
            # Check widgets (in reverse layer order for top-to-bottom hit testing)
            widgets = self.state_manager.get_all_widgets()
            sorted_widgets = sorted(widgets.items(), 
                                  key=lambda x: x[1].get("properties", {}).get("layer", 2), 
                                  reverse=True)
            
            for widget_id, widget_data in sorted_widgets:
                geometry = widget_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
                widget_rect = QRect(geometry[0], geometry[1], geometry[2], geometry[3])
                if widget_rect.contains(pos):
                    return widget_id
            
            return "main_window"
        
        return None
    
    def get_resize_handle_at_position(self, pos: QPoint) -> Optional[str]:
        """Get the resize handle at the given position."""
        if not self.selected_widget_id:
            return None
        
        widget_data = self.state_manager.get_widget(self.selected_widget_id)
        if widget_data:
            geometry = widget_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
        elif self.selected_widget_id == "main_window":
            main_window = self.state_manager.get_main_window_data()
            geometry = main_window.get("properties", {}).get("geometry", [100, 100, 800, 600])
        else:
            return None
        
        widget_rect = QRect(geometry[0], geometry[1], geometry[2], geometry[3])
        handles = self.get_resize_handles(widget_rect)
        
        for handle_name, handle_rect in handles.items():
            if handle_rect.contains(pos):
                return handle_name
        
        return None
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        pos = event.pos()
        self.drag_start_pos = pos
        self.last_mouse_pos = pos
        
        # Check for resize handle first
        if self.selected_widget_id:
            handle = self.get_resize_handle_at_position(pos)
            if handle:
                self.resizing = True
                self.resize_handle = handle
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                return
        
        # Check for widget selection
        widget_id = self.get_widget_at_position(pos)
        if widget_id != self.selected_widget_id:
            self.selected_widget_id = widget_id
            self.state_manager.set_selected_widget(widget_id)
            self.widget_selected.emit(widget_id or "")
            self.update()
        
        # Start dragging if a widget is selected
        if self.selected_widget_id:
            self.dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        pos = event.pos()
        
        if self.resizing and self.resize_handle and self.selected_widget_id:
            self.handle_resize(pos)
        elif self.dragging and self.selected_widget_id:
            self.handle_drag(pos)
        else:
            # Update cursor based on what's under the mouse
            handle = self.get_resize_handle_at_position(pos)
            if handle:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif self.get_widget_at_position(pos):
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        
        self.last_mouse_pos = pos
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if self.dragging or self.resizing:
            self.widget_modified.emit()
        
        self.dragging = False
        self.resizing = False
        self.resize_handle = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def handle_drag(self, pos: QPoint):
        """Handle widget dragging."""
        if not self.drag_start_pos:
            return
        
        delta = pos - self.drag_start_pos
        
        if self.selected_widget_id == "main_window":
            # Move main window
            main_window = self.state_manager.get_main_window_data()
            geometry = main_window.get("properties", {}).get("geometry", [100, 100, 800, 600])
            new_x = self.snap_to_grid(geometry[0] + delta.x())
            new_y = self.snap_to_grid(geometry[1] + delta.y())
            
            self.state_manager.update_main_window({
                "properties": {"geometry": [new_x, new_y, geometry[2], geometry[3]]}
            })
        else:
            # Move widget
            widget_data = self.state_manager.get_widget(self.selected_widget_id)
            if widget_data:
                geometry = widget_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
                new_x = self.snap_to_grid(geometry[0] + delta.x())
                new_y = self.snap_to_grid(geometry[1] + delta.y())
                
                self.state_manager.update_widget(self.selected_widget_id, {
                    "properties": {"geometry": [new_x, new_y, geometry[2], geometry[3]]}
                })
        
        self.drag_start_pos = pos
        self.update()
    
    def handle_resize(self, pos: QPoint):
        """Handle widget resizing."""
        if not self.resize_handle or not self.selected_widget_id:
            return
        
        if self.selected_widget_id == "main_window":
            main_window = self.state_manager.get_main_window_data()
            geometry = main_window.get("properties", {}).get("geometry", [100, 100, 800, 600])
        else:
            widget_data = self.state_manager.get_widget(self.selected_widget_id)
            if not widget_data:
                return
            geometry = widget_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
        
        x, y, w, h = geometry
        
        # Calculate new geometry based on resize handle
        if "left" in self.resize_handle:
            new_x = self.snap_to_grid(pos.x())
            new_w = max(50, w + (x - new_x))
            x = new_x
            w = new_w
        elif "right" in self.resize_handle:
            w = max(50, self.snap_to_grid(pos.x() - x))
        
        if "top" in self.resize_handle:
            new_y = self.snap_to_grid(pos.y())
            new_h = max(30, h + (y - new_y))
            y = new_y
            h = new_h
        elif "bottom" in self.resize_handle:
            h = max(30, self.snap_to_grid(pos.y() - y))
        
        new_geometry = [x, y, w, h]
        
        if self.selected_widget_id == "main_window":
            self.state_manager.update_main_window({
                "properties": {"geometry": new_geometry}
            })
        else:
            self.state_manager.update_widget(self.selected_widget_id, {
                "properties": {"geometry": new_geometry}
            })
        
        self.update()
    
    def show_context_menu(self, pos: QPoint):
        """Show context menu."""
        widget_id = self.get_widget_at_position(pos)
        
        menu = QMenu(self)
        
        if widget_id and widget_id != "main_window":
            delete_action = menu.addAction("Delete Widget")
            delete_action.triggered.connect(lambda: self.delete_widget(widget_id))
            
            duplicate_action = menu.addAction("Duplicate Widget")
            duplicate_action.triggered.connect(lambda: self.duplicate_widget(widget_id))
            
            menu.addSeparator()
        
        # Layer actions
        if widget_id and widget_id != "main_window":
            layer_menu = menu.addMenu("Layer")
            
            bring_forward = layer_menu.addAction("Bring Forward")
            bring_forward.triggered.connect(lambda: self.change_widget_layer(widget_id, 1))
            
            send_backward = layer_menu.addAction("Send Backward")
            send_backward.triggered.connect(lambda: self.change_widget_layer(widget_id, -1))
        
        if menu.actions():
            menu.exec(self.mapToGlobal(pos))
    
    def delete_widget(self, widget_id: str):
        """Delete a widget."""
        self.state_manager.remove_widget(widget_id)
        self.update()
    
    def duplicate_widget(self, widget_id: str):
        """Duplicate a widget."""
        widget_data = self.state_manager.get_widget(widget_id)
        if widget_data:
            # Create a copy with offset position
            new_data = copy.deepcopy(widget_data)
            geometry = new_data.get("properties", {}).get("geometry", [0, 0, 100, 50])
            geometry[0] += 20
            geometry[1] += 20
            new_data["properties"]["geometry"] = geometry
            
            # Add the duplicate
            self.state_manager.add_widget(new_data)
            self.update()
    
    def change_widget_layer(self, widget_id: str, direction: int):
        """Change widget layer."""
        widget_data = self.state_manager.get_widget(widget_id)
        if widget_data:
            current_layer = widget_data.get("properties", {}).get("layer", 2)
            layer_config = self.state_manager.get_layer_config()
            max_layers = layer_config.get("total_layers", 5)
            
            new_layer = max(1, min(max_layers, current_layer + direction))
            if new_layer != current_layer:
                self.state_manager.update_widget(widget_id, {
                    "properties": {"layer": new_layer}
                })
                self.update()
    
    def on_selection_changed(self, widget_id: Optional[str]):
        """Handle selection change from state manager."""
        self.selected_widget_id = widget_id
        self.update()
    
    def on_widget_added(self, widget_id: str):
        """Handle widget added."""
        self.update()
    
    def on_widget_removed(self, widget_id: str):
        """Handle widget removed."""
        if self.selected_widget_id == widget_id:
            self.selected_widget_id = None
        self.update()