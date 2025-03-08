# Voronoi Pattern Generator

A tool for generating synthetic images using the Voronoi diagram approach with an optional 3D bulge effect.

## Features

- Generate Voronoi diagrams with customizable parameters
- Adjust number of seed points
- Choose between random and grid-based point distributions
- Option to show/hide seed points
- Apply 3D bulge effect to make white spaces appear as protruding rounded bulges
- Create uneven, gently curving base surface for added realism
- Add wet/shiny surface effect with specular highlights and reflections
- Customize 3D effect parameters (bulge strength, roundness, smoothness, shadow depth, lighting)
- Customize uneven surface parameters (scale, complexity, randomization)
- Customize wet surface parameters (wetness, reflection intensity, light direction)
- Scrollable settings panel for easy access to all parameters
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

### User Interface

The application has a user-friendly interface with:
- A scrollable settings panel on the left with all customization options
- Two image display areas on the right (original and 3D effect)
- Controls grouped by category (Image Size, Points, Appearance, 3D Effect, Uneven Surface, Wet Surface)
- Use the mouse wheel to scroll through all available settings

## Algorithm

The Voronoi diagram generator uses the following algorithm:

1. Generate seed points based on selected distribution (random or grid)
2. Compute the Voronoi tessellation using SciPy
3. Render the diagram with OpenCV
4. Apply 3D bulge effect processing (optional)
5. Apply uneven surface effect (optional)
6. Apply wet surface effect with specular highlights (optional)
7. Display or save the resulting images

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