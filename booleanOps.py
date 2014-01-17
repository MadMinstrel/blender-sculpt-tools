import bpy
from . import helper

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

                helper.objSelectFaces(activeObj, 'DESELECT')
                helper.objSelectFaces(SelectedObject, 'SELECT')

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
                helper.objSelectFaces(activeObj, 'DESELECT')

                #select all the faces of the selected object
                helper.objSelectFaces(SelectedObject, 'SELECT')
                
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
                helper.objSelectFaces(activeObj, 'DESELECT')

                #select all the faces of the selected object
                helper.objSelectFaces(SelectedObject, 'SELECT')
                
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
                helper.objSelectFaces(activeObj, 'DESELECT')

                #select all the faces of the selected object
                helper.objSelectFaces(SelectedObject, 'SELECT')

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
                SelectedObjCopy = helper.objDuplicate(SelectedObject)
                
                #make a copy of the active object
                activeObjCopy = helper.objDuplicate(activeObj)

                helper.objSelectFaces(activeObjCopy, 'SELECT')
                helper.objSelectFaces(SelectedObject, 'DESELECT')
                
                
                md = SelectedObject.modifiers.new('sepIntersect', 'BOOLEAN')
                md.operation = 'INTERSECT'
                md.object = activeObjCopy
                # apply the modifier 
                bpy.context.scene.objects.active = SelectedObject
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sepIntersect")
                
                helper.objSelectFaces(SelectedObject, 'INVERT')
                
                #delete the copy of the active object
                bpy.data.scenes[0].objects.unlink(activeObjCopy)
                bpy.data.objects.remove(activeObjCopy)
        
        helper.objSelectFaces(SelectedObjCopy, 'SELECT')
        helper.objSelectFaces(activeObj, 'DESELECT')
   
        md2 = activeObj.modifiers.new('sepDifference', 'BOOLEAN')
        md2.operation = 'DIFFERENCE'
        md2.object = SelectedObjCopy
        
        #apply the second modifier
        bpy.context.scene.objects.active = SelectedObject
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="sepDifference")
        
        #delete the copy of the selected object
        bpy.data.scenes[0].objects.unlink(SelectedObjCopy)
        bpy.data.objects.remove(SelectedObjCopy)
        
        bpy.context.active_object.select = True
        
        return {'FINISHED'}