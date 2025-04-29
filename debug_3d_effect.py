#!/usr/bin/env python3
import cv2
import numpy as np
import os
from voronoi_generator_simple import VoronoiGenerator
from image_processor import ImageProcessor

def debug_3d_effect():
    # Create output directory
    output_dir = "debug_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize generators
    voronoi_gen = VoronoiGenerator()
    image_proc = ImageProcessor()
    
    # Set parameters
    voronoi_gen.width = 800
    voronoi_gen.height = 600
    voronoi_gen.num_points = 50
    voronoi_gen.point_distribution = "random"
    voronoi_gen.edge_thickness = 2
    voronoi_gen.show_points = True
    
    # Configure 3D effect parameters
    image_proc.bulge_strength = 0.7
    image_proc.roundness = 2.0
    image_proc.smoothness = 15
    image_proc.shadow_depth = 0.8
    image_proc.light_intensity = 1.2
    image_proc.ambient_light = 0.3
    image_proc.surface_enabled = True
    image_proc.surface_scale = 0.4
    image_proc.surface_complexity = 2.0
    image_proc.wetness = 0.8
    image_proc.specular_intensity = 1.2
    image_proc.light_direction = np.array([0.5, 0.5, 1.0])
    
    print("Generating Voronoi diagram...")
    original_image, _ = voronoi_gen.generate_voronoi()
    
    # Save original image
    cv2.imwrite(os.path.join(output_dir, "original.png"), original_image)
    
    print("Creating height map...")
    height_map = image_proc.create_height_map(original_image)
    
    # Visualize height map (normalize to 0-255 for saving)
    height_viz = (height_map * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "height_map.png"), height_viz)
    
    print("Computing normal map...")
    normal_map = image_proc.compute_normal_map(height_map)
    
    # Visualize normal map (convert from -1,1 to 0,255 for visualization)
    normal_viz = ((normal_map + 1) * 127.5).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "normal_map.png"), normal_viz)
    
    print("Computing lighting...")
    # Calculate diffuse lighting only
    light_dir = image_proc.light_direction / np.linalg.norm(image_proc.light_direction)
    diffuse = np.sum(normal_map * light_dir, axis=2)
    diffuse_viz = (diffuse * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "diffuse.png"), diffuse_viz)
    
    # Calculate specular highlights
    specular = image_proc.compute_specular_highlights(normal_map)
    specular_viz = (specular * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "specular.png"), specular_viz)
    
    print("Creating final 3D effect...")
    # Apply final lighting with wet surface effect
    processed_image, _, _ = image_proc.create_3d_effect(original_image)
    
    # Save processed image
    cv2.imwrite(os.path.join(output_dir, "processed.png"), processed_image)
    
    print(f"Debug images saved to {output_dir} directory")
    print(f"Processed image shape: {processed_image.shape}, dtype: {processed_image.dtype}")
    print(f"Processed image min: {np.min(processed_image)}, max: {np.max(processed_image)}")

if __name__ == "__main__":
    debug_3d_effect() 