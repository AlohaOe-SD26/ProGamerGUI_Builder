#!/usr/bin/env python3
"""
ProGamerGUI Builder - Main Entry Point
A framework-agnostic GUI builder for Python applications.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.app import GuiBuilderApp
from core.state_manager import setup_logging

def main():
    """Main entry point for the GUI Builder application."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger("main")
        
        logger.info("Starting ProGamerGUI Builder...")
        
        # Import Qt modules (this will handle virtual environment setup if needed)
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
        except ImportError as e:
            logger.error(f"Failed to import PyQt6: {e}")
            print("Error: PyQt6 not found. Please run setup first.")
            return 1
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("ProGamerGUI Builder")
        app.setOrganizationName("ProGamer Studios")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        
        # Create and show main window
        main_window = GuiBuilderApp()
        main_window.show()
        
        logger.info("Application started successfully")
        
        # Run event loop
        return app.exec()
        
    except Exception as e:
        logging.error(f"Critical error in main: {e}", exc_info=True)
        print(f"Critical error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())