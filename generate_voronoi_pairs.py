#!/usr/bin/env python3
import os
import sys
import numpy as np
import cv2
import argparse
import time
import hashlib
from tqdm import tqdm
import pandas as pd
from image_processor import ImageProcessor
from voronoi_generator_simple import VoronoiGenerator

def generate_image_pairs(config, output_dir):
    """
    Generate pairs of Voronoi pattern images (original and 3D effect).
    
    Args:
        config: Dictionary with generation parameters or parameter ranges
        output_dir: Directory to save the generated image pairs
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create generators
    voronoi_gen = VoronoiGenerator()
    image_proc = ImageProcessor()
    
    # Check if we should randomize parameters for each image
    randomize_each_image = config.get('randomize_each_image', False)
    
    # Create a list to store parameters for each image
    params_data = []
    
    # Create a set to track parameter combinations to avoid duplicates
    used_parameter_hashes = set()
    
    # Get default width and height (used only if ranges aren't provided)
    default_width = config.get('width', 800)
    default_height = config.get('height', 600)
    
    # Get width and height ranges if provided
    width_range = config.get('width_range', [default_width, default_width])
    height_range = config.get('height_range', [default_height, default_height])
    
    # Static parameters or default values if ranges aren't provided
    if not randomize_each_image:
        voronoi_gen.edge_thickness = config.get('edge_thickness', 1)
        voronoi_gen.show_points = config.get('show_points', False)
        
        # Configure 3D effect parameters
        image_proc.bulge_strength = config.get('bulge_strength', 0.5)
        image_proc.roundness = config.get('roundness', 2.0)
        image_proc.smoothness = config.get('smoothness', 15)
        image_proc.shadow_depth = config.get('shadow_depth', 0.7)
        image_proc.light_intensity = config.get('light_intensity', 1.2)
        image_proc.ambient_light = config.get('ambient_light', 0.3)
        
        # Configure uneven surface effect
        image_proc.surface_enabled = config.get('surface_enabled', True)
        image_proc.surface_scale = config.get('surface_scale', 0.3)
        image_proc.surface_complexity = config.get('surface_complexity', 2.0)
        
        # Configure wet surface effect
        image_proc.wetness = config.get('wetness', 0.7)
        image_proc.specular_intensity = config.get('specular_intensity', 1.0)
        image_proc.specular_power = config.get('specular_power', 30.0)
        image_proc.light_direction = np.array(config.get('light_direction', [0.5, 0.5, 1.0]))
    
    # Get number of images to generate and point range
    num_images = config.get('num_images', 10)
    min_points = config.get('min_points', 20)
    max_points = config.get('max_points', 100)
    
    # Generate image pairs
    print(f"Generating {num_images} image pairs...")
    for i in tqdm(range(num_images)):
        # Set a unique seed for this image generation that's within the valid range (0 to 2^32-1)
        base_seed = (int(time.time() * 1000) + i * 1000) % (2**32 - 1)
        
        # Keep generating new parameter sets until we get a unique one
        duplicate_found = True
        attempts = 0
        max_attempts = 20
        
        while duplicate_found and attempts < max_attempts:
            # Randomize image dimensions for each image
            seed_value = (base_seed + 5000 + attempts * 19) % (2**32 - 1)
            np.random.seed(seed_value)
            
            # Randomize width and height from their ranges
            voronoi_gen.width = int(np.random.randint(width_range[0], width_range[1] + 1))
            voronoi_gen.height = int(np.random.randint(height_range[0], height_range[1] + 1))
            
            # Use different seeds for different parameter groups, ensuring they're within range
            seed_value = (base_seed + attempts * 123) % (2**32 - 1)
            np.random.seed(seed_value)
            
            # Always randomize point count and surface seed for diversity
            voronoi_gen.num_points = np.random.randint(min_points, max_points + 1)
            image_proc.surface_seed = np.random.randint(0, 10000)  # Increased range
            
            # Use a completely different seed for point distribution
            seed_value = (base_seed + 10000 + attempts * 57) % (2**32 - 1)
            np.random.seed(seed_value)
            voronoi_gen.point_distribution = np.random.choice(['random', 'grid'])
            
            # If randomize_each_image is True, set parameters randomly for each image
            if randomize_each_image:
                # Use different random seeds for different parameter groups
                
                # Edge settings - use a different seed
                seed_value = (base_seed + 20000 + attempts * 31) % (2**32 - 1)
                np.random.seed(seed_value)
                if 'edge_thickness_range' in config:
                    edge_min, edge_max = config['edge_thickness_range']
                    voronoi_gen.edge_thickness = np.random.randint(edge_min, edge_max + 1)
                else:
                    voronoi_gen.edge_thickness = config.get('edge_thickness', 1)
                
                voronoi_gen.show_points = config.get('show_points', False)
                
                # 3D effect parameters - use another seed
                seed_value = (base_seed + 30000 + attempts * 77) % (2**32 - 1)
                np.random.seed(seed_value)
                if 'bulge_strength_range' in config:
                    bulge_min, bulge_max = config['bulge_strength_range']
                    image_proc.bulge_strength = np.random.uniform(bulge_min, bulge_max)
                else:
                    image_proc.bulge_strength = config.get('bulge_strength', 0.5)
                
                if 'roundness_range' in config:
                    round_min, round_max = config['roundness_range']
                    image_proc.roundness = np.random.uniform(round_min, round_max)
                else:
                    image_proc.roundness = config.get('roundness', 2.0)
                
                if 'smoothness_range' in config:
                    smooth_min, smooth_max = config['smoothness_range']
                    # Generate a random odd value in the range
                    if smooth_min <= smooth_max:
                        smoothness_values = list(range(smooth_min, smooth_max + 1, 2))
                        if smoothness_values:
                            image_proc.smoothness = np.random.choice(smoothness_values)
                        else:
                            image_proc.smoothness = smooth_min if smooth_min % 2 == 1 else smooth_min + 1
                    else:
                        image_proc.smoothness = smooth_min
                else:
                    image_proc.smoothness = config.get('smoothness', 15)
                
                if 'shadow_depth_range' in config:
                    shadow_min, shadow_max = config['shadow_depth_range']
                    image_proc.shadow_depth = np.random.uniform(shadow_min, shadow_max)
                else:
                    image_proc.shadow_depth = config.get('shadow_depth', 0.7)
                
                # Lighting parameters - different seed
                seed_value = (base_seed + 40000 + attempts * 91) % (2**32 - 1)
                np.random.seed(seed_value)
                if 'light_intensity_range' in config:
                    light_int_min, light_int_max = config['light_intensity_range']
                    image_proc.light_intensity = np.random.uniform(light_int_min, light_int_max)
                else:
                    image_proc.light_intensity = config.get('light_intensity', 1.2)
                
                if 'ambient_light_range' in config:
                    ambient_min, ambient_max = config['ambient_light_range']
                    image_proc.ambient_light = np.random.uniform(ambient_min, ambient_max)
                else:
                    image_proc.ambient_light = config.get('ambient_light', 0.3)
                
                # Uneven surface parameters - different seed
                seed_value = (base_seed + 50000 + attempts * 103) % (2**32 - 1)
                np.random.seed(seed_value)
                image_proc.surface_enabled = config.get('surface_enabled', True)
                
                if 'surface_scale_range' in config:
                    surf_scale_min, surf_scale_max = config['surface_scale_range']
                    image_proc.surface_scale = np.random.uniform(surf_scale_min, surf_scale_max)
                else:
                    image_proc.surface_scale = config.get('surface_scale', 0.3)
                
                if 'surface_complexity_range' in config:
                    surf_complex_min, surf_complex_max = config['surface_complexity_range']
                    image_proc.surface_complexity = np.random.uniform(surf_complex_min, surf_complex_max)
                else:
                    image_proc.surface_complexity = config.get('surface_complexity', 2.0)
                
                # Wet surface parameters - different seed
                seed_value = (base_seed + 60000 + attempts * 119) % (2**32 - 1)
                np.random.seed(seed_value)
                if 'wetness_range' in config:
                    wet_min, wet_max = config['wetness_range']
                    image_proc.wetness = np.random.uniform(wet_min, wet_max)
                else:
                    image_proc.wetness = config.get('wetness', 0.7)
                
                if 'specular_intensity_range' in config:
                    spec_int_min, spec_int_max = config['specular_intensity_range']
                    image_proc.specular_intensity = np.random.uniform(spec_int_min, spec_int_max)
                else:
                    image_proc.specular_intensity = config.get('specular_intensity', 1.0)
                
                if 'specular_power_range' in config:
                    spec_pow_min, spec_pow_max = config['specular_power_range']
                    image_proc.specular_power = np.random.uniform(spec_pow_min, spec_pow_max)
                else:
                    image_proc.specular_power = config.get('specular_power', 30.0)
                
                # Light direction - different seed
                seed_value = (base_seed + 70000 + attempts * 137) % (2**32 - 1)
                np.random.seed(seed_value)
                if 'light_direction_range' in config:
                    x_range, y_range, z_range = config['light_direction_range']
                    light_x = np.random.uniform(x_range[0], x_range[1])
                    light_y = np.random.uniform(y_range[0], y_range[1])
                    light_z = np.random.uniform(z_range[0], z_range[1])
                    image_proc.light_direction = np.array([light_x, light_y, light_z])
                else:
                    # Add small random variations even if ranges aren't provided
                    default_light = config.get('light_direction', [0.5, 0.5, 1.0])
                    variations = np.random.uniform(-0.1, 0.1, 3)
                    light_dir = [default_light[0] + variations[0], 
                                default_light[1] + variations[1], 
                                default_light[2] + variations[2]]
                    image_proc.light_direction = np.array(light_dir)
            
            # Create a hash of the key parameters to check for duplicates
            param_hash = _create_parameter_hash(voronoi_gen, image_proc)
            
            # Check if this parameter set is unique
            if param_hash not in used_parameter_hashes:
                used_parameter_hashes.add(param_hash)
                duplicate_found = False
            else:
                attempts += 1
                # Scramble the base seed further if we're getting duplicates, but keep within valid range
                base_seed = (base_seed + int(time.time() * 100) + np.random.randint(0, 10000)) % (2**32 - 1)
        
        # If we couldn't find a unique set after max attempts, just go with the last one
        if attempts == max_attempts:
            print(f"Warning: Could not generate completely unique parameters for image {i} after {max_attempts} attempts")
        
        # Generate the Voronoi diagram
        original_image, _ = voronoi_gen.generate_voronoi()
        
        # Process the image to create 3D effect
        processed_image, _, _ = image_proc.create_3d_effect(original_image)
        
        # Invert the original image (make background black and lines white)
        inverted_original = cv2.bitwise_not(original_image)
        
        # Save the image pair
        filename_base = f"voronoi_pair_{i:04d}"
        cv2.imwrite(os.path.join(output_dir, f"{filename_base}_original.png"), inverted_original)
        cv2.imwrite(os.path.join(output_dir, f"{filename_base}_3d_effect.png"), processed_image)
        
        # Store parameters for this image
        image_params = {
            'image_name': filename_base,
            # Basic parameters
            'width': voronoi_gen.width,
            'height': voronoi_gen.height,
            'num_points': voronoi_gen.num_points,
            'point_distribution': voronoi_gen.point_distribution,
            'edge_thickness': voronoi_gen.edge_thickness,
            'show_points': voronoi_gen.show_points,
            
            # 3D Effect parameters
            'bulge_strength': image_proc.bulge_strength,
            'roundness': image_proc.roundness,
            'smoothness': image_proc.smoothness,
            'shadow_depth': image_proc.shadow_depth,
            
            # Lighting parameters
            'light_intensity': image_proc.light_intensity,
            'ambient_light': image_proc.ambient_light,
            
            # Uneven surface parameters
            'surface_enabled': image_proc.surface_enabled,
            'surface_scale': image_proc.surface_scale,
            'surface_complexity': image_proc.surface_complexity,
            'surface_seed': image_proc.surface_seed,
            
            # Wet surface parameters
            'wetness': image_proc.wetness,
            'specular_intensity': image_proc.specular_intensity,
            'specular_power': image_proc.specular_power,
            
            # Light direction
            'light_direction_x': image_proc.light_direction[0],
            'light_direction_y': image_proc.light_direction[1],
            'light_direction_z': image_proc.light_direction[2]
        }
        params_data.append(image_params)
    
    # Create Excel file with all parameters
    if params_data:
        df = pd.DataFrame(params_data)
        excel_path = os.path.join(output_dir, "parameters.xlsx")
        df.to_excel(excel_path, index=False)
        print(f"Parameter data saved to {excel_path}")
    
    print(f"Done! {num_images} image pairs saved to {output_dir}")

def _create_parameter_hash(voronoi_gen, image_proc):
    """Create a hash of the parameters to identify unique combinations"""
    param_str = f"{voronoi_gen.num_points}_{voronoi_gen.point_distribution}_{voronoi_gen.edge_thickness}_"
    param_str += f"{image_proc.bulge_strength:.3f}_{image_proc.roundness:.3f}_{image_proc.smoothness}_"
    param_str += f"{image_proc.shadow_depth:.3f}_{image_proc.light_intensity:.3f}_{image_proc.ambient_light:.3f}_"
    param_str += f"{image_proc.surface_scale:.3f}_{image_proc.surface_complexity:.3f}_{image_proc.surface_seed}_"
    param_str += f"{image_proc.wetness:.3f}_{image_proc.specular_intensity:.3f}_{image_proc.specular_power:.3f}_"
    param_str += f"{image_proc.light_direction[0]:.3f}_{image_proc.light_direction[1]:.3f}_{image_proc.light_direction[2]:.3f}"
    
    # Create a hash of the parameter string
    return hashlib.md5(param_str.encode()).hexdigest()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate pairs of Voronoi pattern images")
    parser.add_argument("--output_dir", type=str, default="voronoi_pairs", 
                        help="Directory to save generated image pairs")
    parser.add_argument("--num_images", type=int, default=10,
                        help="Number of image pairs to generate")
    parser.add_argument("--width", type=int, default=800,
                        help="Width of generated images")
    parser.add_argument("--height", type=int, default=600,
                        help="Height of generated images")
    parser.add_argument("--min_points", type=int, default=20,
                        help="Minimum number of points in Voronoi diagram")
    parser.add_argument("--max_points", type=int, default=100,
                        help="Maximum number of points in Voronoi diagram")
    parser.add_argument("--bulge_strength", type=float, default=0.5,
                        help="Strength of the 3D bulge effect")
    parser.add_argument("--wetness", type=float, default=0.7,
                        help="Wetness level for shiny surface effect")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to JSON configuration file with additional parameters")
    parser.add_argument("--randomize", action="store_true",
                        help="Randomize parameters for each image within allowed ranges")
    
    args = parser.parse_args()
    
    # Initialize configuration with command line arguments
    config = {
        'output_dir': args.output_dir,
        'num_images': args.num_images,
        'width': args.width,
        'height': args.height,
        'min_points': args.min_points,
        'max_points': args.max_points,
        'bulge_strength': args.bulge_strength,
        'wetness': args.wetness,
        'randomize_each_image': args.randomize
    }
    
    # If config file is provided, load additional parameters
    if args.config:
        import json
        try:
            with open(args.config, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    # Generate the image pairs
    generate_image_pairs(config, args.output_dir) 