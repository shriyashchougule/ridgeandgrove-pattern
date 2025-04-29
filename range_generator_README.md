# Voronoi Range Generator UI

This utility provides a graphical user interface for generating multiple Voronoi patterns with randomized parameters within specified ranges.

## Features

- Set minimum and maximum values for all Voronoi pattern parameters
- Generate multiple images with random values selected from your defined ranges
- Organized interface with tabs for basic, advanced, and generation settings
- Save and load parameter range configurations
- Uses the batch generator script in the background

## Usage

### Running the UI

```bash
python voronoi_range_generator_ui.py
```

### Setting Parameter Ranges

1. Use the **Basic Settings** tab to configure:
   - Image size ranges (width and height)
   - Point count ranges (min and max points)
   - Edge thickness range
   - Basic 3D effect parameters

2. Use the **Advanced Effects** tab to configure:
   - Lighting parameter ranges
   - Uneven surface settings
   - Wet surface effects
   - Light direction ranges

3. Use the **Generation** tab to configure:
   - Number of images to generate
   - Output directory
   - Save/load configuration files

### Generating Images

1. Set all your desired parameter ranges across the tabs
2. Optionally save your configuration for future use
3. Click the **Generate Patterns** button at the bottom of the UI
4. The script will create the specified number of images with randomly chosen parameters within your ranges

## How It Works

For each image generation:
1. The UI randomly selects a value within each parameter's specified range
2. These random values are compiled into a single configuration
3. The configuration is passed to the `generate_voronoi_pairs.py` script
4. The script generates the Voronoi images with the randomly selected parameters
5. Original and 3D effect image pairs are saved to the output directory

## Parameter Ranges

### Basic Parameters
- **Width/Height**: Image dimensions (pixels)
- **Min/Max Points**: Range for the number of Voronoi points
- **Edge Thickness**: Thickness of Voronoi cell borders

### 3D Effect Parameters
- **Bulge Strength**: How pronounced the 3D effect appears
- **Roundness**: Controls shape of the bulges
- **Smoothness**: Controls transition smoothness (must be odd numbers)
- **Shadow Depth**: Intensity of shadows in the valleys

### Advanced Parameters
- **Lighting**: Light intensity and ambient light levels
- **Surface Effects**: Scale and complexity of the uneven surface
- **Wetness**: Controls reflectivity and specular highlights
- **Light Direction**: Direction of the light source

## Examples

By setting wide parameter ranges, you can generate diverse sets of Voronoi patterns with significantly different appearances, useful for:
- Creating texture libraries
- Generating training data for machine learning
- Exploring different visual aesthetics
- Creating art collections with consistent style but varied details