# coding=UTF-8

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# last update: 2021/08/10


bl_info = {
    "name" : "Mesh Dismember",
    "author" : "Sai Ling",
    "description": "cut mesh for rig substitute",
    "version": (0, 0, 1),
    "blender" : (2, 90, 0),
    "location": "View3D > Sidebar",
    "warning" : "",
    "wiki_url": "https://github.com/Sai-BlenderAddons/mesh_dismember",
    "category" : "Generic"
}

import os
import bpy

class OBJECT_PT_mesh_dismember(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_label = "Mesh Dismember"
    # bl_options = {"DEFAULT_CLOSED"}   
        
    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene, "dismember_target")
        row = layout.row()
        row.prop(context.scene, "dismember_cutter")
        row = layout.row()
        row.operator('object.mesh_dismember')
        #layout.label('Mesh Tools')

class OBJECT_OT_mesh_dismember(bpy.types.Operator):
    bl_idname = "object.mesh_dismember"
    bl_label = "Dismember"
    bl_description = "Dismember mesh"

    def execute(self, context):
        [obj.select_set(False) for obj in bpy.data.objects]
        result_collection = get_collection('dismember result')
        target = context.scene.dismember_target
        cutter = context.scene.dismember_cutter
        [obj.select_set(True) for obj in cutter.objects]
        bpy.ops.object.duplicate()
        [result_collection.objects.link(obj) for obj in context.selected_objects]
        [cutter.objects.unlink(obj) for obj in context.selected_objects]
        dismember_mesh(result_collection.objects, target)
        target.hide_set(True)
        context.view_layer.layer_collection.children.get(cutter.name).hide_viewport = True
        return {'FINISHED'}

def get_collection(name: str):
    if bpy.data.collections.get(name) is None: 
        bpy.data.collections.new(name)
    
    reslut_collection = bpy.data.collections[name]
    if reslut_collection not in bpy.context.scene.collection.children_recursive:
        bpy.context.scene.collection.children.link(reslut_collection) 

    return bpy.data.collections[name]
    
def dismember_mesh(cutters: list, target: bpy.types.Mesh):
    for obj in cutters:
        modifier = obj.modifiers.new("Remesh", 'REMESH')
        modifier.mode = 'SHARP'
        modifier.octree_depth = 4
        modifier = obj.modifiers.new("boolean", 'BOOLEAN')
        modifier.operation = 'INTERSECT'
        modifier.solver = 'FAST'
        modifier.object = target
        # modifier.object = bpy.data.objects[target_name]
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.convert(target='MESH')

classes = (
    OBJECT_PT_mesh_dismember,
    OBJECT_OT_mesh_dismember,
)

def register():
    bpy.types.Scene.dismember_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.dismember_cutter = bpy.props.PointerProperty(type=bpy.types.Collection)
    
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.dismember_target
    del bpy.types.Scene.dismember_cutter
        
if __name__ == '__main__':
    register()
