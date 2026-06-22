def generate_blender_script(dimensions, output_folder):

    # Stem
    L       = float(dimensions.get("L",   830))
    D2      = float(dimensions.get("D2",  780))
    stem_d  = float(dimensions.get("stem_diameter",  12.7))
    float_d = float(dimensions.get("float_diameter", 25))
    stop_d  = float(dimensions.get("stopper_diameter", 41))

    # Enclosure
    encl_d  = float(dimensions.get("encl_diameter", 85))
    encl_h  = float(dimensions.get("encl_h",        80))

    # Cone
    cone_h      = float(dimensions.get("cone_h",           35))
    cone_top_d  = float(dimensions.get("cone_top_diameter", 85))
    cone_bot_d  = float(dimensions.get("cone_bot_diameter", 36))

    # Gland
    gland_d     = float(dimensions.get("gland_diameter", 20))
    gland_depth = float(dimensions.get("gland_depth",    30))

    # Derived values
    stem_r      = stem_d     / 2
    float_r     = float_d    / 2
    stop_r      = stop_d     / 2
    encl_r      = encl_d     / 2
    cone_top_r  = cone_top_d / 2
    cone_bot_r  = cone_bot_d / 2
    gland_r     = gland_d    / 2

    out      = output_folder.replace("\\", "/")
    obj_path = out + "/model.obj"
    png_path = out + "/render.png"

    script = f"""
import bpy
import math
import os

S = 0.001

# Stem
L        = {L}
D2       = {D2}
stem_r   = {stem_r}  * S
float_r  = {float_r} * S
stop_r   = {stop_r}  * S

# Enclosure
encl_r      = {encl_r}     * S
encl_h      = {encl_h}     * S

# Cone
cone_h      = {cone_h}     * S
cone_top_r  = {cone_top_r} * S
cone_bot_r  = {cone_bot_r} * S

# Gland
gland_r     = {gland_r}     * S
gland_depth = {gland_depth} * S

# Z positions
cone_z  = {cone_h}   / 2
encl_z  = {cone_h}   + {encl_h} / 2
gland_z = encl_z

obj_path = r"{obj_path}"
png_path = r"{png_path}"

os.makedirs(os.path.dirname(obj_path), exist_ok=True)
print("=== FLOAT SWITCH SCRIPT START ===")

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

mat_steel     = make_mat("Steel",     (0.8,  0.8,  0.85, 1), 0.9, 0.2)
mat_float     = make_mat("Float",     (0.7,  0.75, 0.8,  1), 0.9, 0.15)
mat_enclosure = make_mat("Enclosure", (0.55, 0.57, 0.6,  1), 0.7, 0.3)
mat_cone      = make_mat("Cone",      (0.5,  0.52, 0.55, 1), 0.8, 0.25)
mat_stopper   = make_mat("Stopper",   (0.5,  0.52, 0.55, 1), 0.8, 0.3)
mat_gland     = make_mat("Gland",     (0.2,  0.2,  0.22, 1), 0.6, 0.4)
mat_gland_nut = make_mat("GlandNut",  (0.3,  0.3,  0.32, 1), 0.7, 0.35)

# 1. Stem
bpy.ops.mesh.primitive_cylinder_add(
    radius=stem_r, depth=L*0.001,
    location=(0, 0, -(L/2)*0.001))
o = bpy.context.active_object
o.name = "Stem_Rod"; o.data.materials.append(mat_steel)
print("Stem OK")

# 2. Cone connector
bpy.ops.mesh.primitive_cone_add(
    vertices=64,
    radius1=cone_bot_r, radius2=cone_top_r,
    depth=cone_h,
    location=(0, 0, cone_z*0.001))
o = bpy.context.active_object
o.name = "Cone_Connector"; o.data.materials.append(mat_cone)
print("Cone OK")

# 3. Enclosure body
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=encl_r, depth=encl_h,
    location=(0, 0, encl_z*0.001))
o = bpy.context.active_object
o.name = "Enclosure_Body"; o.data.materials.append(mat_enclosure)
print("Enclosure OK")

# 4. Enclosure lid
import bpy as _bpy
lid_r = encl_r + 0.002
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=lid_r, depth=0.004,
    location=(0, 0, (encl_z*0.001 + encl_h/2 + 0.002)))
o = bpy.context.active_object
o.name = "Enclosure_Lid"; o.data.materials.append(mat_enclosure)

# 5. M-20 Gland body (SIDE of enclosure)
bpy.ops.mesh.primitive_cylinder_add(
    radius=gland_r, depth=gland_depth,
    location=(encl_r +