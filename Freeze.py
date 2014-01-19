import bpy
from . import helper

class BooleanFreezeOperator(bpy.types.Operator):
    '''Decimates the object temporarily for viewport performance'''
    bl_idname = "boolean.freeze"
    bl_label = "Boolean Freeze"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)==1

    def execute(self, context):
        
        if "Frozen" not in bpy.data.groups:
            bpy.data.groups.new("Frozen")
        
        ob = context.active_object
        obCopy = helper.objDuplicate(ob)
        md = ob.modifiers.new('BoolDecimate', 'DECIMATE')
        md.ratio = 0.1
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="BoolDecimate")
        ob.hide_render = True
        obCopy.select = True
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        obCopy.name = "Frozen_"+ob.name
        obCopy.hide = True
        obCopy.hide_select = True
        obCopy.select = False
        ob.select = True
        bpy.ops.object.group_link(group='Frozen')
        
        # for SelectedObject in bpy.context.selected_objects :
            # if SelectedObject != activeObj :

                # helper.objSelectFaces(activeObj, 'DESELECT')
                # helper.objSelectFaces(SelectedObject, 'SELECT')

                # bpy.context.scene.objects.active = activeObj

                # md = activeObj.modifiers.new('booleanunion', 'BOOLEAN')
                # md.operation = 'UNION'
                # md.object = SelectedObject       
                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="booleanunion")
                # bpy.data.scenes[0].objects.unlink(SelectedObject)
                # bpy.data.objects.remove(SelectedObject)
        
        return {'FINISHED'}
        
class BooleanUnfreezeOperator(bpy.types.Operator):
    '''Decimates the object temporarily for viewport performance'''
    bl_idname = "boolean.unfreeze"
    bl_label = "Boolean Unfreeze"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and len(bpy.context.selected_objects)==1

    def execute(self, context):
        
        
        ob = bpy.context.active_object
        
        for sceneObj in bpy.context.scene.objects:
            if sceneObj.parent == ob:
                frozen = sceneObj
        
        ob.data = bpy.context.scene.objects['Frozen_'+ob.name].data
        
        bpy.data.scenes[0].objects.unlink(frozen)
        bpy.data.objects.remove(frozen)
        
        ob.hide_render = False
        
        bpy.data.groups['Frozen'].objects.unlink(bpy.context.object)
        
        return {'FINISHED'}