#!/usr/bin/env python3
"""THE KEEPER — Act 3 (true-3D lane). Kip's rowboat reaches the light at dusk.

384 frames @24fps = 16s. Cycles CPU, 1920×1080, 48spp + denoise, AgX.
Same procedural lighthouse world as LIGHTHOUSE (Blender-5 API ports carried over);
KIP_001's low-poly counterpart uses the casting sheet's exact palette hexes.
Run: .venv/bin/python act3_3d.py [start [end]]   (resumable chunks, PNG frames)
"""
import math
import sys

import bpy

FPS = 24
RES = (1920, 1080)
SAMPLES = 48
FRAMES = 384

# KIP_001 casting sheet — canon hexes (studio/casting/keeper/KIP_001.json)
COAT = (0.85, 0.635, 0.306)      # #D9A24E in linear-ish approx
CAP = (0.165, 0.20, 0.345)       # #2A3358
SKIN = (0.79, 0.545, 0.42)       # #C98B6B
BEARD = (0.95, 0.937, 0.91)      # #F2EFE8
HULL = (0.43, 0.29, 0.18)


def mat(name, rgb, rough=0.7, emit=None, strength=0.0, alpha=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    if alpha is not None:
        b.inputs["Alpha"].default_value = alpha
    return m


def sky(elev_from, elev_to):
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    s = nt.nodes.new("ShaderNodeTexSky")
    s.sky_type = "MULTIPLE_SCATTERING"
    s.sun_rotation = math.radians(200)
    s.sun_intensity = 0.6
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(s.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    s.sun_elevation = math.radians(elev_from)
    s.keyframe_insert("sun_elevation", frame=1)
    s.sun_elevation = math.radians(elev_to)
    s.keyframe_insert("sun_elevation", frame=FRAMES)


def lighthouse_world():
    bpy.ops.mesh.primitive_plane_add(size=500)
    ocean = bpy.context.object
    om = mat("ocean", (0.012, 0.05, 0.09), rough=0.12)
    nt = om.node_tree
    b = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value = 5.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["W"].default_value = 0.0
    noise.inputs["W"].keyframe_insert("default_value", frame=1)
    noise.inputs["W"].default_value = 2.4
    noise.inputs["W"].keyframe_insert("default_value", frame=FRAMES)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.8
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    ocean.data.materials.append(om)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=6, location=(0, 0, -1.5))
    rock = bpy.context.object
    rock.scale = (1.4, 1.1, 0.55)
    tex = bpy.data.textures.new("rocktex", type="VORONOI")
    tex.noise_scale = 1.8
    dis = rock.modifiers.new("dis", "DISPLACE")
    dis.texture = tex
    dis.strength = 1.6
    rock.data.materials.append(mat("rock", (0.14, 0.12, 0.11), rough=0.95))

    white = mat("lh_white", (0.85, 0.82, 0.76), rough=0.5)
    red = mat("lh_red", (0.55, 0.12, 0.10), rough=0.5)
    dark = mat("lh_dark", (0.08, 0.08, 0.09), rough=0.4)
    glass = mat("lamp", (1, 1, 1), rough=0.2, emit=(1.0, 0.85, 0.55))
    for i, (z, r0, r1, m) in enumerate([(2.2, 2.0, 1.7, white), (4.4, 1.7, 1.45, red),
                                        (6.6, 1.45, 1.25, white), (8.8, 1.25, 1.1, red),
                                        (10.6, 1.1, 1.0, white)]):
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r0, radius2=r1, depth=2.3, location=(0, 0, z))
        bpy.context.object.data.materials.append(m)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.5, depth=0.25, location=(0, 0, 11.9))
    bpy.context.object.data.materials.append(dark)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.85, depth=1.5, location=(0, 0, 12.8))
    bpy.context.object.data.materials.append(glass)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=1.2, radius2=0.05, depth=1.1, location=(0, 0, 14.1))
    bpy.context.object.data.materials.append(red)

    bpy.ops.object.empty_add(location=(0, 0, 12.8))
    pivot = bpy.context.object
    beam_m = mat("beam", (1, 1, 1), emit=(1.0, 0.9, 0.6), alpha=0.08)
    for sgn in (1, -1):
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=2.2, depth=30,
                                        location=(sgn * 15, 0, 12.8), rotation=(0, sgn * math.pi / 2, 0))
        c = bpy.context.object
        c.data.materials.append(beam_m)
        c.parent = pivot
        c.matrix_parent_inverse = pivot.matrix_world.inverted()
        c.visible_camera = False
    return glass, beam_m, pivot


def kip_in_boat():
    """KIP_001 low-poly + rowboat, parented to a mover empty."""
    bpy.ops.object.empty_add(location=(0, 0, 0))
    boat = bpy.context.object
    boat.name = "boat_root"
    def add(obj):
        o = bpy.context.object
        o.parent = boat
        o.matrix_parent_inverse = boat.matrix_world.inverted()
        return o
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=1.0, depth=3.6,
                                        location=(0, 0, 0.25), rotation=(math.pi / 2, 0, 0))
    hull = add(bpy.context.object)
    hull.scale = (0.55, 1.0, 0.58)
    hull.data.materials.append(mat("hull", (0.26, 0.165, 0.10), rough=0.85))
    # Kip: coat cylinder, head sphere, cap cone, beard cube — canon palette
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.46, radius2=0.30, depth=0.95, location=(0, 0.2, 1.0))
    add(bpy.context.object).data.materials.append(mat("kcoat", COAT, rough=0.7))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.27, location=(0, 0.2, 1.68))
    add(bpy.context.object).data.materials.append(mat("kskin", SKIN, rough=0.6))
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.28, radius2=0.17, depth=0.24, location=(0, 0.2, 1.86))
    add(bpy.context.object).data.materials.append(mat("kcap", CAP, rough=0.7))
    bpy.ops.mesh.primitive_cube_add(size=0.27, location=(0, 0.44, 1.52))
    beard = add(bpy.context.object)
    beard.scale = (0.9, 0.4, 0.7)
    beard.data.materials.append(mat("kbeard", BEARD, rough=0.8))
    # oars: two thin cylinders, rocking
    for sgn in (1, -1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=2.4,
                                            location=(sgn * 0.85, 0.2, 0.7),
                                            rotation=(0, sgn * 1.1, 0))
        oar = add(bpy.context.object)
        oar.name = f"oar{sgn}"
        oar.data.materials.append(mat(f"oar{sgn}m", (0.30, 0.20, 0.12), rough=0.8))
        oar.rotation_euler[0] = -0.25
        oar.keyframe_insert("rotation_euler", frame=1)
        oar.rotation_euler[0] = 0.25
        oar.keyframe_insert("rotation_euler", frame=36)
        oar.rotation_euler[0] = -0.25
        oar.keyframe_insert("rotation_euler", frame=72)
        if oar.animation_data and oar.animation_data.action:
            for layer in oar.animation_data.action.layers:
                for strip in layer.strips:
                    for slot in oar.animation_data.action.slots:
                        cb = strip.channelbag(slot)
                        if cb:
                            for fc in cb.fcurves:
                                fc.modifiers.new("CYCLES")
    # journey: far → the rock's landing, with bob
    boat.location = (-34, -16, 0.05)
    boat.rotation_euler = (0, 0, math.radians(42))
    boat.keyframe_insert("location", frame=1)
    boat.keyframe_insert("rotation_euler", frame=1)
    boat.location = (-8.5, -5.5, 0.05)
    boat.rotation_euler = (0, 0, math.radians(38))
    boat.keyframe_insert("location", frame=300)
    boat.keyframe_insert("rotation_euler", frame=300)
    boat.location = (-8.0, -5.2, 0.05)
    boat.keyframe_insert("location", frame=FRAMES)
    return boat


def lamp_wake(glass, beam_m, pivot, on_frame=264):
    for ob in bpy.data.objects:
        if ob.type == "MESH" and any(m and m.name == "beam" for m in ob.data.materials):
            ob.visible_camera = False
            ob.keyframe_insert("visible_camera", frame=on_frame - 9)
            ob.visible_camera = True
            ob.keyframe_insert("visible_camera", frame=on_frame - 8)
    for m, strength in ((glass, 5.0), (beam_m, 9.0)):
        e = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        e.default_value = 0.0
        e.keyframe_insert("default_value", frame=on_frame - 8)
        e.default_value = strength
        e.keyframe_insert("default_value", frame=on_frame + 12)
    pivot.rotation_euler = (0, 0, 0)
    pivot.keyframe_insert("rotation_euler", frame=on_frame)
    pivot.rotation_euler = (0, 0, math.radians(260))
    pivot.keyframe_insert("rotation_euler", frame=FRAMES)


def camera():
    bpy.ops.object.empty_add(location=(-5, -3.5, 5.5))
    tgt = bpy.context.object
    bpy.ops.object.camera_add(location=(-36, -20, 2.2))
    cam = bpy.context.object
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    cam.data.lens = 32
    cam.data.lens = 32
    cam.data.keyframe_insert("lens", frame=1)
    cam.keyframe_insert("location", frame=1)
    tgt.keyframe_insert("location", frame=1)
    cam.location = (-23, -14.5, 3.6)
    cam.data.lens = 42
    cam.data.keyframe_insert("lens", frame=FRAMES)
    cam.keyframe_insert("location", frame=FRAMES)
    tgt.location = (-1.5, -1, 8.6)       # eye rises toward the lamp, boat stays in frame
    tgt.keyframe_insert("location", frame=FRAMES)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 18
    cam.data.dof.aperture_fstop = 2.8
    bpy.context.scene.camera = cam


def ease_all():
    for act in bpy.data.actions:
        if hasattr(act, "fcurves"):
            curves = act.fcurves
        else:
            curves = [fc for layer in act.layers for strip in layer.strips
                      for slot in act.slots
                      for fc in ((strip.channelbag(slot).fcurves) if strip.channelbag(slot) else [])]
        for fc in curves:
            for kp in fc.keyframe_points:
                kp.interpolation = "SINE"
                kp.easing = "EASE_IN_OUT"


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sky(2.0, -4.0)
    glass, beam_m, pivot = lighthouse_world()
    kip_in_boat()
    lamp_wake(glass, beam_m, pivot)
    camera()
    ease_all()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, FRAMES
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = "/home/user/ViralReel/out/keeper/a3/f"
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        sc.view_settings.view_transform = "Filmic"
    if len(args) >= 1 and args[0] == "still":
        sc.frame_set(int(args[1]))
        sc.render.filepath = f"/home/user/ViralReel/out/keeper/a3-still-{args[1]}.png"
        bpy.ops.render.render(write_still=True)
        print(f"STILL_OK {args[1]}")
        return
    if len(args) >= 1:
        sc.frame_start = int(args[0])
    if len(args) >= 2:
        sc.frame_end = min(int(args[1]), FRAMES)
    bpy.ops.render.render(animation=True)
    print("A3_CHUNK_OK")


main()
