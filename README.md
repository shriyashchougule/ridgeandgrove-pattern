# Voronoi Pattern Generator

A tool for generating synthetic images using the Voronoi diagram approach with an optional 3D bulge effect.

## Features

- Generate Voronoi diagrams with customizable parameters
- Adjust number of seed points
- Choose between random and grid-based point distributions
- Option to show/hide seed points
- Apply 3D bulge effect to make white spaces appear as protruding rounded bulges
- Customize 3D effect parameters (bulge strength, roundness, smoothness, shadow depth, lighting)
- Save both original and 3D effect images

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```
python voronoi_generator_simple.py
```

Or use the provided shell script:
```
./run.sh
```

## Algorithm

The Voronoi diagram generator uses the following algorithm:

1. Generate seed points based on selected distribution (random or grid)
2. Compute the Voronoi tessellation using SciPy
3. Render the diagram with OpenCV
4. Apply 3D bulge effect processing (optional)
5. Display or save the resulting images

## 3D Bulge Effect

The 3D bulge effect creates a visual representation where:
- White spaces in the Voronoi diagram appear as protruding rounded bulges
- The shadows between bulges create the appearance of valleys/ridges

This is achieved through the following steps:
1. Create a height map from the Voronoi diagram using distance transform
2. Apply power function to create rounded bulges
3. Compute a normal map from the height map using Sobel operators
4. Apply lighting calculations with shadow effects to create a 3D appearance
5. Enhance contrast for better visual appearance

### Customizable 3D Effect Parameters

- **Bulge Strength**: Controls how high the bulges appear
- **Roundness**: Controls how rounded the bulges appear (higher values = more rounded)
- **Smoothness**: Controls how smooth the transitions between bulges are
- **Shadow Depth**: Controls how deep the shadows appear in the valleys
- **Light Intensity**: Controls the intensity of the directional light
- **Ambient Light**: Controls the base level of illumination 