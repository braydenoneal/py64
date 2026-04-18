# Py64

A game engine loosely based on the Nintendo 64 using [moderngl](https://github.com/moderngl/moderngl) and [pygame](https://github.com/pygame/pygame).

Also developing [n64-blender](https://github.com/braydenoneal/n64-blender) to make and export a custom model format for the engine.

## Todo

- [x] Merge collision
- [x] Separate player and camera positions
- [x] Toggleable free-cam mode
- [x] Clean up / refactor files
- [x] Refactor / rewrite collision code
- [x] Text display
- [x] Order-independent transparency
- [x] Animations
- [x] Collision debug rendering (transparent ellipsoid model)
- [x] Fog
- [;] Gouraud shading
    - [x] Vertex normals
    - [ ] Specular highlights
- [ ] Data driven animation state transition graph
- [ ] Skybox
- [ ] Horizontal blur
- [ ] Anti-aliasing
- [ ] Texture scroll
- [ ] Texture animations
- [ ] Revisit decoupling frame-rate from physics rate
- [ ] UI framework (maybe something like HTML with tailwind-like class name styling?)
- [ ] Level loading and unloading
- [ ] Sound
- [ ] Lights
- [ ] Normal maps, diffuse maps, etc.
- [ ] Ambient occlusion
- [ ] Bloom
- [ ] Shadows
- [ ] God rays
- [ ] Dynamic lighting
- [ ] Volumetric fog/lighting
- [ ] Depth of field
- [ ] PBR?
- [ ] Environment maps
- [ ] Reflection
- [ ] Emission

## Issues

- [x] Collision is messed up on the back side of two-sided faces

## Model Exporter Todo

- [x] Merge vertex color and alpha attributes
- [x] Animations
- [;] Second textures [separate uv maps]
- [ ] Create an extensive test scene
- [ ] Texture scroll
- [ ] Texture animations
- [ ] Gouraud shading
- [ ] Defining collision faces and other level-editing features

## Model Exporter Issues

- [ ] Hex colors are gamma corrected to an incorrect RGB value
- [ ] Exporter texture names sometimes have .001 at the end
    - Maybe use texture.filepath instead, but test for platform-specific forward-slash and backslash differences
- [ ] Blender linked-libraries are either relative or absolute (neither really works when the file is moved)
    - Maybe find a way to get the absolute Blender addon path machine and platform specific
        - https://blender.stackexchange.com/questions/20850/how-to-automatically-get-a-add-on-folders-path-regardless-of-os
    - Maybe force packed library if that doesn't work
- [ ] Investigate rendering discrepancies between Blender and the engine
    - For example, translucency, vertex colors, filtering, etc. appear slightly differently

## Coordinate Reference

- OpenGL
    - 3D space
        - X: -left, +right
        - Y: -down, +up
        - Z: -towards camera, +away from camera
        - Origin: 0, 0, 0
    - Screen space
        - X: -left, +right
        - Y: -down, +up
        - Center: 0, 0
        - Bottom left: -1, -1
        - Top right: 1, 1
    - UV coordinates
        - X: -left, +right
        - Y: -up, +down
        - Top left: 0, 0
        - Bottom right: 1, 1
- Pillow
    - X: -left, +right
    - Y: -up, +down
    - Top left: 0, 0
    - Bottom right: 1, 1
- Blender
    - 3D space
        - X: -left, +right
        - Y: -towards camera, +away from camera
        - Z: -down, +up
        - Origin: 0, 0, 0
    - UV coordinates
        - X: -left, +right
        - Y: -down, +up
        - Bottom left: 0, 0
        - Top right: 1, 1
