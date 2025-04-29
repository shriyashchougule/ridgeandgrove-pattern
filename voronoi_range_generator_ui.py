#!/usr/bin/env python3
import sys
import os
import json
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QFormLayout, QLabel, QPushButton,
                           QSpinBox, QDoubleSpinBox, QCheckBox, QFileDialog,
                           QGroupBox, QTabWidget, QSlider, QLineEdit)
from PyQt5.QtCore import Qt
import subprocess
from PyQt5.QtGui import QFont

class RangeSpinBox(QWidget):
    """Custom widget that provides min/max range selection for numeric values"""
    def __init__(self, min_value, max_value, decimals=0, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        if decimals > 0:
            self.min_spin = QDoubleSpinBox()
            self.max_spin = QDoubleSpinBox()
            self.min_spin.setDecimals(decimals)
            self.max_spin.setDecimals(decimals)
            self.min_spin.setSingleStep(0.1)
            self.max_spin.setSingleStep(0.1)
        else:
            self.min_spin = QSpinBox()
            self.max_spin = QSpinBox()
        
        self.min_spin.setMinimum(min_value)
        self.min_spin.setMaximum(max_value)
        self.max_spin.setMinimum(min_value)
        self.max_spin.setMaximum(max_value)
        
        self.min_spin.setValue(min_value)
        self.max_spin.setValue(max_value)
        
        self.min_label = QLabel("Min:")
        self.max_label = QLabel("Max:")
        
        self.layout.addWidget(self.min_label)
        self.layout.addWidget(self.min_spin)
        self.layout.addWidget(self.max_label)
        self.layout.addWidget(self.max_spin)
        
        # Connect value changed signals
        self.min_spin.valueChanged.connect(self._on_min_changed)
        self.max_spin.valueChanged.connect(self._on_max_changed)
    
    def _on_min_changed(self, value):
        if value > self.max_spin.value():
            self.max_spin.setValue(value)
    
    def _on_max_changed(self, value):
        if value < self.min_spin.value():
            self.min_spin.setValue(value)
    
    def get_range(self):
        return (self.min_spin.value(), self.max_spin.value())

class VoronoiRangeGeneratorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voronoi Range Generator")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.basic_tab = QWidget()
        self.advanced_tab = QWidget()
        self.generation_tab = QWidget()
        
        self.tab_widget.addTab(self.basic_tab, "Basic Settings")
        self.tab_widget.addTab(self.advanced_tab, "Advanced Effects")
        self.tab_widget.addTab(self.generation_tab, "Generation")
        
        # Setup UI for each tab
        self._setup_basic_tab()
        self._setup_advanced_tab()
        self._setup_generation_tab()
        
        # Add generate button at the bottom
        self.generate_button = QPushButton("Generate Patterns")
        self.generate_button.setMinimumHeight(40)
        bold_font = QFont()
        bold_font.setBold(True)
        self.generate_button.setFont(bold_font)
        self.main_layout.addWidget(self.generate_button)
        
        # Connect signals
        self.generate_button.clicked.connect(self.generate_patterns)
    
    def _setup_basic_tab(self):
        layout = QVBoxLayout(self.basic_tab)
        
        # Image size group
        size_group = QGroupBox("Image Size")
        size_layout = QFormLayout()
        self.width_range = RangeSpinBox(100, 3000)
        self.height_range = RangeSpinBox(100, 3000)
        size_layout.addRow("Width:", self.width_range)
        size_layout.addRow("Height:", self.height_range)
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Points group
        points_group = QGroupBox("Voronoi Points")
        points_layout = QFormLayout()
        self.min_points_range = RangeSpinBox(3, 500)
        self.max_points_range = RangeSpinBox(10, 1000)
        self.edge_thickness_range = RangeSpinBox(1, 5)
        self.show_points_check = QCheckBox("Show Points")
        
        points_layout.addRow("Min Points:", self.min_points_range)
        points_layout.addRow("Max Points:", self.max_points_range)
        points_layout.addRow("Edge Thickness:", self.edge_thickness_range)
        points_layout.addRow("Show Points:", self.show_points_check)
        points_group.setLayout(points_layout)
        layout.addWidget(points_group)
        
        # 3D Effect Basic Group
        effect_group = QGroupBox("3D Effect Basic")
        effect_layout = QFormLayout()
        self.bulge_strength_range = RangeSpinBox(0.1, 1.0, 2)
        self.roundness_range = RangeSpinBox(0.5, 5.0, 2)
        self.smoothness_range = RangeSpinBox(5, 31, 2)  # Must be odd numbers for OpenCV
        self.smoothness_range.min_spin.setSingleStep(2)
        self.smoothness_range.max_spin.setSingleStep(2)
        self.shadow_depth_range = RangeSpinBox(0.1, 1.0, 2)
        
        effect_layout.addRow("Bulge Strength:", self.bulge_strength_range)
        effect_layout.addRow("Roundness:", self.roundness_range)
        effect_layout.addRow("Smoothness:", self.smoothness_range)
        effect_layout.addRow("Shadow Depth:", self.shadow_depth_range)
        effect_group.setLayout(effect_layout)
        layout.addWidget(effect_group)
    
    def _setup_advanced_tab(self):
        layout = QVBoxLayout(self.advanced_tab)
        
        # Lighting group
        lighting_group = QGroupBox("Lighting")
        lighting_layout = QFormLayout()
        self.light_intensity_range = RangeSpinBox(0.1, 2.0, 2)
        self.ambient_light_range = RangeSpinBox(0.0, 1.0, 2)
        lighting_layout.addRow("Light Intensity:", self.light_intensity_range)
        lighting_layout.addRow("Ambient Light:", self.ambient_light_range)
        lighting_group.setLayout(lighting_layout)
        layout.addWidget(lighting_group)
        
        # Surface group
        surface_group = QGroupBox("Uneven Surface")
        surface_layout = QFormLayout()
        self.surface_enabled_check = QCheckBox("Enable Uneven Surface")
        self.surface_enabled_check.setChecked(True)
        self.surface_scale_range = RangeSpinBox(0.0, 1.0, 2)
        self.surface_complexity_range = RangeSpinBox(1.0, 5.0, 2)
        
        surface_layout.addRow("Enable:", self.surface_enabled_check)
        surface_layout.addRow("Scale:", self.surface_scale_range)
        surface_layout.addRow("Complexity:", self.surface_complexity_range)
        surface_group.setLayout(surface_layout)
        layout.addWidget(surface_group)
        
        # Wet surface group
        wet_group = QGroupBox("Wet Surface")
        wet_layout = QFormLayout()
        self.wetness_range = RangeSpinBox(0.0, 1.0, 2)
        self.specular_intensity_range = RangeSpinBox(0.0, 2.0, 2)
        self.specular_power_range = RangeSpinBox(1.0, 100.0, 2)
        
        wet_layout.addRow("Wetness:", self.wetness_range)
        wet_layout.addRow("Specular Intensity:", self.specular_intensity_range)
        wet_layout.addRow("Specular Power:", self.specular_power_range)
        wet_group.setLayout(wet_layout)
        layout.addWidget(wet_group)
        
        # Light direction group
        light_dir_group = QGroupBox("Light Direction")
        light_dir_layout = QFormLayout()
        self.light_x_range = RangeSpinBox(-1.0, 1.0, 2)
        self.light_y_range = RangeSpinBox(-1.0, 1.0, 2)
        self.light_z_range = RangeSpinBox(0.1, 2.0, 2)
        
        light_dir_layout.addRow("X Range:", self.light_x_range)
        light_dir_layout.addRow("Y Range:", self.light_y_range)
        light_dir_layout.addRow("Z Range:", self.light_z_range)
        light_dir_group.setLayout(light_dir_layout)
        layout.addWidget(light_dir_group)
    
    def _setup_generation_tab(self):
        layout = QVBoxLayout(self.generation_tab)
        
        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout()
        
        self.num_images_spin = QSpinBox()
        self.num_images_spin.setMinimum(1)
        self.num_images_spin.setMaximum(10000)
        self.num_images_spin.setValue(10)
        
        self.output_dir_edit = QLineEdit("voronoi_output")
        self.browse_button = QPushButton("Browse...")
        browse_layout = QHBoxLayout()
        browse_layout.addWidget(self.output_dir_edit)
        browse_layout.addWidget(self.browse_button)
        
        output_layout.addRow("Number of Images:", self.num_images_spin)
        output_layout.addRow("Output Directory:", browse_layout)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Preview section
        preview_group = QGroupBox("Preview and Progress")
        preview_layout = QVBoxLayout()
        self.status_label = QLabel("Ready to generate patterns")
        self.config_path_label = QLabel("Config will be saved to: voronoi_range_config.json")
        self.excel_info_label = QLabel("Parameter data will be saved to: parameters.xlsx in output directory")
        
        preview_layout.addWidget(self.status_label)
        preview_layout.addWidget(self.config_path_label)
        preview_layout.addWidget(self.excel_info_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Save/Load Config
        config_group = QGroupBox("Configuration")
        config_layout = QHBoxLayout()
        self.save_config_button = QPushButton("Save Config")
        self.load_config_button = QPushButton("Load Config")
        config_layout.addWidget(self.save_config_button)
        config_layout.addWidget(self.load_config_button)
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Connect signals
        self.browse_button.clicked.connect(self._browse_output_dir)
        self.save_config_button.clicked.connect(self._save_config)
        self.load_config_button.clicked.connect(self._load_config)
    
    def _browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_edit.setText(directory)
    
    def _save_config(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Configuration", 
                                              "voronoi_range_config.json", 
                                              "JSON Files (*.json)")
        if file_name:
            config = self._create_range_config()
            with open(file_name, 'w') as f:
                json.dump(config, f, indent=2)
            self.status_label.setText(f"Configuration saved to {file_name}")
    
    def _load_config(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Configuration", 
                                              "", 
                                              "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    config = json.load(f)
                self._apply_range_config(config)
                self.status_label.setText(f"Configuration loaded from {file_name}")
            except Exception as e:
                self.status_label.setText(f"Error loading configuration: {str(e)}")
    
    def _create_range_config(self):
        """Create a configuration dictionary with all parameter ranges"""
        return {
            # Basic settings
            "width_range": self.width_range.get_range(),
            "height_range": self.height_range.get_range(),
            "min_points_range": self.min_points_range.get_range(),
            "max_points_range": self.max_points_range.get_range(),
            "edge_thickness_range": self.edge_thickness_range.get_range(),
            "show_points": self.show_points_check.isChecked(),
            
            # 3D Effect Basic
            "bulge_strength_range": self.bulge_strength_range.get_range(),
            "roundness_range": self.roundness_range.get_range(),
            "smoothness_range": self.smoothness_range.get_range(),
            "shadow_depth_range": self.shadow_depth_range.get_range(),
            
            # Lighting
            "light_intensity_range": self.light_intensity_range.get_range(),
            "ambient_light_range": self.ambient_light_range.get_range(),
            
            # Uneven Surface
            "surface_enabled": self.surface_enabled_check.isChecked(),
            "surface_scale_range": self.surface_scale_range.get_range(),
            "surface_complexity_range": self.surface_complexity_range.get_range(),
            
            # Wet Surface
            "wetness_range": self.wetness_range.get_range(),
            "specular_intensity_range": self.specular_intensity_range.get_range(),
            "specular_power_range": self.specular_power_range.get_range(),
            
            # Light Direction
            "light_x_range": self.light_x_range.get_range(),
            "light_y_range": self.light_y_range.get_range(),
            "light_z_range": self.light_z_range.get_range(),
            
            # Generation settings
            "num_images": self.num_images_spin.value(),
            "output_dir": self.output_dir_edit.text()
        }
    
    def _apply_range_config(self, config):
        """Apply a loaded configuration to the UI widgets"""
        # Basic settings
        if "width_range" in config:
            self.width_range.min_spin.setValue(config["width_range"][0])
            self.width_range.max_spin.setValue(config["width_range"][1])
        
        if "height_range" in config:
            self.height_range.min_spin.setValue(config["height_range"][0])
            self.height_range.max_spin.setValue(config["height_range"][1])
        
        if "min_points_range" in config:
            self.min_points_range.min_spin.setValue(config["min_points_range"][0])
            self.min_points_range.max_spin.setValue(config["min_points_range"][1])
            
        if "max_points_range" in config:
            self.max_points_range.min_spin.setValue(config["max_points_range"][0])
            self.max_points_range.max_spin.setValue(config["max_points_range"][1])
        
        if "edge_thickness_range" in config:
            self.edge_thickness_range.min_spin.setValue(config["edge_thickness_range"][0])
            self.edge_thickness_range.max_spin.setValue(config["edge_thickness_range"][1])
        
        if "show_points" in config:
            self.show_points_check.setChecked(config["show_points"])
        
        # 3D Effect Basic
        if "bulge_strength_range" in config:
            self.bulge_strength_range.min_spin.setValue(config["bulge_strength_range"][0])
            self.bulge_strength_range.max_spin.setValue(config["bulge_strength_range"][1])
        
        if "roundness_range" in config:
            self.roundness_range.min_spin.setValue(config["roundness_range"][0])
            self.roundness_range.max_spin.setValue(config["roundness_range"][1])
        
        if "smoothness_range" in config:
            self.smoothness_range.min_spin.setValue(config["smoothness_range"][0])
            self.smoothness_range.max_spin.setValue(config["smoothness_range"][1])
        
        if "shadow_depth_range" in config:
            self.shadow_depth_range.min_spin.setValue(config["shadow_depth_range"][0])
            self.shadow_depth_range.max_spin.setValue(config["shadow_depth_range"][1])
        
        # Lighting
        if "light_intensity_range" in config:
            self.light_intensity_range.min_spin.setValue(config["light_intensity_range"][0])
            self.light_intensity_range.max_spin.setValue(config["light_intensity_range"][1])
        
        if "ambient_light_range" in config:
            self.ambient_light_range.min_spin.setValue(config["ambient_light_range"][0])
            self.ambient_light_range.max_spin.setValue(config["ambient_light_range"][1])
        
        # Uneven Surface
        if "surface_enabled" in config:
            self.surface_enabled_check.setChecked(config["surface_enabled"])
        
        if "surface_scale_range" in config:
            self.surface_scale_range.min_spin.setValue(config["surface_scale_range"][0])
            self.surface_scale_range.max_spin.setValue(config["surface_scale_range"][1])
        
        if "surface_complexity_range" in config:
            self.surface_complexity_range.min_spin.setValue(config["surface_complexity_range"][0])
            self.surface_complexity_range.max_spin.setValue(config["surface_complexity_range"][1])
        
        # Wet Surface
        if "wetness_range" in config:
            self.wetness_range.min_spin.setValue(config["wetness_range"][0])
            self.wetness_range.max_spin.setValue(config["wetness_range"][1])
        
        if "specular_intensity_range" in config:
            self.specular_intensity_range.min_spin.setValue(config["specular_intensity_range"][0])
            self.specular_intensity_range.max_spin.setValue(config["specular_intensity_range"][1])
        
        if "specular_power_range" in config:
            self.specular_power_range.min_spin.setValue(config["specular_power_range"][0])
            self.specular_power_range.max_spin.setValue(config["specular_power_range"][1])
        
        # Light Direction
        if "light_x_range" in config:
            self.light_x_range.min_spin.setValue(config["light_x_range"][0])
            self.light_x_range.max_spin.setValue(config["light_x_range"][1])
        
        if "light_y_range" in config:
            self.light_y_range.min_spin.setValue(config["light_y_range"][0])
            self.light_y_range.max_spin.setValue(config["light_y_range"][1])
        
        if "light_z_range" in config:
            self.light_z_range.min_spin.setValue(config["light_z_range"][0])
            self.light_z_range.max_spin.setValue(config["light_z_range"][1])
        
        # Generation settings
        if "num_images" in config:
            self.num_images_spin.setValue(config["num_images"])
        
        if "output_dir" in config:
            self.output_dir_edit.setText(config["output_dir"])
    
    def _create_batch_config(self):
        """Create a configuration dictionary suitable for the batch generator"""
        # Get all the parameter ranges
        range_config = self._create_range_config()
        
        # Create a configuration with ranges for batch generator to use
        # Instead of generating fixed random values, we'll pass the ranges
        # so each image can have unique random parameters
        batch_config = {}
        
        # Pass width and height ranges instead of fixed values
        batch_config['width_range'] = [
            int(range_config['width_range'][0]),
            int(range_config['width_range'][1])
        ]
        batch_config['height_range'] = [
            int(range_config['height_range'][0]),
            int(range_config['height_range'][1])
        ]
        
        # Pass parameter ranges directly instead of random values
        # Points range
        batch_config['min_points'] = int(range_config['min_points_range'][0])
        batch_config['max_points'] = int(range_config['max_points_range'][1])
        
        # Edge thickness range
        batch_config['edge_thickness_range'] = [
            int(range_config['edge_thickness_range'][0]),
            int(range_config['edge_thickness_range'][1])
        ]
        
        # Show points (fixed value)
        batch_config['show_points'] = range_config['show_points']
        
        # 3D Effect parameter ranges
        batch_config['bulge_strength_range'] = [
            float(range_config['bulge_strength_range'][0]),
            float(range_config['bulge_strength_range'][1])
        ]
        
        batch_config['roundness_range'] = [
            float(range_config['roundness_range'][0]),
            float(range_config['roundness_range'][1])
        ]
        
        # Smoothness must be odd for OpenCV GaussianBlur
        smoothness_min = int(range_config['smoothness_range'][0])
        smoothness_max = int(range_config['smoothness_range'][1])
        
        # Make sure values are odd
        if smoothness_min % 2 == 0:
            smoothness_min += 1
        if smoothness_max % 2 == 0:
            smoothness_max -= 1
        
        batch_config['smoothness_range'] = [smoothness_min, smoothness_max]
        
        batch_config['shadow_depth_range'] = [
            float(range_config['shadow_depth_range'][0]),
            float(range_config['shadow_depth_range'][1])
        ]
        
        # Lighting parameter ranges
        batch_config['light_intensity_range'] = [
            float(range_config['light_intensity_range'][0]),
            float(range_config['light_intensity_range'][1])
        ]
        
        batch_config['ambient_light_range'] = [
            float(range_config['ambient_light_range'][0]),
            float(range_config['ambient_light_range'][1])
        ]
        
        # Uneven surface parameters
        batch_config['surface_enabled'] = range_config['surface_enabled']
        
        batch_config['surface_scale_range'] = [
            float(range_config['surface_scale_range'][0]),
            float(range_config['surface_scale_range'][1])
        ]
        
        batch_config['surface_complexity_range'] = [
            float(range_config['surface_complexity_range'][0]),
            float(range_config['surface_complexity_range'][1])
        ]
        
        # Wet surface parameter ranges
        batch_config['wetness_range'] = [
            float(range_config['wetness_range'][0]),
            float(range_config['wetness_range'][1])
        ]
        
        batch_config['specular_intensity_range'] = [
            float(range_config['specular_intensity_range'][0]),
            float(range_config['specular_intensity_range'][1])
        ]
        
        batch_config['specular_power_range'] = [
            float(range_config['specular_power_range'][0]),
            float(range_config['specular_power_range'][1])
        ]
        
        # Light direction ranges
        batch_config['light_direction_range'] = [
            [float(range_config['light_x_range'][0]), float(range_config['light_x_range'][1])],
            [float(range_config['light_y_range'][0]), float(range_config['light_y_range'][1])],
            [float(range_config['light_z_range'][0]), float(range_config['light_z_range'][1])]
        ]
        
        # Set randomize_each_image flag
        batch_config['randomize_each_image'] = True
        
        # Number of images
        batch_config['num_images'] = int(range_config['num_images'])
        
        return batch_config, range_config['output_dir']
    
    def generate_patterns(self):
        """Generate patterns by creating a batch config and calling the generator script"""
        # Create the batch configuration
        batch_config, output_dir = self._create_batch_config()
        
        # Save the configuration to a temporary file
        temp_config_path = "temp_batch_config.json"
        with open(temp_config_path, 'w') as f:
            json.dump(batch_config, f, indent=2)
        
        # Update the status
        self.status_label.setText(f"Generating {batch_config['num_images']} images with random parameters...")
        self.excel_info_label.setText(f"Parameters will be saved to: {os.path.join(output_dir, 'parameters.xlsx')}")
        QApplication.processEvents()  # Make sure UI updates
        
        try:
            # Call the batch generator script
            cmd = ["python", "generate_voronoi_pairs.py", "--config", temp_config_path, "--output_dir", output_dir]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.status_label.setText(f"Successfully generated {batch_config['num_images']} images in {output_dir}")
                self.excel_info_label.setText(f"Parameters saved to: {os.path.join(output_dir, 'parameters.xlsx')}")
            else:
                error_msg = stderr.decode('utf-8')
                self.status_label.setText(f"Error generating images: {error_msg}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
        finally:
            # Clean up temporary config file
            if os.path.exists(temp_config_path):
                os.remove(temp_config_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoronoiRangeGeneratorUI()
    window.show()
    sys.exit(app.exec_())