import bpy

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
    
def objDiagonal(obj):
    return ((obj.dimensions[0]**2)+(obj.dimensions[1]**2)+(obj.dimensions[2]**2))**0.5
    
def objDelete(obj):
    rem = obj
    remname = rem.data.name
    bpy.data.scenes[bpy.context.scene.name].objects.unlink(rem)
    bpy.data.objects.remove(rem)
    # remove mesh to prevent memory being cluttered up with hundreds of high-poly objects
    bpy.data.meshes.remove(bpy.data.meshes[remname])