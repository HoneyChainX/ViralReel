#!/usr/bin/env python3
"""LIGHTHOUSE — the platform's first true-3D film. Procedural bpy scene, Cycles CPU.

Three shots, one world, day → dusk:
  s1  0-120   wide orbit, warm afternoon
  s2  0-96    water-level push-in, sunset
  s3  0-144   lamp close-up, dusk: the light wakes and sweeps
15s @ 24fps total. Run: .venv/bin/python make_film.py [s1|s2|s3|still <shot> <frame>]

Everything is primitives + procedural materials — no external assets, so the film is
reproducible from this one file. previs notes inline; cinematography bible at bottom.
"""
import math
import sys

import bpy

FPS = 24
RES = (1280, 720)
SAMPLES = 48
SHOTS = {"s1": 120, "s2": 96, "s3": 144}


def clean():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, base, rough=0.6, emit=None, emit_strength=0.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def build_world(sun_elev_deg):
    w = bpy.data.worlds.new("sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "MULTIPLE_SCATTERING"  # Blender 5's physically-based sky (Nishita successor)
    sky.sun_elevation = math.radians(sun_elev_deg)
    sky.sun_rotation = math.radians(200)
    sky.sun_intensity = 0.6
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return sky


def build_scene():
    # ── Ocean: big plane, animated procedural waves via displacement in shader
    bpy.ops.mesh.primitive_plane_add(size=400)
    ocean = bpy.context.object
    ocean.name = "ocean"
    om = mat("ocean", (0.015, 0.07, 0.12), rough=0.15)
    nt = om.node_tree
    b = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 4.0
    noise.inputs["Detail"].default_value = 6.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.8
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    # drift the waves
    noise.noise_dimensions = "4D"
    noise.inputs["W"].default_value = 0.0
    noise.inputs["W"].keyframe_insert("default_value", frame=1)
    noise.inputs["W"].default_value = 3.0
    noise.inputs["W"].keyframe_insert("default_value", frame=150)
    ocean.data.materials.append(om)

    # ── Rock island: displaced icosphere
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=6, location=(0, 0, -1.5))
    rock = bpy.context.object
    rock.name = "rock"
    rock.scale = (1.4, 1.1, 0.55)
    tex = bpy.data.textures.new("rocktex", type="VORONOI")
    tex.noise_scale = 1.8
    dis = rock.modifiers.new("dis", "DISPLACE")
    dis.texture = tex
    dis.strength = 1.6
    rock.data.materials.append(mat("rock", (0.16, 0.14, 0.13), rough=0.95))

    # ── Lighthouse: tapered tower + gallery + lamp room + roof
    white = mat("lh_white", (0.85, 0.82, 0.76), rough=0.5)
    red = mat("lh_red", (0.55, 0.12, 0.10), rough=0.5)
    dark = mat("lh_dark", (0.08, 0.08, 0.09), rough=0.4, metal=0.6)
    glass_on = mat("lamp", (1, 1, 1), rough=0.2, emit=(1.0, 0.85, 0.55), emit_strength=0.0)

    for i, (z, r0, r1, m) in enumerate([
        (2.2, 2.0, 1.7, white), (4.4, 1.7, 1.45, red), (6.6, 1.45, 1.25, white),
        (8.8, 1.25, 1.1, red), (10.6, 1.1, 1.0, white),
    ]):
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r0, radius2=r1, depth=2.3,
                                        location=(0, 0, z))
        seg = bpy.context.object
        seg.name = f"tower{i}"
        seg.data.materials.append(m)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.5, depth=0.25, location=(0, 0, 11.9))
    bpy.context.object.data.materials.append(dark)          # gallery deck
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.85, depth=1.5, location=(0, 0, 12.8))
    lamp_room = bpy.context.object
    lamp_room.data.materials.append(glass_on)               # lamp room (emissive at dusk)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=1.2, radius2=0.05, depth=1.1,
                                    location=(0, 0, 14.1))
    bpy.context.object.data.materials.append(red)           # roof

    # ── The beam: two long emissive cones parented to a rotating empty
    bpy.ops.object.empty_add(location=(0, 0, 12.8))
    pivot = bpy.context.object
    pivot.name = "beam_pivot"
    beam_m = mat("beam", (1, 1, 1), emit=(1.0, 0.9, 0.6), emit_strength=0.0)
    if hasattr(beam_m, "blend_method"):  # EEVEE-era property, absent in Blender 5
        beam_m.blend_method = "BLEND"
    beam_m.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.10
    for sgn in (1, -1):
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.12, radius2=2.2, depth=30,
                                        location=(sgn * 15, 0, 12.8), rotation=(0, sgn * math.pi / 2, 0))
        cone = bpy.context.object
        cone.name = f"beam{sgn}"
        cone.data.materials.append(beam_m)
        cone.parent = pivot
        cone.matrix_parent_inverse = pivot.matrix_world.inverted()
        cone.visible_camera = False  # s3's lamp_wake turns beams on
    # gulls: three tiny dark v-shapes drifting (cheap life)
    gull_m = mat("gull", (0.05, 0.05, 0.06), rough=0.9)
    for i in range(3):
        bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.35, radius2=0.0, depth=0.06,
                                        location=(6 + i * 2.5, -4 - i * 2, 9 + i * 1.2))
        g = bpy.context.object
        g.name = f"gull{i}"
        g.data.materials.append(gull_m)
        g.keyframe_insert("location", frame=1)
        g.location.x -= 18
        g.location.z += 1.5
        g.keyframe_insert("location", frame=150)
    return glass_on, beam_m, pivot


def add_camera(loc, rot_target=(0, 0, 8), lens=35, dof_dist=None):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.data.lens = lens
    bpy.ops.object.empty_add(location=rot_target)
    tgt = bpy.context.object
    tgt.name = "cam_target"
    con = cam.constraints.new("TRACK_TO")
    con.target = tgt
    if dof_dist:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_distance = dof_dist
        cam.data.dof.aperture_fstop = 2.0
    bpy.context.scene.camera = cam
    return cam, tgt


def setup_render(shot, out_path, frame_end):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, frame_end
    # pip-wheel bpy has no ffmpeg encoder — render PNG frames; the farm assembles.
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = out_path
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        sc.view_settings.view_transform = "Filmic"


def animate_sun(sky, elev_from, elev_to, frames):
    sky.sun_elevation = math.radians(elev_from)
    sky.keyframe_insert("sun_elevation", frame=1)
    sky.sun_elevation = math.radians(elev_to)
    sky.keyframe_insert("sun_elevation", frame=frames)


def lamp_wake(glass_on, beam_m, pivot, on_frame, frames):
    for ob in bpy.data.objects:
        if ob.name.startswith("beam") and hasattr(ob, "visible_camera"):
            ob.visible_camera = True
    for m, strength in ((glass_on, 5.0), (beam_m, 6.0)):
        e = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        e.default_value = 0.0
        e.keyframe_insert("default_value", frame=on_frame - 6)
        e.default_value = strength
        e.keyframe_insert("default_value", frame=on_frame + 10)
    pivot.rotation_euler = (0, 0, 0)
    pivot.keyframe_insert("rotation_euler", frame=on_frame)
    pivot.rotation_euler = (0, 0, math.radians(300))
    pivot.keyframe_insert("rotation_euler", frame=frames)


def build_shot(shot):
    clean()
    frames = SHOTS[shot]
    glass_on, beam_m, pivot = build_scene()
    if shot == "s1":
        sky = build_world(18)                       # warm afternoon
        animate_sun(sky, 18, 14, frames)
        cam, tgt = add_camera((26, -22, 9), (0, 0, 7.5), lens=32)
        # slow orbit: 40 degrees over the shot
        bpy.ops.object.empty_add(location=(0, 0, 0))
        orb = bpy.context.object
        cam.parent = orb
        cam.matrix_parent_inverse = orb.matrix_world.inverted()
        orb.rotation_euler = (0, 0, 0)
        orb.keyframe_insert("rotation_euler", frame=1)
        orb.rotation_euler = (0, 0, math.radians(40))
        orb.keyframe_insert("rotation_euler", frame=frames)
    elif shot == "s2":
        sky = build_world(3)                        # sunset
        animate_sun(sky, 3, 0.8, frames)
        cam, tgt = add_camera((34, 6, 1.4), (0, 0, 9), lens=45)
        cam.keyframe_insert("location", frame=1)
        cam.location = (17, 3, 1.8)
        cam.keyframe_insert("location", frame=frames)
    else:  # s3 — dusk close-up, the light wakes
        sky = build_world(1.5)
        animate_sun(sky, 1.5, -3, frames)
        cam, tgt = add_camera((9.5, -7.5, 12.4), (0, 0, 12.7), lens=50, dof_dist=11)
        cam.keyframe_insert("location", frame=1)
        cam.location = (7.6, -5.9, 12.8)
        cam.keyframe_insert("location", frame=frames)
        lamp_wake(glass_on, beam_m, pivot, on_frame=36, frames=frames)
    for act in bpy.data.actions:                     # gentle ease everywhere
        if hasattr(act, "fcurves"):                  # ≤4.3 flat API
            curves = act.fcurves
        else:                                        # Blender 5 slotted actions
            curves = [fc for layer in act.layers for strip in layer.strips
                      for slot in act.slots for fc in (strip.channelbag(slot).fcurves
                                                       if strip.channelbag(slot) else [])]
        for fc in curves:
            for kp in fc.keyframe_points:
                kp.interpolation = "SINE"
                kp.easing = "EASE_IN_OUT"
    return frames


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    mode = args[0] if args else "s1"
    if mode == "still":
        shot, frame = args[1], int(args[2])
        build_shot(shot)
        sc = bpy.context.scene
        setup_render(shot, f"/home/user/ViralReel/out/lh-{shot}-f{frame}.png", SHOTS[shot])
        sc.render.image_settings.file_format = "PNG"
        sc.frame_set(frame)
        bpy.ops.render.render(write_still=True)
        print(f"STILL_OK {shot} f{frame}")
        return
    frames = build_shot(mode)
    setup_render(mode, f"/home/user/ViralReel/out/lighthouse3d/{mode}/f", frames)
    if len(args) > 1:                     # resume: render [start..end] only
        bpy.context.scene.frame_start = int(args[1])
    bpy.ops.render.render(animation=True)
    print(f"SHOT_OK {mode} {frames}f")


main()

# ── Cinematography bible (previs-director, one page) ──────────────────────────
# Lens: 32/45/60 — wider only when the world is the subject. Movement: one idea per
# shot (orbit, push, drift). Light: the sun does the acting; the lamp answers it.
# Palette: sea slate, tower bone-white + oxide red, dusk amber. The film is about
# the moment a built thing takes over from the sky. Grade: Filmic, no LUT needed —
# the colorist reviews shot joins for sky-tone continuity (s1→s2→s3 darkening must
# read as one evening, not three days).
