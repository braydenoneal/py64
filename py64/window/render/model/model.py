import json
from typing import Any

import moderngl
from moderngl import Context, Program
from pyglm.glm import vec3, mat4x4

from py64.window.render.model.animation.animation import Animation
from py64.window.render.model.material.material import Material


class Model:
    def __init__(self, ctx: Context, program: Program, path: str, scale: vec3 = vec3(1), render_armature: bool = False):
        self.ctx = ctx
        self.program = program
        self.render_armature = render_armature

        self.model_dict: dict[str, Any] = {}

        with open(path) as file:
            self.model_dict = json.load(file)

        self.materials: list[Material] = []
        self.transparent_materials: list[Material] = []

        for material_dict in self.model_dict['materials'].values():
            material = Material(ctx, self.program, material_dict, self.model_dict['bones'], scale)

            if 'transparency' in material_dict:
                self.transparent_materials.append(material)
            else:
                self.materials.append(material)

        self.animation: Animation | None = None
        self.empty_bones = b''.join(mat4x4(1).to_bytes() for _ in range(100))

        if self.model_dict['bones'] != {}:
            self.animation = Animation(self.ctx, self.model_dict['bones'], scale)

    def set_uniforms(self, camera_matrix: mat4x4):
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)

        self.program['light'].write(vec3(-0.1, 0.55, 0.35))
        self.program['camera'].write(camera_matrix)

        if self.animation is not None:
            self.program['animate'] = True
            self.program['bones'].write(self.animation.bone_matrices_bytes)
        else:
            self.program['animate'] = False
            self.program['bones'].write(self.empty_bones)

    def step_animation(self):
        if self.animation is not None:
            self.animation.step()

    def render(self, camera_matrix: mat4x4):
        self.set_uniforms(camera_matrix)

        for material in self.materials:
            material.render()

        if self.animation is not None and self.render_armature:
            self.ctx.disable(moderngl.DEPTH_TEST)
            self.animation.render_armature(camera_matrix)
            self.ctx.enable(moderngl.DEPTH_TEST)

    def render_transparent(self, camera_matrix: mat4x4):
        self.set_uniforms(camera_matrix)

        for material in self.transparent_materials:
            material.render()
