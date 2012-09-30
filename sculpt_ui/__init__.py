bl_info = {
    "name": "Sculpt Tools UI",
    "author": "Nicholas Bishop, Roberto Roch, Bartosz Styperek, Piotr Adamowicz",
    "version": (0, 2),
    "blender": (2, 5, 5),
    "location": "Sculpt>Toool shelf",
    "description": "Simple UI for Boolean and Remesh operators",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Sculpting"}


import bpy
from bpy.props import *

# Define an RNA prop for every object
bpy.types.Object.remeshDepthInt = IntProperty(
    name="Depth", 
    min = 2, max = 10,
    default = 4)
    
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
    '''Toggles sculpt mode X symmetry'''
    bl_idname = "boolean.mod_apply"
    bl_label = "Apply Modifiers"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):

        return {'FINISHED'}

class ModApplyOperator(bpy.types.Operator):
    '''Applies all modifiers for all selected objects. Also works in sculpt or edit mode.'''
    bl_idname = "boolean.mod_apply"
    bl_label = "Apply Modifiers"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        print( "hello")
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

#                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=md.name)

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

class RemeshOperator(bpy.types.Operator):
    '''Remesh an object at the given octree depth'''
    bl_idname = "sculpt.remesh"
    bl_label = "Sculpt Remesh"
    depth = bpy.props.IntProperty()
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        # add a smooth remesh modifier
        ob = context.active_object
        dyntopoOn = False
        #try for whether we're running a dyntopo branch
        try:
            if context.sculpt_object.use_dynamic_topology_sculpting:
                dyntopoOn = True
                bpy.ops.sculpt.dynamic_topology_toggle()
        except:
            pass
            
        md = ob.modifiers.new('sculptremesh', 'REMESH')
        md.mode = 'SMOOTH'
        md.octree_depth = ob.remeshDepthInt
        md.scale = .99
        md.remove_disconnected_pieces = False

        # apply the modifier
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sculptremesh")

        if dyntopoOn == True:
            bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}
        

class BooleanUnionOperator(bpy.types.Operator):
    '''Creates an union of the selected objects'''
    bl_idname = "boolean.union"
    bl_label = "Boolean Union"

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
        
class RemeshBooleanPanel(bpy.types.Panel):
    """UI panel for the Remesh and Boolean buttons"""
    bl_label = "Sculpt Tools"
    bl_idname = "OBJECT_PT_remesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row(align=True)
        row.alignment = 'EXPAND'

        try:
            RemeshDepth = obj.remeshDepthInt
        except:
            RemeshDepth = 0
        
        try:
            row.operator("sculpt.remesh", text='Remesh').depth = RemeshDepth
            row.prop(obj, 'remeshDepthInt')
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
        

def register():
    bpy.utils.register_module(__name__)
    
    #km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    #km.keymap_items.new('view3d.mode_menu', 'TAB', 'PRESS', key_modifier="Q")
    
#    km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
#    for kmi in km.keymap_items:
#        if kmi.idname == 'view3d.mode_menu':
#            km.keymap_items.remove(kmi)
#            break
    
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()