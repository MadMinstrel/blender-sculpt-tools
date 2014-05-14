import bpy
# import mathutils
import bmesh
from . import helper, booleanOps

class GreaseTrim(bpy.types.Operator):
    """Cuts the selected object along the grease pencil stroke"""
    bl_idname = "boolean.grease_trim"
    bl_label = "Grease Cut"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod 
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH'  and 0<len(bpy.context.selected_objects)<=2

    def execute(self, context):
        objBBDiagonal = helper.objDiagonal(context.active_object)*2
        # objBBDiagonal = objBBDiagonal*2
        subdivisions = 32

        if len(bpy.context.selected_objects)==1:
            try:
                mesh = bpy.context.active_object
                bpy.ops.gpencil.convert(type='POLY', timing_mode='LINEAR', use_timing_data=False)
                context.active_object.grease_pencil.clear()
                mesh = bpy.context.active_object
                if mesh == bpy.context.selected_objects[0]:
                    ruler = bpy.context.selected_objects[1]
                else: 
                    ruler = bpy.context.selected_objects[0]
                bpy.context.scene.objects.active = ruler
                bpy.ops.object.convert(target='MESH')
                
                rulerDiagonal = helper.objDiagonal(ruler)
                verts = []
                
                bm = bmesh.new()
                bm.from_mesh(ruler.data)
                
                for v in bm.verts:
                    if len(v.link_edges) == 1:
                        v.select = True
                        verts.append(v)
                dist = verts[0].co - verts[1].co
                if dist.length < rulerDiagonal/10:
                    bm.edges.new(verts)
                
                bm.to_mesh(ruler.data)
                
            except:
                self.report({'WARNING'}, "Draw a line with grease pencil first")
                return {'FINISHED'}
        elif len(bpy.context.selected_objects)==2:
            mesh = bpy.context.active_object
            
            if mesh == bpy.context.selected_objects[0]:
                ruler = bpy.context.selected_objects[1]
            else: 
                ruler = bpy.context.selected_objects[0]
            
            if ruler.type == 'MESH' and len(ruler.data.polygons)>0:
                bpy.context.scene.objects.active = ruler
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_mode(type="EDGE")
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.region_to_loop()
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.delete(type='EDGE')
                bpy.ops.object.mode_set(mode='OBJECT')
            elif ruler.type == 'CURVE':
                bpy.context.scene.objects.active = ruler
                bpy.ops.object.convert(target='MESH')
            


        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                viewZAxis = tuple([z * objBBDiagonal for z in area.spaces[0].region_3d.view_matrix[2][0:3]])
                negViewZAxis = tuple([z * (-2*objBBDiagonal*(1/subdivisions)) for z in area.spaces[0].region_3d.view_matrix[2][0:3]])
                break
        
        bpy.context.scene.objects.active = ruler

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.transform.translate(value = viewZAxis)
        for i in range(0, subdivisions):
            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":negViewZAxis})
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = mesh
        bpy.ops.boolean.separate()
    
        return {'FINISHED'}

class PurgeAllPencils(bpy.types.Operator):
    """Removes all Grease Pencil Layers"""
    bl_idname = "boolean.purge_pencils"
    bl_label = "Clears all grease pencil user data in the scene"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if not context.scene.grease_pencil == None:
            context.scene.grease_pencil.clear()
        for obj in context.scene.objects:
            if not context.scene.objects[obj.name].grease_pencil == None:
                context.scene.objects[obj.name].grease_pencil.clear() 
        return {'FINISHED'}   