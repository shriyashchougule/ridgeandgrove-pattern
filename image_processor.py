#!/usr/bin/env python3
import numpy as np
import cv2
from scipy import ndimage

class ImageProcessor:
    def __init__(self):
        self.bulge_strength = 0.5  # Controls the height of the bulges
        self.smoothness = 15       # Controls the smoothness of the bulges
        self.light_direction = np.array([1.0, 1.0, 0.5])  # Light direction vector
        self.light_intensity = 1.0  # Light intensity
        self.ambient_light = 0.3   # Ambient light level
        
    def create_height_map(self, image):
        """
        Create a height map from the Voronoi diagram.
        White areas will be high (bulges) and black lines will be low (ridges).
        """
        # Convert to grayscale if it's a color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Invert so that white areas are high and black areas are low
        height_map = gray.astype(np.float32) / 255.0
        
        # Apply Gaussian blur to smooth the height map
        height_map = cv2.GaussianBlur(height_map, (self.smoothness, self.smoothness), 0)
        
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
    
    def apply_lighting(self, normal_map, original_image=None):
        """
        Apply lighting to the normal map to create a 3D effect.
        """
        # Normalize light direction
        light_dir = self.light_direction / np.linalg.norm(self.light_direction)
        
        # Compute diffuse lighting (dot product of normal and light direction)
        diffuse = np.sum(normal_map * light_dir, axis=2)
        diffuse = np.clip(diffuse, 0, 1)  # Clamp to [0, 1]
        
        # Apply light intensity and ambient light
        lighting = self.ambient_light + diffuse * self.light_intensity
        lighting = np.clip(lighting, 0, 1)
        
        # Create the lit image
        if original_image is not None and len(original_image.shape) == 3:
            # Use original image colors
            hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # Apply lighting to value channel
            v = (v.astype(np.float32) / 255.0) * lighting
            v = np.clip(v * 255, 0, 255).astype(np.uint8)
            
            # Merge channels and convert back to BGR
            hsv = cv2.merge([h, s, v])
            lit_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        else:
            # Create grayscale lit image
            lit_image = (lighting * 255).astype(np.uint8)
            lit_image = cv2.cvtColor(lit_image, cv2.COLOR_GRAY2BGR)
        
        return lit_image
    
    def create_3d_effect(self, image):
        """
        Process the input Voronoi image to create a 3D bulge effect.
        """
        # Create height map
        height_map = self.create_height_map(image)
        
        # Compute normal map
        normal_map = self.compute_normal_map(height_map)
        
        # Apply lighting
        result = self.apply_lighting(normal_map, image)
        
        # Enhance contrast
        result = cv2.convertScaleAbs(result, alpha=1.2, beta=0)
        
        return result, height_map, normal_map 