import bpy

from .register_class import _get_cls, operator


class CLG_OT_make_sample(bpy.types.Operator):
    """サンプル作成"""

    bl_idname = "object.make_sample"
    bl_label = "Make Sample"
    bl_description = "Make sample."

    def execute(self, context):
        return {"FINISHED"}


class CLG_OT_make_grid(bpy.types.Operator):
    """格子作成"""

    bl_idname = "object.make_grid"
    bl_label = "Make Grid"
    bl_description = "Make grid."

    x: bpy.props.IntProperty() = bpy.props.IntProperty(default=10)  # type: ignore
    y: bpy.props.IntProperty() = bpy.props.IntProperty(default=10)  # type: ignore

    def execute(self, context):
        return {"FINISHED"}


class CLG_OT_make_anim(bpy.types.Operator):
    """アニメーション作成"""

    bl_idname = "object.make_anim"
    bl_label = "Make Anim"
    bl_description = "make animation."

    ncycle: bpy.props.IntProperty() = bpy.props.IntProperty(default=10)  # type: ignore
    unit: bpy.props.IntProperty() = bpy.props.IntProperty(default=5)  # type: ignore

    def execute(self, context):
        bpy.ops.screen.animation_play()
        return {"FINISHED"}


class CLG_PT_bit(bpy.types.Panel):
    bl_label = "LifeGame"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context):
        operator(self.layout, CLG_OT_make_sample)
        self.layout.separator()
        self.layout.prop(context.scene, "x", text="X")
        self.layout.prop(context.scene, "y", text="Y")
        prop = operator(self.layout, CLG_OT_make_grid)
        prop.x = context.scene.x
        prop.y = context.scene.y
        self.layout.separator()
        self.layout.prop(context.scene, "ncycle", text="NCycle")
        self.layout.prop(context.scene, "unit", text="Unit")
        prop = operator(self.layout, CLG_OT_make_anim)
        prop.ncycle = context.scene.ncycle
        prop.unit = context.scene.unit


# __init__.pyで使用
ui_classes = _get_cls(__name__)
