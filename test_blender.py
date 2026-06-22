
import bpy
import os

print("=== BLENDER TEST START ===")
print("Blender version:", bpy.app.version_string)

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add a cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
print("Cube added OK")

# Test OBJ export
out = r"C:/Users/DELL/OneDrive - Shridhan Automation Pvt Ltd/Desktop/FloatSwitch_Automation/outputs/test.obj"
os.makedirs(os.path.dirname(out), exist_ok=True)

try:
    bpy.ops.wm.obj_export(filepath=out)
    print("OBJ export SUCCESS via wm.obj_export")
except Exception as e:
    print(f"wm.obj_export FAILED: {e}")
    try:
        bpy.ops.export_scene.obj(filepath=out)
        print("OBJ export SUCCESS via export_scene.obj")
    except Exception as e2:
        print(f"export_scene.obj FAILED: {e2}")

# List available export operators
print("=== AVAILABLE EXPORTERS ===")
for op in dir(bpy.ops.export_scene):
    print("export_scene." + op)
for op in dir(bpy.ops.wm):
    if 'export' in op.lower() or 'obj' in op.lower():
        print("wm." + op)

print("=== BLENDER TEST END ===")
