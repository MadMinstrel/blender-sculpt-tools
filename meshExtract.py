import bpy

class MaskExtractOperator(bpy.types.Operator):
    """Extracts the masked area into a new mesh"""
    bl_idname = "boolean.mask_extract"
    bl_label = "Mask Extract"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'SCULPT'
    
    def draw(self, context): 
        wm = context.window_manager
        layout = self.layout
        layout.prop(wm, "extractStyleEnum", text="Style")
        layout.prop(wm, "extractDepthFloat", text="Depth")
        layout.prop(wm, "extractOffsetFloat", text="Offset")
        layout.prop(wm, "extractSmoothIterationsInt", text="Smooth Iterations")
    
    def execute(self, context):
        wm = context.window_manager
        activeObj = context.active_object
        
        # This is a hackish way to support redo functionality despite sculpt mode having its own undo system.
        # The set of conditions here is not something the user can create manually from the UI.
        # Unfortunately I haven't found a way to make Undo itself work
        if  2>len(bpy.context.selected_objects)>0 and \
            context.selected_objects[0] != activeObj and \
            context.selected_objects[0].name.startswith("Extracted."):
            rem = context.selected_objects[0]
            remname = rem.data.name
            bpy.data.scenes[0].objects.unlink(rem)
            bpy.data.objects.remove(rem)
            # remove mesh to prevent memory being cluttered up with hundreds of high-poly objects
            bpy.data.meshes.remove(bpy.data.meshes[remname])
        
        # For multires we need to copy the object and apply the modifiers
        try:
            if activeObj.modifiers["Multires"]:
                use_multires = True
                objCopy = helper.objDuplicate(activeObj)
                bpy.context.scene.objects.active = objCopy
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.boolean.mod_apply()
        except:
            use_multires = False
            pass
            
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Automerge will collapse the mesh so we need it off.
        if context.scene.tool_settings.use_mesh_automerge:
            automerge = True
            bpy.data.scenes[context.scene.name].tool_settings.use_mesh_automerge = False
        else:
            automerge = False

        # Until python can read sculpt mask data properly we need to rely on the hiding trick
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent();
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.hide_show(action='HIDE', area='MASKED')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate=None, TRANSFORM_OT_translate=None)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode='EDIT')
        
        # For multires we already have a copy, so lets use that instead of separate.
        if use_multires == True:
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='FACE')
            bpy.context.scene.objects.active = objCopy;
        else:
            try:
                bpy.ops.mesh.separate(type="SELECTED")
                bpy.context.scene.objects.active = context.selected_objects[0];
            except:
                bpy.ops.object.mode_set(mode='SCULPT')
                bpy.ops.paint.hide_show(action='SHOW', area='ALL')
                return {'FINISHED'}
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Rename the object for disambiguation
        bpy.context.scene.objects.active.name = "Extracted." + bpy.context.scene.objects.active.name
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Solid mode should create a two-sided mesh
        if wm.extractStyleEnum == 'SOLID':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.shrink_fatten(value=-wm.extractOffsetFloat) #offset
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.vertices_smooth(repeat = wm.extractSmoothIterationsInt) #smooth everything but border edges to sanitize normals
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.solidify(thickness = -wm.extractDepthFloat)
            bpy.ops.mesh.select_all(action='SELECT')
            if wm.extractSmoothIterationsInt>0: bpy.ops.mesh.vertices_smooth(repeat = wm.extractSmoothIterationsInt)
            bpy.ops.mesh.normals_make_consistent();

        elif wm.extractStyleEnum == 'SINGLE':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.shrink_fatten(value=-wm.extractOffsetFloat) #offset
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.vertices_smooth(repeat = wm.extractSmoothIterationsInt) #smooth everything but border edges to sanitize normals
            bpy.ops.mesh.select_all(action='SELECT')
            # This is to create an extra loop and prevent the bottom vertices running up too far in smoothing
            # Tried multiple ways to prevent this and this one seemed best
            bpy.ops.mesh.inset(thickness=0, depth=wm.extractDepthFloat/1000, use_select_inset=False)
            bpy.ops.mesh.inset(thickness=0, depth=wm.extractDepthFloat-(wm.extractDepthFloat/1000), use_select_inset=False)
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.vertices_smooth(repeat = wm.extractSmoothIterationsInt)
            bpy.ops.mesh.normals_make_consistent()

        elif wm.extractStyleEnum == 'FLAT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # Offset doesn't make much sense for Flat mode, so let's add it to the depth to make it a single op.
            bpy.ops.transform.shrink_fatten(value=-wm.extractDepthFloat-wm.extractOffsetFloat) 
            if wm.extractSmoothIterationsInt>0: bpy.ops.mesh.vertices_smooth(repeat = wm.extractSmoothIterationsInt)
            
        # clear mask on the extracted mesh
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.paint.mask_flood_fill(mode='VALUE', value=0)
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # make sure to recreate the odd selection situation for redo
        if use_multires:
            bpy.ops.object.select_pattern(pattern=context.active_object.name, case_sensitive=True, extend=False)
        bpy.context.scene.objects.active = activeObj
        
        # restore automerge
        if automerge:
            bpy.data.scenes[context.scene.name].tool_settings.use_mesh_automerge = True

        # restore mode for original object
        bpy.ops.object.mode_set(mode='SCULPT')
        return {'FINISHED'}