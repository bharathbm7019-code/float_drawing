def generate_blender_script(dimensions, output_folder):


    # ── Inputs ──────────────────────────────────────────────
    flange = dimensions.get("flange", "None")
    L           = float(dimensions.get("L",               830))
    D2          = float(dimensions.get("D2",              780))
    stem_d      = float(dimensions.get("stem_diameter",  12.7))
    float_d     = float(dimensions.get("float_diameter",   25))
    stop_d      = float(dimensions.get("stopper_diameter", 41))
    encl_d      = float(dimensions.get("encl_diameter",    85))
    encl_h      = float(dimensions.get("encl_h",           80))
    cone_h      = float(dimensions.get("cone_h",           35))
    cone_top_d  = float(dimensions.get("cone_top_diameter",85))
    cone_bot_d  = float(dimensions.get("cone_bot_diameter",36))
    gland_d     = float(dimensions.get("gland_diameter",   20))
    gland_depth = float(dimensions.get("gland_depth",      30))
    flange_od = 120        # Outside diameter (mm)
    flange_id = stem_d + 4 # Centre hole diameter (mm)
    flange_thk = 12        # Flange thickness (mm)
    bolt_circle = 90       # PCD (mm)
    bolt_dia = 12          # Bolt hole diameter (mm)
    bolt_count = 4
    neck_dia = 50          # Neck OD (mm)
    neck_h = 20            # Neck height (mm)
    # ── Derived (in mm) ─────────────────────────────────────
    stem_r      = stem_d     / 2
    float_r     = float_d    / 2
    stop_r      = stop_d     / 2
    encl_r      = encl_d     / 2
    cone_top_r  = cone_top_d / 2
    cone_bot_r  = cone_bot_d / 2
    gland_r     = gland_d    / 2

    # Z positions in mm (converted to metres inside script)
    cone_z   = cone_h / 2
    encl_z   = cone_h + encl_h / 2
    lid_z    = cone_h + encl_h + 2
    gland_z  = encl_z
    flange_z = cone_h + flange_thk / 2
    neck_z = flange_z + flange_thk / 2 + neck_h / 2

    # Camera math (all in metres)
    S            = 0.001
    model_top    = (cone_h + encl_h + 4) * S      # top of lid
    model_bottom = -(L - 7.5) * S                  # bottom of stopper
    model_height = model_top - model_bottom
    center_z     = (model_top + model_bottom) / 2
    cam_dist     = model_height * 0.8

    # Output paths
    out      = output_folder.replace("\\", "/")
    obj_path = out + "/model.obj"
    png_path = out + "/render.png"

    # ── Build script line by line ────────────────────────────
    lines = [
        "import bpy, math, os",
        "S = 0.001",
        "",
        f"L           = {L}",
        f"D2          = {D2}",
        f"stem_r      = {stem_r}    * S",
        f"float_r     = {float_r}   * S",
        f"stop_r      = {stop_r}    * S",
        f"encl_r      = {encl_r}    * S",
        f"encl_h      = {encl_h}    * S",
        f"cone_h      = {cone_h}    * S",
        f"cone_top_r  = {cone_top_r}* S",
        f"cone_bot_r  = {cone_bot_r}* S",
        f"gland_r     = {gland_r}   * S",
        f"gland_depth = {gland_depth}* S",
        f"cone_z      = {cone_z}    * S",
        f"encl_z      = {encl_z}    * S",
        f"lid_z       = {lid_z}     * S",
        f"gland_z     = {gland_z}   * S",
        f'flange_material = "{flange}"',
        f"flange_od   = {flange_od} * S",
        f"flange_id   = {flange_id} * S",
        f"flange_thk  = {flange_thk} * S",
        f"bolt_circle = {bolt_circle} * S",
        f"bolt_dia    = {bolt_dia} * S",
        f"bolt_count  = {bolt_count}",
        f"neck_dia    = {neck_dia} * S",
        f"neck_h      = {neck_h} * S",
        f"flange_z    = {flange_z} * S",
        f"neck_z      = {neck_z} * S",
        "os.makedirs(os.path.dirname(obj_path), exist_ok=True)",
        "print('=== START ===')",
        "",
        "bpy.ops.object.select_all(action='SELECT')",
        "bpy.ops.object.delete()",
        "",
        "def mat(name, color, m=0.8, r=0.2):",
        "    o = bpy.data.materials.new(name=name)",
        "    o.use_nodes = True",
        "    b = o.node_tree.nodes['Principled BSDF']",
        "    b.inputs['Base Color'].default_value = color",
        "    b.inputs['Metallic'].default_value   = m",
        "    b.inputs['Roughness'].default_value  = r",
        "    return o",
        "",
        "ms = mat('Steel',    (0.8, 0.8,  0.85,1), 0.9, 0.15)",
        "mf = mat('Float',    (0.7, 0.75, 0.8, 1), 0.9, 0.15)",
        "me = mat('Enclosure',(0.6, 0.62, 0.65,1), 0.85,0.2)",
        "mc = mat('Cone',     (0.55,0.57, 0.6, 1), 0.8, 0.25)",
        "mp = mat('Stopper',  (0.5, 0.52, 0.55,1), 0.8, 0.3)",
        "mg = mat('Gland',    (0.2, 0.2,  0.22,1), 0.6, 0.4)",
        "mn = mat('GlandNut', (0.3, 0.3,  0.32,1), 0.7, 0.35)",
        "",
        "# 1. Stem",
        "bpy.ops.mesh.primitive_cylinder_add(radius=stem_r, depth=L*S, location=(0,0,-(L/2)*S))",
        "o=bpy.context.active_object; o.name='Stem'; o.data.materials.append(ms)",
        "",
        "# 2. Cone",
        "bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=cone_bot_r, radius2=cone_top_r, depth=cone_h, location=(0,0,cone_z))",
        "o=bpy.context.active_object; o.name='Cone'; o.data.materials.append(mc)""# 2A. Flange",
        "if '" + flange + "' != 'None':",
        "    bpy.ops.mesh.primitive_cylinder_add(",
        "        vertices=64,",
        "        radius=flange_od/2,",
        "        depth=flange_thk,",
        "        location=(0,0,flange_z)",
        "    )",
        "    o = bpy.context.active_object",
        "    o.name = 'Flange'",
        "    o.data.materials.append(ms)",
        "",
        "# 3. Enclosure",
        "bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=encl_r, depth=encl_h, location=(0,0,encl_z))",
        "o=bpy.context.active_object; o.name='Enclosure'; o.data.materials.append(me)",
        "",
        "# 2A. Industrial Flange",
        "if flange_material != 'None':",

        "    bpy.ops.mesh.primitive_cylinder_add(",
        "        vertices=64,",
        "        radius=flange_od/2,",
        "        depth=flange_thk,",
        "        location=(0,0,flange_z)",
        "    )",
        "    flange_obj = bpy.context.active_object",
        "    flange_obj.name = 'Flange'",
        "    flange_obj.data.materials.append(ms)",

        "    bpy.ops.mesh.primitive_cylinder_add(",
        "        vertices=64,",
        "        radius=neck_dia/2,",
        "        depth=neck_h,", 
        "        location=(0,0,neck_z)",
        "    )",
        "    neck = bpy.context.active_object",
        "    neck.name = 'FlangeNeck'",
        "    neck.data.materials.append(ms)",

        "    import math",
        "    for i in range(bolt_count):",
        "        ang = math.radians(i * (360 / bolt_count))", 
        "        x = (bolt_circle/2) * math.cos(ang)",
        "        y = (bolt_circle/2) * math.sin(ang)",

        "        bpy.ops.mesh.primitive_cylinder_add(",
        "            vertices=32,",
        "            radius=bolt_dia/2,",
        "            depth=flange_thk + 0.002,",
        "            location=(x,y,flange_z)",
        "        )",
        "        hole = bpy.context.active_object",
        "        hole.name = f'BoltHole{i}'",
        "    bpy.context.view_layer.objects.active = flange_obj",
        "    for obj in bpy.data.objects:",
        "        if obj.name.startswith('BoltHole'):",
        "            mod = flange_obj.modifiers.new(name='Bool', type='BOOLEAN')",
        "            mod.operation = 'DIFFERENCE'",
        "            mod.object = obj",
        "            bpy.ops.object.modifier_apply(modifier=mod.name)",
        "# 4. Lid",
        "bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=encl_r+0.002, depth=0.004, location=(0,0,lid_z))",
        "o=bpy.context.active_object; o.name='Lid'; o.data.materials.append(me)",
        "",
        "# 5. Gland body",
        "bpy.ops.mesh.primitive_cylinder_add(radius=gland_r, depth=gland_depth, location=(encl_r+gland_depth/2,0,gland_z))",
        "o=bpy.context.active_object; o.name='Gland'; o.rotation_euler=(0,1.5708,0); o.data.materials.append(mg)",
        "",
        "# 6. Gland nut",
        "bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=gland_r*1.3, depth=0.008, location=(encl_r+0.004,0,gland_z))",
        "o=bpy.context.active_object; o.name='GlandNut'; o.rotation_euler=(0,1.5708,0); o.data.materials.append(mn)",
        "",
        "# 7. Cable tip",
        "bpy.ops.mesh.primitive_cylinder_add(radius=gland_r*0.4, depth=0.01, location=(encl_r+gland_depth+0.005,0,gland_z))",
        "o=bpy.context.active_object; o.name='Cable'; o.rotation_euler=(0,1.5708,0); o.data.materials.append(mg)",
        "",
        "# 8. Float",
        "bpy.ops.mesh.primitive_uv_sphere_add(radius=float_r, location=(0,0,-D2*S))",
        "o=bpy.context.active_object; o.name='Float'; o.data.materials.append(mf)",
        "bpy.ops.object.shade_smooth()",
        "",
        "# 9. Stopper",
        "bpy.ops.mesh.primitive_cylinder_add(radius=stop_r, depth=0.015, location=(0,0,-(L-7.5)*S))",
        "o=bpy.context.active_object; o.name='Stopper'; o.data.materials.append(mp)",
        "print('All parts OK')",
        "",
        "# 10. Camera — fully dynamic",
        f"center_z  = {center_z:.6f}",
        f"cam_dist  = {cam_dist:.6f}",
        f"model_h   = {model_height:.6f}",
        "",
        "bpy.ops.object.camera_add(location=(cam_dist*0.4, -cam_dist, center_z))",
        "cam = bpy.context.active_object",
        "cam.name = 'Camera'",
        "# Point camera AT the model center using constraints",
        "bpy.ops.object.constraint_add(type='TRACK_TO')",
        "cam.constraints['Track To'].target = None",
        "",
        "# Manually aim: rotation_euler X tilts up/down",
        "# With camera at (x, -y, center_z) pointing at (0,0,center_z)",
        "# We need X rotation = 90deg (looking horizontally)",
        "cam.rotation_euler = (1.5708, 0, 0.38)",
        "cam.data.lens = 50",
        "cam.data.clip_end = 100.0",
        "bpy.context.scene.camera = cam",
        f"print('Camera: dist={cam_dist:.3f}m, center_z={center_z:.3f}m')",
        "",
        "# 11. World",
        "world = bpy.context.scene.world",
        "world.use_nodes = True",
        "world.node_tree.nodes['Background'].inputs[0].default_value = (0.06,0.06,0.06,1)",
        "world.node_tree.nodes['Background'].inputs[1].default_value = 1.0",
        "",
        "# 12. Lights — scale with model",
        f"ld = {cam_dist:.6f}",
        f"cz = {center_z:.6f}",
        "bpy.ops.object.light_add(type='AREA', location=(ld*0.6, -ld*0.8, cz+ld*0.4))",
        "bpy.context.active_object.data.energy = 10000",
        "bpy.context.active_object.data.size   = ld*0.8",
        "bpy.ops.object.light_add(type='AREA', location=(-ld*0.5, ld*0.4, cz))",
        "bpy.context.active_object.data.energy = 5000",
        "bpy.context.active_object.data.size   = ld*0.6",
        "bpy.ops.object.light_add(type='SUN',  location=(1,-1,2))",
        "bpy.context.active_object.data.energy = 2",
        "",
        "# 13. Export OBJ",
        "try:",
        "    bpy.ops.wm.obj_export(filepath=obj_path)",
        "    print('OBJ OK')",
        "except Exception as e:",
        "    print('OBJ error:', e)",
        "",
        "# 14. Render PNG",
        "try:",
        "    sc = bpy.context.scene",
        "    sc.render.engine          = 'CYCLES'",
        "    sc.cycles.device          = 'CPU'",
        "    sc.cycles.samples         = 64",
        "    sc.cycles.use_denoising   = True",
        "    sc.render.resolution_x    = 1280",
        "    sc.render.resolution_y    = 720",
        "    sc.render.filepath        = png_path",
        "    sc.render.image_settings.file_format = 'PNG'",
        "    bpy.ops.render.render(write_still=True)",
        "    print('PNG OK')",
        "except Exception as e:",
        "    print('Render error:', e)",
        "",
        "print('=== DONE ===')",
    ]

    return "\n".join(lines)