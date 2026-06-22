def generate_blender_script(dimensions, output_folder):

    L       = float(dimensions.get("L",   830))
    D2      = float(dimensions.get("D2",  780))
    float_d = float(dimensions.get("float_diameter", 25))
    stem_d  = float(dimensions.get("stem_diameter",  10))
    adapt_d = float(dimensions.get("adapter_diameter", 69))
    stop_d  = float(dimensions.get("stopper_diameter", 41))

    # Forward slashes only — Blender needs this
    out = output_folder.replace("\\", "/")
    obj_path = out + "/model.obj"
    png_path = out + "/render.png"

    script = f"""
import bpy
import math
import os

S = 0.001
L        = {L}
D2       = {D2}
float_r  = {float_d / 2} * S
stem_r   = {stem_d  / 2} * S
adapt_r  = {adapt_d / 2} * S
stop_r   = {stop_d  / 2} * S
obj_path = r"{obj_path}"
png_path = r"{png_path}"

os.makedirs(os.path.dirname(obj_path), exist_ok=True)

print("=== FLOAT SWITCH SCRIPT START ===")
print("L =", L, "D2 =", D2)

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def make_mat(name, color, metallic=0.8, roughness=0.2):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value   = metallic
    bsdf.inputs["Roughness"].default_value  = roughness
    return mat

mat_steel   = make_mat("Steel",   (0.8, 0.8,  0.85, 1))
mat_float   = make_mat("Float",   (0.7, 0.75, 0.8,  1))
mat_adapter = make_mat("Adapter", (0.6, 0.62, 0.65, 1))
mat_stopper = make_mat("Stopper", (0.5, 0.52, 0.55, 1))
mat_gland   = make_mat("Gland",   (0.3, 0.3,  0.32, 1))

print("Materials created OK")

# 1. Stem
bpy.ops.mesh.primitive_cylinder_add(
    radius=stem_r, depth=L*S, location=(0, 0, -(L/2)*S))
o = bpy.context.active_object
o.name = "Stem"
o.data.materials.append(mat_steel)
print("Stem created OK")

# 2. Adapter
bpy.ops.mesh.primitive_cylinder_add(
    radius=adapt_r, depth=50*S, location=(0, 0, 25*S))
o = bpy.context.active_object
o.name = "Adapter"
o.data.materials.append(mat_adapter)

# 3. Hex flange
bpy.ops.mesh.primitive_cylinder_add(
    vertices=6, radius=36*S, depth=15*S, location=(0, 0, 57.5*S))
o = bpy.context.active_object
o.name = "HEX_Flange"
o.data.materials.append(mat_adapter)

# 4. O-Ring
bpy.ops.mesh.primitive_torus_add(
    major_radius=adapt_r, minor_radius=2*S, location=(0, 0, 10*S))
o = bpy.context.active_object
o.name = "O_Ring"
mat_o = make_mat("ORing", (0.05, 0.05, 0.05, 1), 0.0, 0.9)
o.data.materials.append(mat_o)

# 5. BSP Port
bpy.ops.mesh.primitive_cylinder_add(
    radius=5*S, depth=20*S,
    location=(adapt_r + 10*S, 0, 25*S))
o = bpy.context.active_object
o.name = "BSP_Port"
o.rotation_euler = (0, math.radians(90), 0)
o.data.materials.append(mat_adapter)

# 6. Gland
bpy.ops.mesh.primitive_cylinder_add(
    radius=10*S, depth=20*S, location=(0, 0, 80*S))
o = bpy.context.active_object
o.name = "M20_Gland"
o.data.materials.append(mat_gland)

# 7. Float
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=float_r, location=(0, 0, -D2*S))
o = bpy.context.active_object
o.name = "Float_D2"
o.data.materials.append(mat_float)
bpy.ops.object.shade_smooth()

# 8. Stopper
bpy.ops.mesh.primitive_cylinder_add(
    radius=stop_r, depth=15*S,
    location=(0, 0, -(L - 7.5)*S))
o = bpy.context.active_object
o.name = "Stopper"
o.data.materials.append(mat_stopper)

print("All parts created OK")

# ---- EXPORT OBJ ----
try:
    bpy.ops.wm.obj_export(filepath=obj_path)
    print("OBJ exported OK:", obj_path)
except Exception as e:
    print("OBJ export error:", str(e))

# ---- RENDER PNG ----
try:
    bpy.ops.object.camera_add(location=(0.3, -0.6, -0.3))
    cam = bpy.context.active_object
    cam.rotation_euler = (math.radians(80), 0, math.radians(15))
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='AREA', location=(0.5, -0.5, 0.5))
    bpy.context.active_object.data.energy = 5000
    bpy.ops.object.light_add(type='AREA', location=(-0.5, 0.3, 0.2))
    bpy.context.active_object.data.energy = 2000

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.filepath = png_path
    scene.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print("PNG rendered OK:", png_path)
except Exception as e:
    print("Render error:", str(e))

print("=== SCRIPT COMPLETE ===")
"""
    return script