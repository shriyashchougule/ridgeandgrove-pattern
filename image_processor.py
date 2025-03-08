#!/usr/bin/env python3
import numpy as np
import cv2
from scipy import ndimage

class ImageProcessor:
    def __init__(self):
        self.bulge_strength = 0.5      # Controls the height of the bulges
        self.smoothness = 15           # Controls the smoothness of the bulges
        self.light_direction = np.array([0.5, 0.5, 1.0])  # Light direction vector (more from above)
        self.light_intensity = 1.2     # Light intensity
        self.ambient_light = 0.3       # Ambient light level
        self.shadow_depth = 0.7        # Controls how deep the shadows appear
        self.roundness = 2.0           # Controls how rounded the bulges appear
        
        # Uneven surface parameters
        self.surface_enabled = True    # Whether to apply the uneven surface effect
        self.surface_scale = 0.3       # Scale of the surface undulations (0.0 to 1.0)
        self.surface_complexity = 2    # Complexity of the surface (1 = simple, higher = more complex)
        self.surface_seed = 42         # Random seed for reproducible surface generation
        
        # Wet surface parameters
        self.wetness = 0.7             # Controls how wet/shiny the surface appears (0.0 to 1.0)
        self.specular_intensity = 1.0  # Controls the intensity of specular highlights
        self.specular_power = 30.0     # Controls the size of specular highlights (higher = smaller)
        self.reflection_color = np.array([255, 255, 255])  # Color of the specular highlights
        
    def create_uneven_surface(self, shape):
        """
        Create an uneven surface base using Perlin-like noise.
        """
        height, width = shape
        
        # Set random seed for reproducibility
        np.random.seed(self.surface_seed)
        
        # Create a grid of coordinates
        x = np.linspace(0, self.surface_complexity, width)
        y = np.linspace(0, self.surface_complexity, height)
        xx, yy = np.meshgrid(x, y)
        
        # Generate multiple frequencies of noise and combine them
        surface = np.zeros((height, width), dtype=np.float32)
        
        # Add different frequencies with decreasing amplitude
        amplitude = 1.0
        frequency = 1.0
        persistence = 0.5
        octaves = 4
        
        for i in range(octaves):
            # Generate noise at current frequency
            phase_x = np.random.random() * 2 * np.pi
            phase_y = np.random.random() * 2 * np.pi
            
            noise = np.sin(xx * frequency + phase_x) * np.cos(yy * frequency + phase_y)
            
            # Add to surface with current amplitude
            surface += noise * amplitude
            
            # Prepare for next octave
            amplitude *= persistence
            frequency *= 2
        
        # Normalize to [0, 1]
        surface = (surface - np.min(surface)) / (np.max(surface) - np.min(surface))
        
        # Scale by the surface scale parameter
        surface *= self.surface_scale
        
        return surface
        
    def create_height_map(self, image):
        """
        Create a height map from the Voronoi diagram.
        White areas will be high (bulges) and black lines will be low (valleys).
        """
        # Convert to grayscale if it's a color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Create a binary image to separate cells from edges
        _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        # Distance transform to create rounded bulges
        # Each pixel value is the distance to the nearest black pixel
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # Normalize the distance transform
        dist_max = np.max(dist_transform)
        if dist_max > 0:
            dist_transform = dist_transform / dist_max
        
        # Apply power function to make bulges more rounded
        height_map = np.power(dist_transform, 1.0 / self.roundness)
        
        # Apply Gaussian blur to smooth the height map
        height_map = cv2.GaussianBlur(height_map, (self.smoothness, self.smoothness), 0)
        
        # Add uneven surface if enabled
        if self.surface_enabled:
            surface = self.create_uneven_surface(height_map.shape)
            
            # Combine the height map with the uneven surface
            # The surface affects both the high and low areas
            height_map = height_map + surface
            
            # Renormalize to [0, 1]
            height_map = (height_map - np.min(height_map)) / (np.max(height_map) - np.min(height_map))
        
        # Scale the height map by the bulge strength
        height_map = height_map * self.bulge_strength
        
        return height_map
    
    def compute_normal_map(self, height_map):
        """
        Compute the normal map from the height map using Sobel operators.
        """
        # Compute gradients using Sobel operators
        grad_x = cv2.Sobel(height_map, cv2.CV_32F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(height_map, cv2.CV_32F, 0, 1, ksize=3)
        
        # Create normal map
        normal_map = np.zeros((height_map.shape[0], height_map.shape[1], 3), dtype=np.float32)
        
        # X and Y components (inverted because gradient points to higher areas)
        normal_map[:, :, 0] = -grad_x
        normal_map[:, :, 1] = -grad_y
        
        # Z component (constant for now)
        normal_map[:, :, 2] = 1.0
        
        # Normalize to unit vectors
        norm = np.sqrt(np.sum(normal_map**2, axis=2, keepdims=True))
        normal_map = normal_map / (norm + 1e-10)  # Add small epsilon to avoid division by zero
        
        return normal_map
    
    def compute_specular_highlights(self, normal_map, view_direction=np.array([0, 0, 1])):
        """
        Compute specular highlights to create a wet/shiny appearance.
        Uses the Blinn-Phong reflection model.
        """
        # Normalize view direction
        view_dir = view_direction / np.linalg.norm(view_direction)
        
        # Normalize light direction
        light_dir = self.light_direction / np.linalg.norm(self.light_direction)
        
        # Calculate half-vector between view and light directions
        half_vector = (view_dir + light_dir) / np.linalg.norm(view_dir + light_dir)
        
        # Compute specular term (dot product of normal and half-vector)
        # raised to a power to control the size of the highlight
        specular = np.maximum(0, np.sum(normal_map * half_vector, axis=2))
        specular = np.power(specular, self.specular_power)
        
        # Scale by specular intensity and wetness
        specular = specular * self.specular_intensity * self.wetness
        
        return specular
    
    def apply_lighting(self, normal_map, height_map, original_image=None):
        """
        Apply lighting to the normal map to create a 3D effect with wet surface appearance.
        """
        # Normalize light direction
        light_dir = self.light_direction / np.linalg.norm(self.light_direction)
        
        # Compute diffuse lighting (dot product of normal and light direction)
        diffuse = np.sum(normal_map * light_dir, axis=2)
        
        # Add shadow effect based on height map
        shadow = 1.0 - (1.0 - height_map) * self.shadow_depth
        
        # Combine diffuse lighting with shadow
        lighting = diffuse * shadow
        
        # Apply light intensity and ambient light
        lighting = self.ambient_light + lighting * self.light_intensity
        lighting = np.clip(lighting, 0, 1)
        
        # Compute specular highlights for wet appearance
        specular = self.compute_specular_highlights(normal_map)
        
        # Create the lit image
        if original_image is not None and len(original_image.shape) == 3:
            # Create a white base image
            base_color = np.ones_like(original_image) * 255
            
            # Apply lighting to create shadows
            lit_image = base_color * lighting[:, :, np.newaxis]
            
            # Add specular highlights
            reflection_color = self.reflection_color.reshape(1, 1, 3)
            lit_image = lit_image + specular[:, :, np.newaxis] * reflection_color
            
            lit_image = np.clip(lit_image, 0, 255).astype(np.uint8)
        else:
            # Create grayscale lit image
            lit_image = (lighting * 255).astype(np.uint8)
            lit_image = cv2.cvtColor(lit_image, cv2.COLOR_GRAY2BGR)
            
            # Add specular highlights
            reflection_color = self.reflection_color.reshape(1, 1, 3)
            lit_image = lit_image + (specular[:, :, np.newaxis] * reflection_color).astype(np.uint8)
            lit_image = np.clip(lit_image, 0, 255).astype(np.uint8)
        
        return lit_image
    
    def create_3d_effect(self, image):
        """
        Process the input Voronoi image to create a 3D bulge effect with wet surface appearance.
        """
        # Create height map
        height_map = self.create_height_map(image)
        
        # Compute normal map
        normal_map = self.compute_normal_map(height_map)
        
        # Apply lighting with wet surface effect
        result = self.apply_lighting(normal_map, height_map, image)
        
        # Enhance contrast
        result = cv2.convertScaleAbs(result, alpha=1.1, beta=5)
        
        return result, height_map, normal_map 