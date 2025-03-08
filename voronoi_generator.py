#!/usr/bin/env python3
import sys
import os
import numpy as np
import cv2
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QSlider, QComboBox, QCheckBox, 
                            QPushButton, QFileDialog, QSpinBox, QGroupBox, QColorDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class VoronoiGenerator:
    def __init__(self):
        self.width = 800
        self.height = 600
        self.num_points = 50
        self.point_distribution = "random"
        self.show_points = True
        self.edge_color = (0, 0, 0)  # Black
        self.point_color = (255, 0, 0)  # Red
        self.background_color = (255, 255, 255)  # White
        self.edge_thickness = 1
        self.point_size = 3
        
    def generate_points(self):
        if self.point_distribution == "random":
            # Generate random points
            points = np.random.rand(self.num_points, 2)
            # Scale points to image dimensions
            points[:, 0] *= self.width
            points[:, 1] *= self.height
        elif self.point_distribution == "grid":
            # Calculate grid dimensions
            grid_cols = int(np.ceil(np.sqrt(self.num_points * self.width / self.height)))
            grid_rows = int(np.ceil(self.num_points / grid_cols))
            
            # Generate grid points
            x = np.linspace(0, self.width, grid_cols)
            y = np.linspace(0, self.height, grid_rows)
            xx, yy = np.meshgrid(x, y)
            
            # Flatten and combine coordinates
            points = np.vstack([xx.flatten(), yy.flatten()]).T
            
            # Limit to requested number of points
            points = points[:self.num_points]
            
            # Add small random offset to make it less regular
            points += np.random.normal(0, min(self.width, self.height) * 0.02, points.shape)
        else:
            raise ValueError(f"Unknown point distribution: {self.point_distribution}")
            
        return points
    
    def generate_voronoi(self):
        # Create a blank image
        image = np.ones((self.height, self.width, 3), dtype=np.uint8) * self.background_color
        
        # Generate seed points
        points = self.generate_points()
        
        # Add points at the corners of the image to ensure the diagram covers the entire image
        corner_points = np.array([
            [-self.width, -self.height],
            [-self.width, 2*self.height],
            [2*self.width, -self.height],
            [2*self.width, 2*self.height]
        ])
        all_points = np.vstack([points, corner_points])
        
        # Compute Voronoi diagram
        vor = Voronoi(all_points)
        
        # Draw Voronoi edges
        for simplex in vor.ridge_vertices:
            if -1 not in simplex:  # Skip ridges that go to infinity
                p1 = vor.vertices[simplex[0]]
                p2 = vor.vertices[simplex[1]]
                
                # Check if the line is within the image bounds
                if (0 <= p1[0] <= self.width and 0 <= p1[1] <= self.height) or \
                   (0 <= p2[0] <= self.width and 0 <= p2[1] <= self.height):
                    # Convert to integer coordinates
                    p1 = (int(p1[0]), int(p1[1]))
                    p2 = (int(p2[0]), int(p2[1]))
                    
                    # Draw the line
                    cv2.line(image, p1, p2, self.edge_color, self.edge_thickness)
        
        # Draw seed points if requested
        if self.show_points:
            for point in points:
                x, y = int(point[0]), int(point[1])
                if 0 <= x < self.width and 0 <= y < self.height:
                    cv2.circle(image, (x, y), self.point_size, self.point_color, -1)
        
        return image, points

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.ax.set_axis_off()

class VoronoiGeneratorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generator = VoronoiGenerator()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Voronoi Pattern Generator')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left panel for controls
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        
        # Image size controls
        size_group = QGroupBox("Image Size")
        size_layout = QVBoxLayout()
        
        # Width control
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 3000)
        self.width_spin.setValue(self.generator.width)
        self.width_spin.setSingleStep(100)
        width_layout.addWidget(self.width_spin)
        size_layout.addLayout(width_layout)
        
        # Height control
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 3000)
        self.height_spin.setValue(self.generator.height)
        self.height_spin.setSingleStep(100)
        height_layout.addWidget(self.height_spin)
        size_layout.addLayout(height_layout)
        
        size_group.setLayout(size_layout)
        control_layout.addWidget(size_group)
        
        # Points controls
        points_group = QGroupBox("Points")
        points_layout = QVBoxLayout()
        
        # Number of points
        num_points_layout = QHBoxLayout()
        num_points_layout.addWidget(QLabel("Number of Points:"))
        self.num_points_spin = QSpinBox()
        self.num_points_spin.setRange(3, 1000)
        self.num_points_spin.setValue(self.generator.num_points)
        num_points_layout.addWidget(self.num_points_spin)
        points_layout.addLayout(num_points_layout)
        
        # Point distribution
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Distribution:"))
        self.dist_combo = QComboBox()
        self.dist_combo.addItems(["random", "grid"])
        dist_layout.addWidget(self.dist_combo)
        points_layout.addLayout(dist_layout)
        
        # Show points
        self.show_points_check = QCheckBox("Show Points")
        self.show_points_check.setChecked(self.generator.show_points)
        points_layout.addWidget(self.show_points_check)
        
        # Point size
        point_size_layout = QHBoxLayout()
        point_size_layout.addWidget(QLabel("Point Size:"))
        self.point_size_slider = QSlider(Qt.Horizontal)
        self.point_size_slider.setRange(1, 10)
        self.point_size_slider.setValue(self.generator.point_size)
        point_size_layout.addWidget(self.point_size_slider)
        points_layout.addLayout(point_size_layout)
        
        points_group.setLayout(points_layout)
        control_layout.addWidget(points_group)
        
        # Appearance controls
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()
        
        # Edge thickness
        edge_thickness_layout = QHBoxLayout()
        edge_thickness_layout.addWidget(QLabel("Edge Thickness:"))
        self.edge_thickness_slider = QSlider(Qt.Horizontal)
        self.edge_thickness_slider.setRange(1, 10)
        self.edge_thickness_slider.setValue(self.generator.edge_thickness)
        edge_thickness_layout.addWidget(self.edge_thickness_slider)
        appearance_layout.addLayout(edge_thickness_layout)
        
        # Color controls
        # Edge color
        edge_color_layout = QHBoxLayout()
        edge_color_layout.addWidget(QLabel("Edge Color:"))
        self.edge_color_btn = QPushButton()
        self.edge_color_btn.setStyleSheet(f"background-color: rgb{self.generator.edge_color}")
        self.edge_color_btn.clicked.connect(lambda: self.choose_color("edge"))
        edge_color_layout.addWidget(self.edge_color_btn)
        appearance_layout.addLayout(edge_color_layout)
        
        # Point color
        point_color_layout = QHBoxLayout()
        point_color_layout.addWidget(QLabel("Point Color:"))
        self.point_color_btn = QPushButton()
        self.point_color_btn.setStyleSheet(f"background-color: rgb{self.generator.point_color}")
        self.point_color_btn.clicked.connect(lambda: self.choose_color("point"))
        point_color_layout.addWidget(self.point_color_btn)
        appearance_layout.addLayout(point_color_layout)
        
        # Background color
        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(QLabel("Background Color:"))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setStyleSheet(f"background-color: rgb{self.generator.background_color}")
        self.bg_color_btn.clicked.connect(lambda: self.choose_color("background"))
        bg_color_layout.addWidget(self.bg_color_btn)
        appearance_layout.addLayout(bg_color_layout)
        
        appearance_group.setLayout(appearance_layout)
        control_layout.addWidget(appearance_group)
        
        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        # Generate button
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.generate_voronoi)
        actions_layout.addWidget(self.generate_btn)
        
        # Save button
        self.save_btn = QPushButton("Save Image")
        self.save_btn.clicked.connect(self.save_image)
        actions_layout.addWidget(self.save_btn)
        
        actions_group.setLayout(actions_layout)
        control_layout.addWidget(actions_group)
        
        # Add stretch to push controls to the top
        control_layout.addStretch(1)
        
        control_panel.setLayout(control_layout)
        control_panel.setFixedWidth(300)
        
        # Right panel for image display
        self.canvas = MatplotlibCanvas(self)
        
        # Add panels to main layout
        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.canvas)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Generate initial image
        self.generate_voronoi()
    
    def choose_color(self, color_type):
        color_dialog = QColorDialog(self)
        if color_dialog.exec_():
            color = color_dialog.selectedColor()
            rgb = (color.red(), color.green(), color.blue())
            
            if color_type == "edge":
                self.generator.edge_color = rgb
                self.edge_color_btn.setStyleSheet(f"background-color: rgb{rgb}")
            elif color_type == "point":
                self.generator.point_color = rgb
                self.point_color_btn.setStyleSheet(f"background-color: rgb{rgb}")
            elif color_type == "background":
                self.generator.background_color = rgb
                self.bg_color_btn.setStyleSheet(f"background-color: rgb{rgb}")
            
            self.generate_voronoi()
    
    def generate_voronoi(self):
        # Update generator parameters from UI
        self.generator.width = self.width_spin.value()
        self.generator.height = self.height_spin.value()
        self.generator.num_points = self.num_points_spin.value()
        self.generator.point_distribution = self.dist_combo.currentText()
        self.generator.show_points = self.show_points_check.isChecked()
        self.generator.edge_thickness = self.edge_thickness_slider.value()
        self.generator.point_size = self.point_size_slider.value()
        
        # Generate the Voronoi diagram
        image, _ = self.generator.generate_voronoi()
        
        # Display the image
        self.canvas.ax.clear()
        self.canvas.ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        self.canvas.ax.set_axis_off()
        self.canvas.fig.tight_layout()
        self.canvas.draw()
    
    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
        if file_path:
            image, _ = self.generator.generate_voronoi()
            cv2.imwrite(file_path, image)

def main():
    app = QApplication(sys.argv)
    window = VoronoiGeneratorUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 