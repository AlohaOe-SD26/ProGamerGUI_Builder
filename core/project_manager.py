"""
Project Manager - Handles project loading, saving, and code export
"""

import json
import logging
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject

from generators.base_generator import get_generator


class ProjectManager(QObject):
    """
    Manages project file operations including save, load, and code export.
    """
    
    def __init__(self, state_manager):
        super().__init__()
        self.state_manager = state_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Project settings
        self.project_file_extension = ".pgb"  # ProGamerGUI Builder
        self.project_filter = f"ProGamerGUI Projects (*{self.project_file_extension})"
        
        # Export settings
        self.output_dir = Path(__file__).parent.parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger.info("ProjectManager initialized")
    
    def new_project(self) -> bool:
        """Create a new project."""
        try:
            self.state_manager.new_project()
            self.logger.info("New project created")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create new project: {e}")
            self.show_error("Failed to create new project", str(e))
            return False
    
    def open_project(self, filepath: Optional[str] = None) -> bool:
        """Open an existing project file."""
        try:
            if not filepath:
                filepath, _ = QFileDialog.getOpenFileName(
                    None,
                    "Open Project",
                    str(self.output_dir),
                    self.project_filter
                )
                
                if not filepath:
                    return False
            
            # Load project data
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Validate project data
            if not self.validate_project_data(project_data):
                self.show_error("Invalid Project", "The selected file is not a valid project file.")
                return False
            
            # Load into state manager
            self.state_manager.load_project_data(project_data)
            self.state_manager.set_project_path(filepath)
            self.state_manager.mark_as_saved()
            
            self.logger.info(f"Project opened: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open project: {e}")
            self.show_error("Failed to open project", str(e))
            return False
    
    def save_project(self) -> bool:
        """Save the current project."""
        project_path = self.state_manager.get_project_path()
        
        if project_path:
            return self.save_project_to_file(project_path)
        else:
            return self.save_project_as()
    
    def save_project_as(self) -> bool:
        """Save the current project with a new filename."""
        try:
            project_data = self.state_manager.get_project_data()
            project_name = project_data.get("name", "New Project")
            
            default_filename = f"{project_name.replace(' ', '_')}{self.project_file_extension}"
            
            filepath, _ = QFileDialog.getSaveFileName(
                None,
                "Save Project As",
                str(self.output_dir / default_filename),
                self.project_filter
            )
            
            if not filepath:
                return False
            
            # Ensure correct extension
            if not filepath.endswith(self.project_file_extension):
                filepath += self.project_file_extension
            
            return self.save_project_to_file(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save project as: {e}")
            self.show_error("Failed to save project", str(e))
            return False
    
    def save_project_to_file(self, filepath: str) -> bool:
        """Save project data to a specific file."""
        try:
            # Get project data
            project_data = self.state_manager.get_project_data()
            
            # Add metadata
            project_data["metadata"] = {
                "version": "1.0",
                "created": project_data.get("metadata", {}).get("created", datetime.now().isoformat()),
                "modified": datetime.now().isoformat(),
                "generator": "ProGamerGUI Builder"
            }
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # Update state manager
            self.state_manager.set_project_path(filepath)
            self.state_manager.mark_as_saved()
            
            self.logger.info(f"Project saved: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save project to file: {e}")
            self.show_error("Failed to save project", str(e))
            return False
    
    def export_code(self) -> bool:
        """Export the current design to executable code."""
        try:
            project_data = self.state_manager.get_project_data()
            framework = self.state_manager.get_target_framework()
            
            # Get the appropriate generator
            generator = get_generator(framework)
            if not generator:
                self.show_error("Export Failed", f"No generator available for framework: {framework}")
                return False
            
            # Get export directory
            project_name = project_data.get("name", "exported_project").replace(" ", "_")
            
            export_dir, _ = QFileDialog.getSaveFileName(
                None,
                "Export Code As",
                str(self.output_dir / f"{project_name}.zip"),
                "Zip Files (*.zip)"
            )
            
            if not export_dir:
                return False
            
            # Generate code
            generated_files = generator.generate_project(project_data)
            
            # Create export package
            success = self.create_export_package(export_dir, generated_files, project_data)
            
            if success:
                self.logger.info(f"Code exported to: {export_dir}")
                self.show_info("Export Successful", f"Code exported successfully to:\n{export_dir}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to export code: {e}")
            self.show_error("Export Failed", str(e))
            return False
    
    def create_export_package(self, export_path: str, generated_files: Dict[str, str], project_data: Dict[str, Any]) -> bool:
        """Create a complete export package with all necessary files."""
        try:
            # Ensure export path ends with .zip
            if not export_path.endswith('.zip'):
                export_path += '.zip'
            
            project_name = project_data.get("name", "exported_project").replace(" ", "_")
            
            # Create temporary directory for the project
            temp_dir = self.output_dir / f"temp_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # Write generated files
                for filename, content in generated_files.items():
                    file_path = temp_dir / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # Create requirements.txt
                requirements = self.generate_requirements(project_data)
                with open(temp_dir / "requirements.txt", 'w', encoding='utf-8') as f:
                    f.write(requirements)
                
                # Create README.md
                readme = self.generate_readme(project_data)
                with open(temp_dir / "README.md", 'w', encoding='utf-8') as f:
                    f.write(readme)
                
                # Create run scripts
                self.create_run_scripts(temp_dir, project_name)
                
                # Copy assets if any
                self.copy_project_assets(temp_dir, project_data)
                
                # Create zip file
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in temp_dir.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_dir)
                            zipf.write(file_path, arcname)
                
                return True
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            self.logger.error(f"Failed to create export package: {e}")
            self.show_error("Export Package Failed", str(e))
            return False
    
    def generate_requirements(self, project_data: Dict[str, Any]) -> str:
        """Generate requirements.txt content."""
        framework = project_data.get("framework", "PyQt6")
        
        requirements = [
            f"# Requirements for {project_data.get('name', 'GUI Application')}",
            f"# Generated by ProGamerGUI Builder",
            f"# Framework: {framework}",
            "",
        ]
        
        # Framework-specific requirements
        if framework == "PyQt6":
            requirements.extend([
                "PyQt6>=6.5.0",
                "PyQt6-Qt6>=6.5.0"
            ])
        elif framework == "PyQt5":
            requirements.extend([
                "PyQt5>=5.15.0"
            ])
        elif framework == "Tkinter":
            requirements.extend([
                "# Tkinter is included with Python",
                "# No additional requirements needed"
            ])
        elif framework == "CustomTkinter":
            requirements.extend([
                "customtkinter>=5.2.0",
                "Pillow>=8.3.0"
            ])
        
        # Add any plugin requirements
        widgets = project_data.get("widgets", [])
        plugin_requirements = set()
        
        for widget in widgets:
            widget_type = widget.get("type", "")
            if widget_type == "MapView":
                plugin_requirements.add("tkintermapview>=1.29")
            elif widget_type == "TimePicker":
                plugin_requirements.add("tktimepicker>=2.0.1")
            elif widget_type == "VideoPlayer":
                plugin_requirements.add("tkvideoplayer>=2.3")
        
        if plugin_requirements:
            requirements.extend(["", "# Plugin requirements"])
            requirements.extend(sorted(plugin_requirements))
        
        return "\n".join(requirements)
    
    def generate_readme(self, project_data: Dict[str, Any]) -> str:
        """Generate README.md content."""
        project_name = project_data.get("name", "GUI Application")
        framework = project_data.get("framework", "PyQt6")
        
        readme_content = f"""# {project_name}

This GUI application was created using ProGamerGUI Builder.

## Framework
- **UI Framework**: {framework}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Requirements
- Python 3.7 or higher
- See `requirements.txt` for package dependencies

## Installation & Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   - **Windows**: Double-click `run.bat`
   - **Linux/Mac**: Run `./run.sh` or `python main.py`

## Project Structure
```
{project_name.replace(' ', '_')}/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── run.bat             # Windows run script
├── run.sh              # Linux/Mac run script
└── assets/             # Application assets (if any)
```

## Features
- Cross-platform GUI application
- Built with {framework}
- Professional layout and design
- Responsive interface

## Development
This application was generated from a visual design using ProGamerGUI Builder.
The generated code is clean, readable, and ready for customization.

## License
This generated code is provided as-is. Modify and distribute according to your needs.

---
*Generated by ProGamerGUI Builder - A professional GUI design tool for Python*
"""
        return readme_content
    
    def create_run_scripts(self, project_dir: Path, project_name: str):
        """Create platform-specific run scripts."""
        # Windows batch script
        bat_content = f"""@echo off
title {project_name}
echo Starting {project_name}...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Install requirements if needed
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo WARNING: Failed to install some requirements
    )
)

REM Run the application
echo Starting application...
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo Check the error messages above
    pause
) else (
    echo.
    echo Application closed successfully
)
"""
        
        with open(project_dir / "run.bat", 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        # Unix shell script
        sh_content = f"""#!/bin/bash
echo "Starting {project_name}..."
echo

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Determine Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# Install requirements if needed
if [ -f "requirements.txt" ]; then
    echo "Installing requirements..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "WARNING: Failed to install some requirements"
    fi
fi

# Run the application
echo "Starting application..."
$PYTHON_CMD main.py

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Application failed to start"
    echo "Check the error messages above"
else
    echo
    echo "Application closed successfully"
fi
"""
        
        with open(project_dir / "run.sh", 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Make shell script executable (on Unix systems)
        try:
            import stat
            sh_path = project_dir / "run.sh"
            sh_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        except:
            pass  # Ignore chmod errors on Windows
    
    def copy_project_assets(self, project_dir: Path, project_data: Dict[str, Any]):
        """Copy project assets to the export directory."""
        # Create assets directory
        assets_dir = project_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # TODO: Copy actual asset files when asset management is implemented
        # For now, create a placeholder
        placeholder_content = """# Assets Directory

This directory contains assets used by the application.
Place images, icons, and other resources here.

## Usage in Code
```python
import os
assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
image_path = os.path.join(assets_dir, 'my_image.png')
```
"""
        with open(assets_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
    
    def validate_project_data(self, project_data: Dict[str, Any]) -> bool:
        """Validate project data structure."""
        try:
            # Check required fields
            required_fields = ["name", "framework"]
            for field in required_fields:
                if field not in project_data:
                    self.logger.warning(f"Missing required field: {field}")
                    return False
            
            # Check main window
            if "main_window" not in project_data:
                self.logger.warning("Missing main_window definition")
                return False
            
            # Check widgets structure
            if "widgets" in project_data:
                if not isinstance(project_data["widgets"], list):
                    self.logger.warning("Widgets must be a list")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Project validation failed: {e}")
            return False
    
    def show_error(self, title: str, message: str):
        """Show error dialog."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()
    
    def show_info(self, title: str, message: str):
        """Show info dialog."""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()