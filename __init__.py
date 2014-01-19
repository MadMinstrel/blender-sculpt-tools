bl_info = {
    "name": "Sculpt Tools UI",
    "author": "Ian Lloyd Dela Cruz, Nicholas Bishop, Roberto Roch, Bartosz Styperek, Piotr Adamowicz",
    "version": (1, 0),
    "blender": (2, 7, 0),
    "location": "3d View > Tool shelf, Shift-Ctrl-B",
    "description": "Simple UI for Boolean and Remesh operators",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Sculpting"}

if "bpy" in locals():
    import imp
    imp.reload(helper)
    imp.reload(booleanOps)
    imp.reload(greaseTrim)
    imp.reload(meshExtract)
    imp.reload(utilOps)
    imp.reload(Freeze)
    print("Reloaded multifiles")
else:
    from . import helper, booleanOps, greaseTrim, meshExtract, utilOps, Freeze
    print("Imported multifiles")
    
import bpy
import mathutils
import bmesh
from bpy.props import *

class RemeshBooleanPanel(bpy.types.Panel):
    """UI panel for the Remesh and Boolean buttons"""
    bl_label = "Sculpt Tools"
    bl_idname = "OBJECT_PT_remesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Sculpt"

    def draw(self, context):
        layout = self.layout
        edit = context.user_preferences.edit
        wm = context.window_manager
        
        row_rem = layout.row(align=True)
        row_rem.alignment = 'EXPAND'
        row_rem.operator("sculpt.remesh", text='Remesh')
        
        row_remint = layout.row(align=True)
        row_remint.alignment = 'EXPAND'

        try:
            row_remint.prop(wm, 'remeshDepthInt', text="Depth")
            row_remint.prop(wm, 'remeshSubdivisions', text="Subdivisions")
            
        except:
            pass
            
        row_rem2 = layout.row(align=True)
        row_rem2.alignment = 'EXPAND'
        row_rem2.prop(wm, 'remeshPreserveShape', text="Preserve Shape")
            
        layout.separator()
        row_freeze = layout.row(align=True)
        row_freeze.alignment = 'EXPAND'        
        row_freeze.operator("boolean.freeze", text="Freeze")
        row_freeze.operator("boolean.unfreeze", text="Unfreeze")
        layout.separator()

        row_b1 = layout.row(align=True)
        row_b1.alignment = 'EXPAND'
        row_b1.operator("boolean.union", text="Union")
        row_b1.operator("boolean.difference", text="Difference")
        row_b1.operator("boolean.intersect", text="Intersect")
        
        row_b2 = layout.row(align=True)
        row_b2.alignment = 'EXPAND'
        
        row_b2.operator("boolean.separate", text="Separate")
        row_b2.operator("boolean.clone", text="Clone")
        
        layout.separator()
        
        row_ma = layout.row(align=True)
        row_ma.alignment = 'EXPAND'
        row_ma.operator("boolean.mod_apply", text="Apply Mods")
        
        row_md = layout.row(align=True)
        row_md.alignment = 'EXPAND'
        row_md.operator("boolean.mesh_deform", text="Mesh Deform")
        
        row_dso = layout.row(align=True)
        row_dso.alignment = 'EXPAND'
        row_dso.operator("boolean.double_sided_off", text="Double Sided Off")
        
        row_sym = layout.row(align=True)
        row_sym.operator("boolean.grease_symm", text='Symmetrize')
        row_sym.prop(wm, "bolsymm", text="")
        
        row_mir = layout.row(align=True)
        row_mir.alignment = 'EXPAND'
        row_mir.operator("boolean.mod_xmirror", text="X-mirror")
        
        row_me_oprow = layout.row(align=True)
        row_me_oprow.alignment = 'EXPAND'
        row_me_oprow.operator("boolean.mask_extract", text="Extract Mask")
        
        layout.separator()
        
        row_gt = layout.row(align=True)
        row_gt.operator("boolean.grease_trim", text='Grease Cut')
        
        box = layout.box().column(align=True)
        if wm.expand_grease_settings == False: 
            box.prop(wm, "expand_grease_settings", icon="TRIA_RIGHT", icon_only=True, text=" Grease Pencil Settings", emboss=False)
        else:
            box.prop(wm, "expand_grease_settings", icon="TRIA_DOWN", icon_only=True, text=" Grease Pencil Settings", emboss=False)
            box.separator()
            box.prop(edit, "grease_pencil_manhattan_distance", text="Manhattan Distance")
            box.prop(edit, "grease_pencil_euclidean_distance", text="Euclidean Distance")
            boxrow = box.row(align=True)
            boxrow.prop(edit, "use_grease_pencil_smooth_stroke", text="Smooth")
            boxrow.prop(edit, "use_grease_pencil_simplify_stroke", text="Simplify")
            box.separator()                                         
            box.operator("boolean.purge_pencils", text='Purge All Grease Pencils')
        

        
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
        layout.operator("boolean.grease_symm",
                        text="Symmetrize",
                        icon='MOD_MIRROR')
        layout.operator("boolean.mesh_deform",
                        text="Mesh Deform",
                        icon='MOD_MESHDEFORM')
        layout.operator("boolean.grease_trim",
                        text="Grease Cut",
                        icon='SCULPTMODE_HLT')
        layout.operator("boolean.mask_extract",
                        text="Mask Extract",
                        icon='RETOPO')
        

def register():
    bpy.utils.register_module(__name__)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new('wm.call_menu', 'B', 'PRESS', ctrl = True, shift = True)
        kmi.properties.name = "BooleanOpsMenu"
        
        kmi = km.keymap_items.new('sculpt.optimize', 'U', 'PRESS')
        
        kmi = km.keymap_items.new('wm.context_toggle', 'X', 'PRESS')
        kmi.properties.data_path = "tool_settings.sculpt.use_symmetry_x"
        
        kmi = km.keymap_items.new('wm.context_toggle', 'E', 'PRESS', shift = True)
        kmi.properties.data_path = "tool_settings.sculpt.use_edge_collapse"
        
        kmi = km.keymap_items.new('sculpt.dynamic_topology_toggle', 'D', 'PRESS', shift = True)

    bpy.types.Object.frozen = BoolProperty(name="frozen", default = False)
        
    bpy.types.WindowManager.remeshDepthInt = IntProperty(min = 2, max = 10, default = 4)
    bpy.types.WindowManager.remeshSubdivisions = IntProperty(min = 0, max = 6, default = 0)
    bpy.types.WindowManager.remeshPreserveShape = BoolProperty(default = True)

    bpy.types.WindowManager.extractDepthFloat = FloatProperty(min = -10.0, max = 10.0, default = 0.1)
    bpy.types.WindowManager.extractOffsetFloat = FloatProperty(min = -10.0, max = 10.0, default = 0.0)

    bpy.types.WindowManager.extractSmoothIterationsInt = IntProperty(min = 0, max = 50, default = 5)
    
    bpy.types.WindowManager.extractStyleEnum = EnumProperty(name="Extract style",
                     items = (("SOLID","Solid",""),
                              ("SINGLE","Single Sided",""),
                              ("FLAT","Flat","")),
                     default = "SOLID")
    
    bpy.types.WindowManager.expand_grease_settings = BoolProperty(default=False)

    bpy.types.WindowManager.bolsymm = EnumProperty(name="",
                     items = (("NEGATIVE_X","-X to +X",""),
                              ("POSITIVE_X","+X to -X",""),
                              ("NEGATIVE_Y","-Y to +Y",""),
                              ("POSITIVE_Y","+Y to -Y",""),
                              ("NEGATIVE_Z","-Z to +Z",""),
                              ("POSITIVE_Z","+Z to -Z","")),                                                                                           
                     default = "NEGATIVE_X")
    
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
        del bpy.types.WindowManager.expand_grease_settings
        del bpy.types.WindowManager.extractDepthFloat
        del bpy.types.WindowManager.extractSmoothIterationsInt
        del bpy.types.WindowManager.bolsymm
        
    except:
        pass

if __name__ == "__main__":
    register()