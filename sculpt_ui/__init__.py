bl_info = {
    "name": "Sculpt Tools UI",
    "author": "Nicholas Bishop, Roberto Roch, Bartosz Styperek, Piotr Adamowicz",
    "version": (0, 2),
    "blender": (2, 5, 5),
    "location": "3d View > Tool shelf",
    "description": "Simple UI for Boolean and Remesh operators",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Sculpting"}


import bpy
from bpy.props import *


# helper function for face selection
def objSelectFaces(obj, mode):
    
    #store active object
    activeObj = bpy.context.active_object
    
    #store the mode of the active object
    oldMode = activeObj.mode
    
    #perform selection
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action=mode)
    
    #restore old active object and mode
    bpy.ops.object.mode_set(mode=oldMode)
    bpy.context.scene.objects.active = activeObj

#helper function to duplicate an object    
def objDuplicate(obj):

    activeObj = bpy.context.active_object
    oldMode = activeObj.mode    

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action = 'DESELECT')
    bpy.ops.object.select_pattern(pattern = obj.name)
    bpy.ops.object.duplicate()
    objCopy = bpy.context.selected_objects[0]

    bpy.context.scene.objects.active = activeObj
    bpy.ops.object.mode_set(mode=oldMode)
    return objCopy
    
    

#Debug test area
#class BooleanDebugOperator(bpy.types.Operator):
#    '''Debug'''
#    bl_idname = "boolean.debug"
#    bl_label = "Boolean Debug Op"
#
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None
#
#    def execute(self, context):
#        return {'FINISHED'}
#    



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
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=md.name)
            bpy.ops.object.mode_set(mode=oldMode)
        bpy.context.scene.objects.active = activeObj
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
    
class DyntopoUpdateOperator(bpy.types.Operator):
    '''Update Dynamic topology'''
    bl_idname = "sculpt.dyntopo_update"
    bl_label = "Dyntopo Update"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        ob = context.active_object
        #try for whether we're running a dyntopo branch
        try:
            if context.sculpt_object.use_dynamic_topology_sculpting:
                bpy.ops.sculpt.dynamic_topology_toggle()
                bpy.ops.sculpt.dynamic_topology_toggle()
        except:
            pass
        
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
        
        
    def execute(self, context):
        # add a smooth remesh modifier
        ob = context.active_object
        wm = context.window_manager
        oldMode = ob.mode
        
        #try for whether we're running a dyntopo branch
        dyntopoOn = False;
        try:
            if context.sculpt_object.use_dynamic_topology_sculpting:
                dyntopoOn = True
                bpy.ops.sculpt.dynamic_topology_toggle()
        except:
            pass
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        md = ob.modifiers.new('sculptremesh', 'REMESH')
        md.mode = 'SMOOTH'
        md.octree_depth = wm.remeshDepthInt
        md.scale = .99
        md.remove_disconnected_pieces = False

        # apply the modifier
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sculptremesh")
        
        bpy.ops.object.mode_set(mode=oldMode)
        
        if dyntopoOn == True:
            bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}
        

class BooleanUnionOperator(bpy.types.Operator):
    '''Creates an union of the selected objects'''
    bl_idname = "boolean.union"
    bl_label = "Boolean Union"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)>1

    def execute(self, context):
        # add a union boolean modifier
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
            if SelectedObject != activeObj :

                objSelectFaces(activeObj, 'DESELECT')
                objSelectFaces(SelectedObject, 'SELECT')

                bpy.context.scene.objects.active = activeObj

                md = activeObj.modifiers.new('booleanunion', 'BOOLEAN')
                md.operation = 'UNION'
                md.object = SelectedObject       
                # apply the modifier
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanunion")
                bpy.data.scenes[0].objects.unlink(SelectedObject)
                bpy.data.objects.remove(SelectedObject)
        
        return {'FINISHED'}

class BooleanDifferenceOperator(bpy.types.Operator):
    '''Subtracts the selection from the active object'''
    bl_idname = "boolean.difference"
    bl_label = "Boolean Difference"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)>1

    def execute(self, context):
        # add a difference boolean modifier
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
            if SelectedObject != activeObj :

                #deselect all the faces of the active object
                objSelectFaces(activeObj, 'DESELECT')

                #select all the faces of the selected object
                objSelectFaces(SelectedObject, 'SELECT')
                
                bpy.context.scene.objects.active = activeObj
                
                md = activeObj.modifiers.new('booleandifference', 'BOOLEAN')
                md.operation = 'DIFFERENCE'
                md.object = SelectedObject       
                # apply the modifier
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleandifference")
                bpy.data.scenes[0].objects.unlink(SelectedObject)
                bpy.data.objects.remove(SelectedObject)
        
        return {'FINISHED'}

class BooleanIntersectOperator(bpy.types.Operator):
    '''Creates an intersection of all the selected objects'''
    bl_idname = "boolean.intersect"
    bl_label = "Boolean intersect"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)>1

    def execute(self, context):
        # add a intersect boolean modifier
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
            if SelectedObject != activeObj :
                
                #deselect all the faces of the active object
                objSelectFaces(activeObj, 'DESELECT')

                #select all the faces of the selected object
                objSelectFaces(SelectedObject, 'SELECT')
                
                bpy.context.scene.objects.active = activeObj

                md = activeObj.modifiers.new('booleanintersect', 'BOOLEAN')
                md.operation = 'INTERSECT'
                md.object = SelectedObject       
                
                # apply the modifier
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanintersect")
                bpy.data.scenes[0].objects.unlink(SelectedObject)
                bpy.data.objects.remove(SelectedObject)
        
        return {'FINISHED'}

class BooleanCloneOperator(bpy.types.Operator):
    '''Clones the intersecting part of the mesh'''
    bl_idname = "boolean.clone"
    bl_label = "Boolean clone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)==2

    def execute(self, context):
        # add a intersect boolean modifier
        activeObj = context.active_object
        for SelectedObject in bpy.context.selected_objects :
            if SelectedObject != activeObj :
                
                #deselect all the faces of the active object
                objSelectFaces(activeObj, 'DESELECT')

                #select all the faces of the selected object
                objSelectFaces(SelectedObject, 'SELECT')

                md = SelectedObject.modifiers.new('booleanclone', 'BOOLEAN')
                md.operation = 'INTERSECT'
                md.object = activeObj       
                
                # apply the modifier
                bpy.context.scene.objects.active = SelectedObject
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanclone")
                
                #restore the active object
                bpy.context.scene.objects.active = activeObj
        
        return {'FINISHED'}

class BooleanSeparateOperator(bpy.types.Operator):
    '''Separates the active object along the intersection of the selected objects'''
    bl_idname = "boolean.separate"
    bl_label = "Boolean separation"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)==2

    def execute(self, context):
        # add a intersect boolean modifier
        activeObj = context.active_object
        Selection = bpy.context.selected_objects
        
        for SelectedObject in Selection :
            if SelectedObject != activeObj :
                
                #make a copy of the selected object
                SelectedObjCopy = objDuplicate(SelectedObject)
                
                #make a copy of the active object
                activeObjCopy = objDuplicate(activeObj)

                objSelectFaces(activeObjCopy, 'SELECT')
                objSelectFaces(SelectedObject, 'DESELECT')
                
                
                md = SelectedObject.modifiers.new('sepIntersect', 'BOOLEAN')
                md.operation = 'INTERSECT'
                md.object = activeObjCopy
                # apply the modifier 
                bpy.context.scene.objects.active = SelectedObject
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sepIntersect")
                
                objSelectFaces(SelectedObject, 'INVERT')
                
                #delete the copy of the active object
                bpy.data.scenes[0].objects.unlink(activeObjCopy)
                bpy.data.objects.remove(activeObjCopy)
        
        objSelectFaces(SelectedObjCopy, 'SELECT')
        objSelectFaces(activeObj, 'DESELECT')
   
        md2 = activeObj.modifiers.new('sepDifference', 'BOOLEAN')
        md2.operation = 'DIFFERENCE'
        md2.object = SelectedObjCopy
        
        #apply the second modifier
        bpy.context.scene.objects.active = SelectedObject
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sepDifference")
        
        #delete the copy of the selected object
        bpy.data.scenes[0].objects.unlink(SelectedObjCopy)
        bpy.data.objects.remove(SelectedObjCopy)
        
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
    
        
class RemeshBooleanPanel(bpy.types.Panel):
    """UI panel for the Remesh and Boolean buttons"""
    bl_label = "Sculpt Tools"
    bl_idname = "OBJECT_PT_remesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        wm = context.window_manager
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'

        try:
            row.operator("sculpt.remesh", text='Remesh')
            row.prop(wm, 'remeshDepthInt', text="Depth")
        except:
            pass

        row2 = layout.row(align=True)
        row2.alignment = 'EXPAND'
        row2.operator("boolean.union", text="Union")
        row2.operator("boolean.difference", text="Difference")
        row2.operator("boolean.intersect", text="Intersect")
        
        row3 = layout.row(align=True)
        row3.alignment = 'EXPAND'
        
        row3.operator("boolean.separate", text="Separate")
        row3.operator("boolean.clone", text="Clone")
        
        row4 = layout.row(align=True)
        row4.alignment = 'EXPAND'
        row4.operator("boolean.mod_apply", text="Apply Mods")
        row4.operator("boolean.mod_xmirror", text="X-Mirror")
        
        row5 = layout.row(align=True)
        row5.alignment = 'EXPAND'
        row5.operator("boolean.mesh_deform", text="Mesh Deform")
        
        row6 = layout.row(align=True)
        row6.alignment = 'EXPAND'
        row6.operator("boolean.double_sided_off", text="Double Sided Off")
        
class BooleanOpsMenu(bpy.types.Menu):
    bl_label = "Booleans"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator("boolean.union",
                        text="Union",
                        icon='ROTATECOLLECTION')
        layout.operator("boolean.difference",
                        text="Difference",
                        icon='ROTACTIVE')
        layout.operator("boolean.intersect",
                        text="Intersection",
                        icon='ROTATECENTER')


        layout.separator()
        layout.operator("boolean.separate",
                        text="Separate",
                        icon='ARROW_LEFTRIGHT')
        layout.operator("boolean.clone",
                        text="Clone",
                        icon='MOD_BOOLEAN')
        layout.separator()
        layout.operator("boolean.mod_apply",
                        text="Apply Modifiers",
                        icon='MODIFIER')
        layout.operator("boolean.mod_xmirror",
                        text="X-Mirror",
                        icon='MOD_MIRROR')
        layout.operator("boolean.mesh_deform",
                        text="Mesh Deform",
                        icon='MOD_MESHDEFORM')
        

def register():
    bpy.utils.register_module(__name__)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS', ctrl = True)
        kmi.properties.name = "BooleanOpsMenu"
        
        kmi = km.keymap_items.new('sculpt.dyntopo_update', 'U', 'PRESS')
        
        kmi = km.keymap_items.new('wm.context_toggle', 'X', 'PRESS')
        kmi.properties.data_path = "tool_settings.sculpt.use_symmetry_x"
        
        kmi = km.keymap_items.new('wm.context_toggle', 'E', 'PRESS', shift = True)
        kmi.properties.data_path = "tool_settings.sculpt.use_edge_collapse"
        
        kmi = km.keymap_items.new('sculpt.dynamic_topology_toggle', 'D', 'PRESS', shift = True)
        
    bpy.types.WindowManager.remeshDepthInt = IntProperty(
    min = 2, max = 10,
    default = 4)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps["3D View"]
        for kmi in km.keymap_items:
            if kmi.idname == 'wm.call_menu':
                if kmi.properties.name == "BooleanOpsMenu":
                    km.keymap_items.remove(kmi)
                    break
    try:
        del bpy.types.WindowManager.remeshDepthInt
    except:
        pass

if __name__ == "__main__":
    register()