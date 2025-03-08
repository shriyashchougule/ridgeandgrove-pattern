#!/usr/bin/env python3
import sys
import os
import numpy as np
import cv2
from scipy.spatial import Voronoi
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk

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
        bg_color = self.background_color
        if isinstance(bg_color, tuple):
            bg_color = np.array(bg_color, dtype=np.uint8)
        image = np.ones((self.height, self.width, 3), dtype=np.uint8) * bg_color
        
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

class VoronoiGeneratorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voronoi Pattern Generator")
        self.root.geometry("1200x800")
        
        self.generator = VoronoiGenerator()
        self.current_image = None
        self.photo_image = None
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create control panel
        self.control_frame = ttk.Frame(self.main_frame, width=300)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Create image display frame
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for image display
        self.canvas = tk.Canvas(self.display_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create controls
        self.create_controls()
        
        # Generate initial image
        self.root.update()  # Update to get correct canvas size
        self.generate_voronoi()
    
    def create_controls(self):
        # Image size controls
        size_frame = ttk.LabelFrame(self.control_frame, text="Image Size")
        size_frame.pack(fill=tk.X, pady=5)
        
        # Width control
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.width_var = tk.IntVar(value=self.generator.width)
        width_spin = ttk.Spinbox(size_frame, from_=100, to=3000, textvariable=self.width_var, width=10)
        width_spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Height control
        ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.height_var = tk.IntVar(value=self.generator.height)
        height_spin = ttk.Spinbox(size_frame, from_=100, to=3000, textvariable=self.height_var, width=10)
        height_spin.grid(row=1, column=1, padx=5, pady=5)
        
        # Points controls
        points_frame = ttk.LabelFrame(self.control_frame, text="Points")
        points_frame.pack(fill=tk.X, pady=5)
        
        # Number of points
        ttk.Label(points_frame, text="Number of Points:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.num_points_var = tk.IntVar(value=self.generator.num_points)
        num_points_spin = ttk.Spinbox(points_frame, from_=3, to=1000, textvariable=self.num_points_var, width=10)
        num_points_spin.grid(row=0, column=1, padx=5, pady=5)
        
        # Point distribution
        ttk.Label(points_frame, text="Distribution:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.dist_var = tk.StringVar(value=self.generator.point_distribution)
        dist_combo = ttk.Combobox(points_frame, textvariable=self.dist_var, values=["random", "grid"], width=10)
        dist_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Show points
        self.show_points_var = tk.BooleanVar(value=self.generator.show_points)
        show_points_check = ttk.Checkbutton(points_frame, text="Show Points", variable=self.show_points_var)
        show_points_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Point size
        ttk.Label(points_frame, text="Point Size:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.point_size_var = tk.IntVar(value=self.generator.point_size)
        point_size_scale = ttk.Scale(points_frame, from_=1, to=10, variable=self.point_size_var, orient=tk.HORIZONTAL)
        point_size_scale.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Appearance controls
        appearance_frame = ttk.LabelFrame(self.control_frame, text="Appearance")
        appearance_frame.pack(fill=tk.X, pady=5)
        
        # Edge thickness
        ttk.Label(appearance_frame, text="Edge Thickness:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.edge_thickness_var = tk.IntVar(value=self.generator.edge_thickness)
        edge_thickness_scale = ttk.Scale(appearance_frame, from_=1, to=10, variable=self.edge_thickness_var, orient=tk.HORIZONTAL)
        edge_thickness_scale.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Edge color
        ttk.Label(appearance_frame, text="Edge Color:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.edge_color_btn = ttk.Button(appearance_frame, text="Choose", command=lambda: self.choose_color("edge"))
        self.edge_color_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # Point color
        ttk.Label(appearance_frame, text="Point Color:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.point_color_btn = ttk.Button(appearance_frame, text="Choose", command=lambda: self.choose_color("point"))
        self.point_color_btn.grid(row=2, column=1, padx=5, pady=5)
        
        # Background color
        ttk.Label(appearance_frame, text="Background Color:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.bg_color_btn = ttk.Button(appearance_frame, text="Choose", command=lambda: self.choose_color("background"))
        self.bg_color_btn.grid(row=3, column=1, padx=5, pady=5)
        
        # Action buttons
        actions_frame = ttk.LabelFrame(self.control_frame, text="Actions")
        actions_frame.pack(fill=tk.X, pady=5)
        
        # Generate button
        generate_btn = ttk.Button(actions_frame, text="Generate", command=self.generate_voronoi)
        generate_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Save button
        save_btn = ttk.Button(actions_frame, text="Save Image", command=self.save_image)
        save_btn.pack(fill=tk.X, padx=5, pady=5)
    
    def choose_color(self, color_type):
        color = colorchooser.askcolor(title=f"Choose {color_type} color")[0]
        if color:
            rgb = tuple(map(int, color))
            
            if color_type == "edge":
                self.generator.edge_color = rgb
            elif color_type == "point":
                self.generator.point_color = rgb
            elif color_type == "background":
                self.generator.background_color = rgb
            
            self.generate_voronoi()
    
    def generate_voronoi(self):
        # Update generator parameters from UI
        self.generator.width = self.width_var.get()
        self.generator.height = self.height_var.get()
        self.generator.num_points = self.num_points_var.get()
        self.generator.point_distribution = self.dist_var.get()
        self.generator.show_points = self.show_points_var.get()
        self.generator.edge_thickness = self.edge_thickness_var.get()
        self.generator.point_size = self.point_size_var.get()
        
        # Generate the Voronoi diagram
        try:
            self.current_image, _ = self.generator.generate_voronoi()
            
            # Convert OpenCV image (BGR) to PIL Image (RGB)
            pil_image = Image.fromarray(cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB))
            
            # Resize image to fit canvas if needed
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Check if canvas has been drawn
                # Calculate scaling factor to fit image in canvas
                scale_width = canvas_width / self.generator.width
                scale_height = canvas_height / self.generator.height
                scale = min(scale_width, scale_height)
                
                # Resize image
                new_width = int(self.generator.width * scale)
                new_height = int(self.generator.height * scale)
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert PIL Image to PhotoImage
            self.photo_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width() // 2,
                self.canvas.winfo_height() // 2,
                anchor=tk.CENTER,
                image=self.photo_image
            )
        except Exception as e:
            print(f"Error generating Voronoi diagram: {e}")
    
    def save_image(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path and self.current_image is not None:
            cv2.imwrite(file_path, self.current_image)

def main():
    root = tk.Tk()
    app = VoronoiGeneratorUI(root)
    
    # Update image when window is resized
    def on_resize(event):
        if hasattr(app, 'current_image') and app.current_image is not None:
            app.generate_voronoi()
    
    root.bind("<Configure>", on_resize)
    root.mainloop()

if __name__ == "__main__":
    main() 