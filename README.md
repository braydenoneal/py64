# Py64

A game engine loosely based on the Nintendo 64 using [moderngl](https://github.com/moderngl/moderngl) and [pygame](https://github.com/pygame/pygame).

Also developing [n64-blender](https://github.com/braydenoneal/n64-blender) to make and export a custom model format for the engine.

## Todo

- [x] Merge collision
- [x] Separate player and camera positions
- [x] Toggleable free-cam mode
- [ ] Re-implement decoupling frame-rate from physics rate
- [ ] Fog
- [ ] Order-independent transparency
- [ ] Horizontal blur
- [ ] Anti-aliasing
- [ ] Animations
- [ ] Text display

## Issues

- [ ] Collision is messed up on the back side of two-sided faces

## Model Exporter Todo

- [x] Merge vertex color and alpha attributes
- [;] Second textures
- [ ] Create an extensive test scene
- [ ] Animations

## Model Exporter Issues

- [ ] Exporter missing some faces on wall_bottom_half for some reason
- [ ] Exporter texture names sometimes have .001 at the end
    - Maybe use texture.filepath instead, but test for platform-specific forward-slash and backslash differences
- [ ] Blender linked-libraries are either relative or absolute (neither really works when the file is moved)
    - Maybe find a way to get the absolute Blender addon path machine and platform specific
        - https://blender.stackexchange.com/questions/20850/how-to-automatically-get-a-add-on-folders-path-regardless-of-os
    - Maybe force packed library if that doesn't work
- [ ] Investigate rendering discrepancies between Blender and the engine
    - For example, translucency, vertex colors, filtering, etc. appear slightly differently
