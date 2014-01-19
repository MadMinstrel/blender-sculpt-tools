import bpy
from . import helper

class BooleanMeshDeformOperator(bpy.types.Operator):
    '''Binds a deforming mesh to the object'''
    bl_idname = "boolean.mesh_deform"
    bl_label = "Mesh deform"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)==2

    def execute(self, context):
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
            if SelectedObject != activeObj :
                md = activeObj.modifiers.new('mesh_deform', 'MESH_DEFORM')
                md.object = SelectedObject
                bpy.ops.object.meshdeform_bind(modifier="mesh_deform")
                bpy.context.scene.objects.active = SelectedObject
                SelectedObject.draw_type="WIRE"
                bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}
    
class ModApplyOperator(bpy.types.Operator):
    '''Applies all modifiers for all selected objects. Also works in sculpt or edit mode.'''
    bl_idname = "boolean.mod_apply"
    bl_label = "Apply Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
               
            bpy.context.scene.objects.active = SelectedObject
            oldMode = SelectedObject.mode    
            bpy.ops.object.mode_set(mode='OBJECT')
            for md in SelectedObject.modifiers :
                # apply the modifier
                try:
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=md.name)
                except:
                    pass
            bpy.ops.object.mode_set(mode=oldMode)
        bpy.context.scene.objects.active = activeObj
        return {'FINISHED'}
    
class RemeshOperator(bpy.types.Operator):
    '''Remesh an object at the given octree depth'''
    bl_idname = "sculpt.remesh"
    bl_label = "Sculpt Remesh"

    bl_options = {'REGISTER', 'UNDO'}
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def draw(self, context): 
        if context.active_object.mode != 'SCULPT':   
            wm = context.window_manager
            layout = self.layout
            layout.prop(wm, "remeshDepthInt", text="Depth")
            layout.prop(wm, "remeshSubdivisions", text="Subdivisions")
            layout.prop(wm, "remeshPreserveShape", text="Preserve Shape")
        
    def execute(self, context):
        # add a smooth remesh modifier
        ob = context.active_object
        wm = context.window_manager
        oldMode = ob.mode
        
        dyntopoOn = False;
        if context.active_object.mode == 'SCULPT': 
            if context.sculpt_object.use_dynamic_topology_sculpting:
                dyntopoOn = True
                bpy.ops.sculpt.dynamic_topology_toggle()
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        if wm.remeshPreserveShape:            
            obCopy = helper.objDuplicate(ob)
        
        md = ob.modifiers.new('sculptremesh', 'REMESH')
        md.mode = 'SMOOTH'
        md.octree_depth = wm.remeshDepthInt
        md.scale = .99
        md.use_remove_disconnected = False

        # apply the modifier
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sculptremesh")
        
        if wm.remeshSubdivisions > 0:
            mdsub = ob.modifiers.new('RemeshSubSurf', 'SUBSURF')
            mdsub.levels = wm.remeshSubdivisions
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="RemeshSubSurf")
        
        
        if wm.remeshPreserveShape:            
            md2 = ob.modifiers.new('RemeshShrinkwrap', 'SHRINKWRAP')
            md2.wrap_method = 'PROJECT'
            md2.use_negative_direction = True
            md2.use_positive_direction = True
            md2.target = obCopy
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="RemeshShrinkwrap")
            
            bpy.data.scenes[0].objects.unlink(obCopy)
            bpy.data.objects.remove(obCopy)
        
        bpy.ops.object.mode_set(mode=oldMode)
        
        if dyntopoOn == True:
            bpy.ops.sculpt.dynamic_topology_toggle()
        
        ob.select = True
        return {'FINISHED'}
        

        
class XMirrorOperator(bpy.types.Operator):
    '''Applies an X-axis mirror modifier to the selected object. If more objects are selected, they will be mirrored around the active object.'''
    bl_idname = "boolean.mod_xmirror"
    bl_label = "X-Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        activeObj = context.active_object
        if len(bpy.context.selected_objects)>1 :
            for SelectedObject in bpy.context.selected_objects :
                if SelectedObject != activeObj :
                    oldMode = SelectedObject.mode    

                    bpy.context.scene.objects.active = SelectedObject

                    bpy.ops.object.mode_set(mode='OBJECT')

                    md = SelectedObject.modifiers.new('xmirror', 'MIRROR')
                    md.mirror_object = activeObj



                    bpy.ops.object.mode_set(mode=oldMode)
                    bpy.context.scene.objects.active = activeObj
                    
        #if there's only one object selected, apply straight fo the active obj.
        if len(bpy.context.selected_objects)==1 :

            oldMode = activeObj.mode    

            bpy.ops.object.mode_set(mode='OBJECT')

            md = activeObj.modifiers.new('xmirror', 'MIRROR')

            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=md.name)

            bpy.ops.object.mode_set(mode=oldMode)
                
        return {'FINISHED'}

        
class DoubleSidedOffOperator(bpy.types.Operator):
    '''Turn off double sided for all objects'''
    bl_idname = "boolean.double_sided_off"
    bl_label = "Double Sided Off"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for mesh in bpy.data.meshes:
            mesh.show_double_sided = False
        return {'FINISHED'}

class SymmetrizeBoolMesh(bpy.types.Operator):
    """Copies one side of the mesh to the other along the chosen axis"""
    bl_idname = "boolean.grease_symm"
    bl_label = "Bool Mesh Symm Function"
    bl_options = {'REGISTER', 'UNDO'}
    
    symm_int = bpy.props.FloatProperty(name="Threshold", min = 0.0001, max = 1, default = .001)       
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'OBJECT' and context.active_object.type == 'MESH' or context.active_object is not None and context.active_object.mode == 'VERTEX_PAINT'

    def execute(self, context):
        func = bpy.ops
        wm = context.window_manager
        mode_curr = context.active_object.mode
        func.object.editmode_toggle()
        func.mesh.select_all(action='SELECT')
        func.mesh.symmetrize(direction = wm.bolsymm, threshold= self.symm_int)
        func.mesh.remove_doubles()
        func.object.editmode_toggle()
        if mode_curr == 'VERTEX_PAINT':
            func.object.mode_set(mode='VERTEX_PAINT')
        return {'FINISHED'}