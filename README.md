# Voronoi Pattern Generator

This tool generates Voronoi pattern images with 3D effects for various applications like textures, backgrounds, or art.

## Features

- Generate multiple image pairs (original Voronoi + 3D effect) in a single batch
- Configurable parameters via command line or config file
- Randomized point distribution and count for each image
- Customizable 3D effect parameters including bulge strength, wetness, and lighting
- Parameter range configuration UI for batch generation with randomized settings

## Generating Images

This toolkit provides multiple ways to generate Voronoi pattern images:

### 1. Command Line Generation

Generate a batch of images from the command line:

```bash
python generate_voronoi_pairs.py --output_dir=my_patterns --num_images=20 --width=1024 --height=768
```

#### Basic Command Line Options:
- `--output_dir`: Directory to save generated images (default: "voronoi_pairs")
- `--num_images`: Number of image pairs to generate (default: 10)
- `--width`/`--height`: Image dimensions (default: 800x600)
- `--min_points`/`--max_points`: Range for randomized point count (default: 20-100)
- `--bulge_strength`: 3D effect strength (default: 0.5)
- `--wetness`: Reflectivity of surface (default: 0.7)
- `--config`: Path to JSON configuration file for advanced settings

### 2. Configuration File

For more control over all parameters, use a JSON configuration file:

```bash
python generate_voronoi_pairs.py --config=my_config.json
```

Example configuration (see `voronoi_config_template.json` for a complete template):

```json
{
  "width": 800,
  "height": 600,
  "num_images": 10,
  "min_points": 20,
  "max_points": 100,
  "edge_thickness": 1,
  "show_points": false,
  
  "bulge_strength": 0.5,
  "roundness": 2.0,
  "smoothness": 15,
  "shadow_depth": 0.7,
  "light_intensity": 1.2,
  "ambient_light": 0.3,
  
  "surface_enabled": true,
  "surface_scale": 0.3,
  "surface_complexity": 2.0,
  
  "wetness": 0.7,
  "specular_intensity": 1.0,
  "specular_power": 30.0,
  "light_direction": [0.5, 0.5, 1.0]
}
```

### 3. Range Generator UI

For generating multiple images with randomized parameters within specified ranges:

```bash
python voronoi_range_generator_ui.py
```

This launches a graphical interface with three tabs:
- **Basic Settings**: Configure image size, point counts, and basic 3D effect parameters
- **Advanced Effects**: Configure lighting, surface effects, and wet/reflective properties
- **Generation**: Set number of images and output directory, save/load configurations

## Parameter Recommendations

### For Subtle 3D Effects
```json
{
  "bulge_strength": 0.3,
  "roundness": 3.0,
  "smoothness": 21,
  "shadow_depth": 0.5,
  "light_intensity": 1.0,
  "ambient_light": 0.4,
  "surface_scale": 0.2,
  "wetness": 0.4
}
```

### For Dramatic 3D Effects
```json
{
  "bulge_strength": 0.8,
  "roundness": 1.5,
  "smoothness": 11,
  "shadow_depth": 0.9,
  "light_intensity": 1.5,
  "ambient_light": 0.2,
  "surface_scale": 0.5,
  "wetness": 0.9
}
```

### For Organic/Natural Look
```json
{
  "point_distribution": "random",
  "min_points": 30,
  "max_points": 80,
  "surface_complexity": 3.0,
  "light_direction": [0.3, 0.7, 1.0]
}
```

### For Geometric/Regular Look
```json
{
  "point_distribution": "grid",
  "min_points": 50,
  "max_points": 150,
  "edge_thickness": 2,
  "surface_complexity": 1.5,
  "light_direction": [0.5, 0.5, 1.0]
}
```

## Parameter Descriptions

### Basic Parameters
- **Width/Height**: Image dimensions in pixels
- **Min/Max Points**: Range for number of Voronoi points (cells)
- **Point Distribution**: "random" or "grid" placement of seed points
- **Edge Thickness**: Thickness of Voronoi cell borders
- **Show Points**: Whether to display seed points

### 3D Effect Parameters
- **Bulge Strength** (0.1-1.0): How pronounced the 3D effect appears
  - Lower values (0.1-0.3): Subtle, gentle bulges
  - Higher values (0.7-1.0): Dramatic, pronounced bulges
  
- **Roundness** (0.5-5.0): Controls the shape of the bulges
  - Lower values (0.5-1.5): More peaked, sharp bulges
  - Higher values (3.0-5.0): More rounded, dome-like bulges
  
- **Smoothness** (5-31, odd numbers only): Controls transition smoothness
  - Lower values (5-11): More detailed, sharper transitions
  - Higher values (21-31): Smoother, more blended transitions
  
- **Shadow Depth** (0.1-1.0): Intensity of shadows in the valleys
  - Lower values (0.1-0.4): Subtle shadows, lower contrast
  - Higher values (0.7-1.0): Deep shadows, high contrast

### Lighting Parameters
- **Light Intensity** (0.1-2.0): Brightness of the directional light
- **Ambient Light** (0.0-1.0): Base level of illumination
- **Light Direction**: [X, Y, Z] coordinates of light source

### Surface Parameters
- **Surface Enabled**: Toggle uneven surface effect on/off
- **Surface Scale** (0.0-1.0): How pronounced the surface undulations are
- **Surface Complexity** (1.0-5.0): How complex the surface pattern is
- **Surface Seed**: Random seed for reproducible surface generation

### Wet Surface Parameters
- **Wetness** (0.0-1.0): How wet/shiny the surface appears
- **Specular Intensity** (0.0-2.0): Brightness of specular highlights
- **Specular Power** (1.0-100.0): Size of specular highlights (higher = smaller)

## Example Usage

### Generate 10 Dramatic 3D Effect Images
```bash
python generate_voronoi_pairs.py --bulge_strength=0.8 --shadow_depth=0.9 --wetness=0.9 --output_dir=dramatic_effects
```

### Generate 50 Images with Randomized Parameters
```bash
python voronoi_range_generator_ui.py
# Then in the UI:
# 1. Set parameter ranges in "Basic Settings" and "Advanced Effects" tabs
# 2. Set num_images=50 in the "Generation" tab
# 3. Click "Generate Patterns"
```

### Generate Images for ML Training Data
```bash
# Create a configuration file with desired parameter ranges
# Then run:
python generate_voronoi_pairs.py --config=training_data_config.json --num_images=1000 --output_dir=training_data
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Interactive UI

Run the interactive editor:
```
python voronoi_generator_simple.py
```

Or use the provided shell script:
```
./run.sh
```

The interactive UI features:
- A scrollable settings panel with all customization options
- Real-time preview of both original pattern and 3D effect
- Controls grouped by category for easy access
- Save/load functionality for both images and configurations

## Available Tools

This repository includes several tools for working with Voronoi patterns:

1. **Interactive Editor** (`voronoi_generator_simple.py`): Create and edit Voronoi patterns interactively
2. **Batch Generator** (`generate_voronoi_pairs.py`): Generate multiple patterns with fixed parameters
3. **Range Generator UI** (`voronoi_range_generator_ui.py`): Generate patterns with randomized parameters within specified ranges
4. **Debug Tool** (`debug_3d_effect.py`): Visualize the steps of 3D effect generation

## Algorithm Details

The Voronoi diagram generator creates patterns through these steps:

1. Generate seed points based on selected distribution (random or grid)
2. Compute the Voronoi tessellation using SciPy
3. Render the diagram with OpenCV
4. Apply 3D bulge effect through height map generation
5. Apply uneven surface effect with Perlin-like noise (if enabled)
6. Apply wet surface effect with specular highlights (if enabled)
7. Apply final contrast and lighting adjustments
8. Save the resulting images as pairs (original + 3D effect)

## 3D Bulge Effect

The 3D bulge effect creates a visual representation where:
- White spaces in the Voronoi diagram appear as protruding rounded bulges
- The shadows between bulges create the appearance of valleys/ridges
- The entire pattern can be placed on an uneven, gently curving surface
- The surface can appear wet/shiny with realistic reflections

This is achieved through the following steps:
1. Create a height map from the Voronoi diagram using distance transform
2. Apply power function to create rounded bulges
3. Generate an uneven base surface using Perlin-like noise (optional)
4. Combine the bulge height map with the uneven surface
5. Compute a normal map from the combined height map using Sobel operators
6. Apply diffuse lighting calculations with shadow effects
7. Calculate specular highlights using the Blinn-Phong reflection model
8. Combine diffuse and specular components for a realistic wet appearance
9. Enhance contrast for better visual appearance

### Customizable 3D Effect Parameters

- **Bulge Strength**: Controls how high the bulges appear
- **Roundness**: Controls how rounded the bulges appear (higher values = more rounded)
- **Smoothness**: Controls how smooth the transitions between bulges are
- **Shadow Depth**: Controls how deep the shadows appear in the valleys
- **Light Intensity**: Controls the intensity of the directional light
- **Ambient Light**: Controls the base level of illumination

### Uneven Surface Parameters

- **Enable Uneven Surface**: Toggle the uneven surface effect on/off
- **Surface Scale**: Controls how pronounced the surface undulations are
- **Surface Complexity**: Controls how complex the surface pattern is (higher = more detailed)
- **Surface Seed**: Random seed for reproducible surface generation
- **Randomize Seed**: Generate a new random surface pattern

### Wet Surface Parameters

- **Wetness**: Controls how wet/shiny the surface appears
- **Reflection Intensity**: Controls the brightness of specular highlights
- **Reflection Size**: Controls the size of specular highlights (higher values = smaller, more focused reflections)
- **Light Direction**: Controls the direction of the light source (X, Y, Z coordinates)
- **Reflection Color**: Controls the color of the specular highlights 