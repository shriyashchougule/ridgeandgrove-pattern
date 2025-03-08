#!/usr/bin/env python3
import sys
import os
import numpy as np
import cv2
from scipy.spatial import Voronoi
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk
from image_processor import ImageProcessor

# Scrollable Frame class
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # Configure the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Create a window in the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to scroll
        self.bind_mousewheel()
        
    def bind_mousewheel(self):
        # Bind mousewheel to scroll
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind for different platforms
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))  # Linux
    
    def unbind_mousewheel(self):
        # Unbind mousewheel events when the frame is not in focus
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

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
        self.root.geometry("1600x900")
        
        self.generator = VoronoiGenerator()
        self.image_processor = ImageProcessor()
        self.current_image = None
        self.processed_image = None
        self.photo_image_original = None
        self.photo_image_processed = None
        
        # Create main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable control panel
        self.control_frame_container = ttk.Frame(self.main_frame, width=350)  # Increased width for better visibility
        self.control_frame_container.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.control_frame_container.pack_propagate(False)  # Prevent container from shrinking
        
        # Add a title for the settings panel
        settings_title = ttk.Label(self.control_frame_container, text="Settings Panel", font=("Arial", 12, "bold"))
        settings_title.pack(pady=(0, 5))
        
        # Add a hint about scrolling
        scroll_hint = ttk.Label(self.control_frame_container, text="(Scroll to see more options)", font=("Arial", 8))
        scroll_hint.pack(pady=(0, 5))
        
        # Add a separator
        ttk.Separator(self.control_frame_container, orient="horizontal").pack(fill="x", padx=10, pady=5)
        
        # Create scrollable frame for controls
        self.scrollable_control_frame = ScrollableFrame(self.control_frame_container)
        self.scrollable_control_frame.pack(fill=tk.BOTH, expand=True)
        
        # Set the control frame to be the scrollable frame
        self.control_frame = self.scrollable_control_frame.scrollable_frame
        
        # Bind events to handle mousewheel focus
        self.control_frame_container.bind("<Enter>", self._on_enter_control_frame)
        self.control_frame_container.bind("<Leave>", self._on_leave_control_frame)
        
        # Create image display frame
        self.display_frame = ttk.Frame(self.main_frame)
        self.display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create two canvases for image display
        self.display_frame_top = ttk.Frame(self.display_frame)
        self.display_frame_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.display_frame_bottom = ttk.Frame(self.display_frame)
        self.display_frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # Labels for the images
        ttk.Label(self.display_frame_top, text="Original Voronoi Pattern").pack(anchor=tk.W)
        ttk.Label(self.display_frame_bottom, text="3D Bulge Effect").pack(anchor=tk.W)
        
        # Create canvases for image display
        self.canvas_original = tk.Canvas(self.display_frame_top, bg="white")
        self.canvas_original.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_processed = tk.Canvas(self.display_frame_bottom, bg="white")
        self.canvas_processed.pack(fill=tk.BOTH, expand=True)
        
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
        
        # 3D Effect controls
        effect_frame = ttk.LabelFrame(self.control_frame, text="3D Effect")
        effect_frame.pack(fill=tk.X, pady=5)
        
        # Bulge strength
        ttk.Label(effect_frame, text="Bulge Strength:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.bulge_strength_var = tk.DoubleVar(value=self.image_processor.bulge_strength)
        bulge_strength_scale = ttk.Scale(effect_frame, from_=0.1, to=1.0, variable=self.bulge_strength_var, orient=tk.HORIZONTAL)
        bulge_strength_scale.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Roundness
        ttk.Label(effect_frame, text="Roundness:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.roundness_var = tk.DoubleVar(value=self.image_processor.roundness)
        roundness_scale = ttk.Scale(effect_frame, from_=0.5, to=5.0, variable=self.roundness_var, orient=tk.HORIZONTAL)
        roundness_scale.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Smoothness
        ttk.Label(effect_frame, text="Smoothness:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.smoothness_var = tk.IntVar(value=self.image_processor.smoothness)
        smoothness_scale = ttk.Scale(effect_frame, from_=3, to=31, variable=self.smoothness_var, orient=tk.HORIZONTAL)
        smoothness_scale.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Shadow depth
        ttk.Label(effect_frame, text="Shadow Depth:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.shadow_depth_var = tk.DoubleVar(value=self.image_processor.shadow_depth)
        shadow_depth_scale = ttk.Scale(effect_frame, from_=0.1, to=1.0, variable=self.shadow_depth_var, orient=tk.HORIZONTAL)
        shadow_depth_scale.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Light intensity
        ttk.Label(effect_frame, text="Light Intensity:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.light_intensity_var = tk.DoubleVar(value=self.image_processor.light_intensity)
        light_intensity_scale = ttk.Scale(effect_frame, from_=0.1, to=2.0, variable=self.light_intensity_var, orient=tk.HORIZONTAL)
        light_intensity_scale.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Ambient light
        ttk.Label(effect_frame, text="Ambient Light:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.ambient_light_var = tk.DoubleVar(value=self.image_processor.ambient_light)
        ambient_light_scale = ttk.Scale(effect_frame, from_=0.0, to=1.0, variable=self.ambient_light_var, orient=tk.HORIZONTAL)
        ambient_light_scale.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Uneven Surface controls
        surface_frame = ttk.LabelFrame(self.control_frame, text="Uneven Surface")
        surface_frame.pack(fill=tk.X, pady=5)
        
        # Enable uneven surface
        self.surface_enabled_var = tk.BooleanVar(value=self.image_processor.surface_enabled)
        surface_enabled_check = ttk.Checkbutton(surface_frame, text="Enable Uneven Surface", variable=self.surface_enabled_var)
        surface_enabled_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Surface scale
        ttk.Label(surface_frame, text="Surface Scale:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.surface_scale_var = tk.DoubleVar(value=self.image_processor.surface_scale)
        surface_scale_scale = ttk.Scale(surface_frame, from_=0.1, to=1.0, variable=self.surface_scale_var, orient=tk.HORIZONTAL)
        surface_scale_scale.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Surface complexity
        ttk.Label(surface_frame, text="Surface Complexity:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.surface_complexity_var = tk.DoubleVar(value=self.image_processor.surface_complexity)
        surface_complexity_scale = ttk.Scale(surface_frame, from_=1.0, to=5.0, variable=self.surface_complexity_var, orient=tk.HORIZONTAL)
        surface_complexity_scale.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Surface seed
        ttk.Label(surface_frame, text="Surface Seed:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.surface_seed_var = tk.IntVar(value=self.image_processor.surface_seed)
        surface_seed_spin = ttk.Spinbox(surface_frame, from_=0, to=1000, textvariable=self.surface_seed_var, width=10)
        surface_seed_spin.grid(row=3, column=1, padx=5, pady=5)
        
        # Randomize seed button
        randomize_seed_btn = ttk.Button(surface_frame, text="Randomize Seed", 
                                        command=lambda: self.surface_seed_var.set(np.random.randint(0, 1000)))
        randomize_seed_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        # Wet Surface controls
        wet_frame = ttk.LabelFrame(self.control_frame, text="Wet Surface Effect")
        wet_frame.pack(fill=tk.X, pady=5)
        
        # Wetness
        ttk.Label(wet_frame, text="Wetness:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.wetness_var = tk.DoubleVar(value=self.image_processor.wetness)
        wetness_scale = ttk.Scale(wet_frame, from_=0.0, to=1.0, variable=self.wetness_var, orient=tk.HORIZONTAL)
        wetness_scale.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Specular intensity
        ttk.Label(wet_frame, text="Reflection Intensity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.specular_intensity_var = tk.DoubleVar(value=self.image_processor.specular_intensity)
        specular_intensity_scale = ttk.Scale(wet_frame, from_=0.0, to=2.0, variable=self.specular_intensity_var, orient=tk.HORIZONTAL)
        specular_intensity_scale.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Specular power
        ttk.Label(wet_frame, text="Reflection Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.specular_power_var = tk.DoubleVar(value=self.image_processor.specular_power)
        specular_power_scale = ttk.Scale(wet_frame, from_=5.0, to=100.0, variable=self.specular_power_var, orient=tk.HORIZONTAL)
        specular_power_scale.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Light direction controls
        ttk.Label(wet_frame, text="Light Direction:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Light direction X
        light_dir_frame = ttk.Frame(wet_frame)
        light_dir_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(light_dir_frame, text="X:").pack(side=tk.LEFT, padx=5)
        self.light_dir_x_var = tk.DoubleVar(value=self.image_processor.light_direction[0])
        light_dir_x_scale = ttk.Scale(light_dir_frame, from_=-1.0, to=1.0, variable=self.light_dir_x_var, orient=tk.HORIZONTAL)
        light_dir_x_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Light direction Y
        light_dir_frame = ttk.Frame(wet_frame)
        light_dir_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(light_dir_frame, text="Y:").pack(side=tk.LEFT, padx=5)
        self.light_dir_y_var = tk.DoubleVar(value=self.image_processor.light_direction[1])
        light_dir_y_scale = ttk.Scale(light_dir_frame, from_=-1.0, to=1.0, variable=self.light_dir_y_var, orient=tk.HORIZONTAL)
        light_dir_y_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Light direction Z
        light_dir_frame = ttk.Frame(wet_frame)
        light_dir_frame.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(light_dir_frame, text="Z:").pack(side=tk.LEFT, padx=5)
        self.light_dir_z_var = tk.DoubleVar(value=self.image_processor.light_direction[2])
        light_dir_z_scale = ttk.Scale(light_dir_frame, from_=0.1, to=2.0, variable=self.light_dir_z_var, orient=tk.HORIZONTAL)
        light_dir_z_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Reflection color
        ttk.Label(wet_frame, text="Reflection Color:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        self.reflection_color_btn = ttk.Button(wet_frame, text="Choose", command=self.choose_reflection_color)
        self.reflection_color_btn.grid(row=7, column=1, padx=5, pady=5)
        
        # Action buttons
        actions_frame = ttk.LabelFrame(self.control_frame, text="Actions")
        actions_frame.pack(fill=tk.X, pady=5)
        
        # Generate button
        generate_btn = ttk.Button(actions_frame, text="Generate", command=self.generate_voronoi)
        generate_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Save button
        save_original_btn = ttk.Button(actions_frame, text="Save Original Image", command=lambda: self.save_image("original"))
        save_original_btn.pack(fill=tk.X, padx=5, pady=5)
        
        save_processed_btn = ttk.Button(actions_frame, text="Save 3D Effect Image", command=lambda: self.save_image("processed"))
        save_processed_btn.pack(fill=tk.X, padx=5, pady=5)
    
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
    
    def choose_reflection_color(self):
        color = colorchooser.askcolor(title="Choose Reflection Color", 
                                     initialcolor=tuple(self.image_processor.reflection_color))[0]
        if color:
            rgb = np.array(list(map(int, color)))
            self.image_processor.reflection_color = rgb
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
        
        # Update image processor parameters
        self.image_processor.bulge_strength = self.bulge_strength_var.get()
        self.image_processor.roundness = self.roundness_var.get()
        self.image_processor.smoothness = self.smoothness_var.get()
        if self.image_processor.smoothness % 2 == 0:  # Ensure smoothness is odd
            self.image_processor.smoothness += 1
        self.image_processor.shadow_depth = self.shadow_depth_var.get()
        self.image_processor.light_intensity = self.light_intensity_var.get()
        self.image_processor.ambient_light = self.ambient_light_var.get()
        
        # Update uneven surface parameters
        self.image_processor.surface_enabled = self.surface_enabled_var.get()
        self.image_processor.surface_scale = self.surface_scale_var.get()
        self.image_processor.surface_complexity = self.surface_complexity_var.get()
        self.image_processor.surface_seed = self.surface_seed_var.get()
        
        # Update wet surface parameters
        self.image_processor.wetness = self.wetness_var.get()
        self.image_processor.specular_intensity = self.specular_intensity_var.get()
        self.image_processor.specular_power = self.specular_power_var.get()
        self.image_processor.light_direction = np.array([
            self.light_dir_x_var.get(),
            self.light_dir_y_var.get(),
            self.light_dir_z_var.get()
        ])
        
        try:
            # Generate the Voronoi diagram
            self.current_image, _ = self.generator.generate_voronoi()
            
            # Process the image to create 3D effect
            self.processed_image, _, _ = self.image_processor.create_3d_effect(self.current_image)
            
            # Display both images
            self.display_images()
            
        except Exception as e:
            print(f"Error generating Voronoi diagram: {e}")
    
    def display_images(self):
        # Display original image
        self.display_image(self.current_image, self.canvas_original, "original")
        
        # Display processed image
        self.display_image(self.processed_image, self.canvas_processed, "processed")
    
    def display_image(self, image, canvas, image_type):
        if image is None:
            return
            
        # Convert OpenCV image (BGR) to PIL Image (RGB)
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Resize image to fit canvas if needed
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:  # Check if canvas has been drawn
            # Calculate scaling factor to fit image in canvas
            scale_width = canvas_width / image.shape[1]
            scale_height = canvas_height / image.shape[0]
            scale = min(scale_width, scale_height)
            
            # Resize image
            new_width = int(image.shape[1] * scale)
            new_height = int(image.shape[0] * scale)
            pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert PIL Image to PhotoImage
        if image_type == "original":
            self.photo_image_original = ImageTk.PhotoImage(pil_image)
            photo_image = self.photo_image_original
        else:
            self.photo_image_processed = ImageTk.PhotoImage(pil_image)
            photo_image = self.photo_image_processed
        
        # Update canvas
        canvas.delete("all")
        canvas.create_image(
            canvas.winfo_width() // 2,
            canvas.winfo_height() // 2,
            anchor=tk.CENTER,
            image=photo_image
        )
    
    def save_image(self, image_type):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            if image_type == "original" and self.current_image is not None:
                cv2.imwrite(file_path, self.current_image)
            elif image_type == "processed" and self.processed_image is not None:
                cv2.imwrite(file_path, self.processed_image)
    
    def _on_enter_control_frame(self, event):
        # Bind mousewheel when mouse enters the control frame
        self.scrollable_control_frame.bind_mousewheel()
    
    def _on_leave_control_frame(self, event):
        # Unbind mousewheel when mouse leaves the control frame
        self.scrollable_control_frame.unbind_mousewheel()

def main():
    root = tk.Tk()
    app = VoronoiGeneratorUI(root)
    
    # Update image when window is resized
    def on_resize(event):
        if hasattr(app, 'current_image') and app.current_image is not None:
            app.display_images()
    
    root.bind("<Configure>", on_resize)
    root.mainloop()

if __name__ == "__main__":
    main() 