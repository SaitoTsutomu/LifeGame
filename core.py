from itertools import product

import bmesh
import bpy
import numpy as np

from .register_class import _get_cls, operator


def add_geometry(obj: bpy.types.Object) -> None:
    """ライフゲーム用のジオメトリーノード作成

    :param obj: 対象オブジェクト
    """
    modifier = obj.modifiers.new("GeometryNodes", "NODES")
    node_tree = bpy.data.node_groups.new("Geometry Nodes", "GeometryNodeTree")
    modifier.node_group = node_tree
    modifier.node_group.is_modifier = True
    node_tree.interface.new_socket("Instances", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    node_tree.interface.new_socket("Instance", in_out="INPUT", socket_type="NodeSocketGeometry")
    ss = (
        "NodeGroupInput NodeGroupOutput GeometryNodeInstanceOnPoints "
        "GeometryNodeInputPosition ShaderNodeSeparateXYZ GeometryNodeMeshCube"
    ).split()
    nds = [node_tree.nodes.new(s) for s in ss]
    lks = [[0, 2], [2, 1], [3, 4], [24, 12], [5, 22], [2, 1]]
    for i, j in lks:
        node_tree.links.new(nds[i % 10].outputs[i // 10], nds[j % 10].inputs[j // 10])
    poss = [[80, 40], [410, 40], [250, 40], [-80, -99], [80, -99], [-240, -28]]
    for nd, pos in zip(nds, poss):
        nd.location = pos


def make_grid(context, nx, ny):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=nx - 1, y_subdivisions=ny - 1, size=1)
    bpy.ops.transform.resize(value=(nx - 1, ny - 1, 0))
    bpy.ops.object.transform_apply()
    add_geometry(context.object)
    bpy.ops.object.mode_set(mode="EDIT")


def make_anim(context, obj, nx, ny, n_cycle, unit):
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.data.animation_data_clear()
    vtx = np.array(obj.data.vertices).reshape(ny, nx)
    cells = np.zeros((ny + 2, nx + 2), bool)
    for y, x in product(range(ny), range(nx)):
        cells[y + 1, x + 1] = vtx[y, x].select
    ss = [slice(None, -2), slice(1, -1), slice(2, None)]  # 前中後用のスライス
    sc = ss[1]  # 中央用のスライス
    context.scene.frame_current = 1
    context.scene.frame_end = n_cycle * unit + 1
    for tm in range(n_cycle + 1):
        context.scene.frame_current = tm * unit + 1
        for y, x in product(range(ny), range(nx)):
            pre, nxt = vtx[y, x].co.z, cells[y + 1, x + 1] * 0.5
            if tm == 0 or (nxt != pre):
                if tm:
                    vtx[y, x].keyframe_insert("co", frame=tm * unit + 0.5, index=2)
                vtx[y, x].co.z = nxt
                vtx[y, x].keyframe_insert("co", frame=tm * unit + 1, index=2)
        cum = np.sum([cells[s1, s2] for s1 in ss for s2 in ss if s1 != sc or s2 != sc], 0)
        n2 = cum == 2
        n3 = cum == 3
        cells[sc, sc] = cells[sc, sc] & n2 | n3
    bpy.ops.screen.animation_play()


class CLG_OT_make_sample(bpy.types.Operator):
    """サンプル作成"""

    bl_idname = "object.make_sample"
    bl_label = "Make Sample"
    bl_description = "Make sample."

    def execute(self, context):
        sc = context.scene
        sc.nx, sc.ny, sc.n_cycle = 15, 15, 8
        make_grid(context, sc.nx, sc.ny)
        obj = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bpy.ops.mesh.select_all(action="DESELECT")
        for y, x in product(range(2), range(6)):
            bm.verts[x + 15 * y + 48].select = bm.verts[x + 15 * y + 156].select = True
            bm.verts[15 * x + y + 93].select = bm.verts[15 * x + y + 55].select = True
        # bm.free()
        bpy.ops.object.mode_set(mode="OBJECT")
        make_anim(context, obj, sc.nx, sc.ny, sc.n_cycle, sc.unit)
        return {"FINISHED"}


class CLG_OT_make_grid(bpy.types.Operator):
    """格子作成"""

    bl_idname = "object.make_grid"
    bl_label = "Make Grid"
    bl_description = "Make grid."

    nx: bpy.props.IntProperty() = bpy.props.IntProperty(default=10)
    ny: bpy.props.IntProperty() = bpy.props.IntProperty(default=10)

    def execute(self, context):
        make_grid(context, self.nx, self.ny)
        return {"FINISHED"}


class CLG_OT_make_anim(bpy.types.Operator):
    """アニメーション作成"""

    bl_idname = "object.make_anim"
    bl_label = "Make Anim"
    bl_description = "make animation."

    n_cycle: bpy.props.IntProperty() = bpy.props.IntProperty(default=10)
    unit: bpy.props.IntProperty() = bpy.props.IntProperty(default=5)

    def execute(self, context):
        nx, ny = context.scene.nx, context.scene.ny
        obj = context.object
        if not obj or obj.type != "MESH" or nx * ny != len(obj.data.vertices):
            self.report({"WARNING"}, "Select a object.")
            return {"CANCELLED"}
        make_anim(context, obj, nx, ny, self.n_cycle, self.unit)
        return {"FINISHED"}


class CLG_PT_bit(bpy.types.Panel):
    bl_label = "LifeGame"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Edit"

    def draw(self, context):
        operator(self.layout, CLG_OT_make_sample)
        self.layout.separator()
        self.layout.prop(context.scene, "nx", text="NX")
        self.layout.prop(context.scene, "ny", text="NY")
        prop = operator(self.layout, CLG_OT_make_grid)
        prop.nx = context.scene.nx
        prop.ny = context.scene.ny
        self.layout.separator()
        self.layout.prop(context.scene, "n_cycle", text="NCycle")
        self.layout.prop(context.scene, "unit", text="Unit")
        prop = operator(self.layout, CLG_OT_make_anim)
        prop.n_cycle = context.scene.n_cycle
        prop.unit = context.scene.unit


# __init__.pyで使用
ui_classes = _get_cls(__name__)
