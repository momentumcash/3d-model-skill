"""
Momentum's 3D model skill: Blender build template.

Copy this file to models/<name>/build.py, fill in PALETTE from STYLE.md and build() from SPEC.md, then run:
    blender -b --python models/<name>/build.py -- models/<name>

It writes:
    <out>/<name>.fbx            the model (1 unit = 1 stud, origin at base centre, front = -Y), palette texture embedded
    <out>/palette.png           the colour swatch texture the model uses
    <out>/renders/*.png         front, side, back, top (orthographic) + three_quarter (perspective) for the critic

How colour works: every colour in PALETTE becomes a square on one small texture, and each part's UVs point at its
colour's square. That way Roblox gets ONE texture for the whole mesh and the colours survive the import.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

NAME = "treasure_chest"          # file name of the model
TRI_BUDGET = 3000                # from STYLE.md

# Palette: name -> hex (from STYLE.md). Only these colours are allowed.
PALETTE = {
    "wood":      "#9A5B32",
    "wood_dark": "#6E3E22",
    "gold":      "#F2B530",
    "gold_dark": "#C88A1A",
    "glow":      "#FFE27A",
}

# ---------------------------------------------------------------- helpers (you shouldn't need to change these)
def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

_parts = []

def _finish(obj, color, bevel, group="body"):
    """Bevel and tag a part with its palette colour and export group (parts that glow, move or are see-through get their own group = their own mesh)."""
    if color not in PALETTE:
        raise ValueError(f"colour '{color}' is not in PALETTE")
    if bevel and bevel > 0:
        m = obj.modifiers.new("bevel", "BEVEL")
        m.width = bevel
        m.segments = 2
        m.limit_method = "ANGLE"
        m.angle_limit = math.radians(35)
    obj["palette"] = color
    obj["group"] = group
    _parts.append(obj)
    return obj

def box(name, size, loc, rot=(0, 0, 0), color="wood", bevel=None, group="body"):
    """Bevelled box. size = (x, y, z) in studs, loc = centre, rot in degrees. bevel defaults to ~5% of smallest side."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=[math.radians(a) for a in rot])
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, color, min(size) * 0.05 if bevel is None else bevel, group)

def cylinder(name, radius, depth, loc, rot=(0, 0, 0), color="wood", verts=24, bevel=None, group="body"):
    """Bevelled cylinder standing on Z. rot (90,0,0) lays it along Y, (0,90,0) along X."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc,
                                        rotation=[math.radians(a) for a in rot])
    o = bpy.context.object
    o.name = name
    return _finish(o, color, min(radius, depth) * 0.06 if bevel is None else bevel, group)

def half_cylinder(name, radius, length, loc, color="wood", verts=24, bevel=None, group="body"):
    """A half cylinder lying along X with its flat side down (chest lids, roofs, arches)."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=length, location=loc,
                                        rotation=(0, math.radians(90), 0))
    o = bpy.context.object
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0),
                           plane_no=(0, 0, 1), clear_inner=True)
    bmesh.ops.holes_fill(bm, edges=bm.edges[:], sides=0)
    bm.to_mesh(o.data)
    bm.free()
    return _finish(o, color, radius * 0.05 if bevel is None else bevel, group)

def sphere(name, radius, loc, color="wood", segments=24, scale=(1, 1, 1), group="body"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=segments // 2, radius=radius, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return _finish(o, color, 0, group)

def cone(name, r1, r2, depth, loc, rot=(0, 0, 0), color="wood", verts=24, group="body"):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc,
                                    rotation=[math.radians(a) for a in rot])
    o = bpy.context.object
    o.name = name
    return _finish(o, color, min(r1, depth) * 0.05, group)

# ---------------------------------------------------------------- BUILD: fill this in from SPEC.md
def build():
    """Demo: a chunky treasure chest, 4 x 2.6 x 3 studs. Replace everything in here with your SPEC.md parts."""
    W, D, H = 4.0, 2.6, 1.8
    box("body", (W, D, H), (0, 0, H / 2), color="wood")
    for z in (0.6, 1.2):                                        # dark plank lines around the body
        box(f"plank_{z}", (W + 0.02, D + 0.02, 0.06), (0, 0, z), color="wood_dark", bevel=0.01)
    for x in (-W / 2 + 0.15, W / 2 - 0.15):                     # gold corner bands
        box(f"band_{x:+.1f}", (0.3, D + 0.08, H + 0.04), (x, 0, H / 2), color="gold")
    half_cylinder("lid", D / 2 + 0.02, W + 0.02, (0, 0, H), color="wood")
    for x in (-W / 2 + 0.15, W / 2 - 0.15):                     # gold bands over the lid
        half_cylinder(f"lid_band_{x:+.1f}", D / 2 + 0.08, 0.3, (x, 0, H), color="gold")
    box("lock_plate", (0.7, 0.12, 0.8), (0, -D / 2 - 0.06, H - 0.05), color="gold")
    box("keyhole", (0.14, 0.06, 0.3), (0, -D / 2 - 0.13, H - 0.12), color="wood_dark", bevel=0.02)
    sphere("gem", 0.16, (0, -D / 2 - 0.14, H + 0.18), color="glow", group="gem")   # own mesh: set it to Neon in Studio

# ---------------------------------------------------------------- pipeline (palette texture, join, export, renders)
def make_palette():
    names = list(PALETTE)
    n = len(names)
    cell = 32   # big solid squares so colours stay clean at low texture quality
    img = bpy.data.images.new("palette", width=cell * n, height=cell, alpha=False)
    px = []
    for _row in range(cell):
        for i in range(n):
            r, g, b = _hex(PALETTE[names[i]])
            px += [r, g, b, 1.0] * cell
    img.pixels = px
    return img, {nm: ((i + 0.5) / n, 0.5) for i, nm in enumerate(names)}

def apply_palette(img, uv_of):
    mat = bpy.data.materials.new("palette_mat")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.45
    for o in _parts:
        bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
        if not o.data.uv_layers:
            o.data.uv_layers.new(name="UVMap")
        u, v = uv_of[o["palette"]]
        for loop_uv in o.data.uv_layers.active.data:
            loop_uv.uv = (u, v)
        o.data.materials.clear()
        o.data.materials.append(mat)
        for p in o.data.polygons:
            p.use_smooth = False
    return mat

def join_and_origin():
    """Join parts into one mesh per export group, all sharing one origin at the base centre of the whole model."""
    pts = [o.matrix_world @ v.co for o in _parts for v in o.data.vertices]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    base = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    groups = {}
    for o in _parts:
        groups.setdefault(o["group"], []).append(o)
    objs = []
    for g, parts in groups.items():
        bpy.ops.object.select_all(action="DESELECT")
        for o in parts:
            o.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        if len(parts) > 1:
            bpy.ops.object.join()
        obj = bpy.context.object
        obj.name = NAME if g == "body" else f"{NAME}_{g}"
        bpy.context.scene.cursor.location = base
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        objs.append(obj)
    for obj in objs:
        obj.location -= base
    tris = 0
    for obj in objs:
        obj.data.calc_loop_triangles()
        n = len(obj.data.loop_triangles)
        tris += n
        if n > 20000:
            raise SystemExit(f"STOP: mesh {obj.name} has {n} triangles. Roblox caps one mesh at 20,000. Simplify the spec.")
    return objs, mx - mn, tris

def setup_scene():
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in s.render.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
    s.render.resolution_x = s.render.resolution_y = 900
    s.render.film_transparent = False
    s.view_settings.view_transform = "Standard"   # true palette colours (Filmic/AgX wash them out)
    w = s.world or bpy.data.worlds.new("World")
    s.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.82, 0.84, 0.87, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    s.collection.objects.link(sun)

def render_views(objs, dims, out):
    s = bpy.context.scene
    os.makedirs(os.path.join(out, "renders"), exist_ok=True)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    s.collection.objects.link(cam)
    s.camera = cam
    centre = Vector((0, 0, dims.z / 2))
    size = max(dims) * 1.35
    views = {  # name: (direction from centre, ortho)
        "front": (Vector((0, -1, 0)), True), "side": (Vector((1, 0, 0)), True), "back": (Vector((0, 1, 0)), True),
        "top": (Vector((0, 0, 1)), True), "three_quarter": (Vector((0.8, -1.0, 0.65)).normalized(), False),
    }
    for nm, (d, ortho) in views.items():
        cam.data.type = "ORTHO" if ortho else "PERSP"
        cam.data.ortho_scale = size
        cam.data.lens = 50
        cam.data.clip_start = 0.01
        cam.data.clip_end = size * 20
        dist = size * (3 if ortho else 2.2)
        cam.location = centre + d * dist
        cam.rotation_euler = (0, 0, 0) if nm == "top" else (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
        s.render.filepath = os.path.join(out, "renders", nm + ".png")
        bpy.ops.render.render(write_still=True)

def main():
    out = os.path.abspath(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else os.getcwd()
    os.makedirs(out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build()
    img, uv_of = make_palette()
    img.filepath_raw = os.path.join(out, "palette.png")
    img.file_format = "PNG"
    img.save()
    apply_palette(img, uv_of)
    objs, dims, tris = join_and_origin()
    if tris > TRI_BUDGET * 1.5:
        raise SystemExit(f"STOP: {tris} triangles is way over the budget of {TRI_BUDGET}. Simplify before exporting.")
    setup_scene()
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    # Roblox's recommended Blender FBX settings: units scale, -Z forward, Y up. Import in Studio with Scale Unit = Studs.
    bpy.ops.export_scene.fbx(filepath=os.path.join(out, NAME + ".fbx"), use_selection=True, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y", bake_anim=False,
                             path_mode="COPY", embed_textures=True, mesh_smooth_type="FACE")
    render_views(objs, dims, out)
    over = " OVER BUDGET" if tris > TRI_BUDGET else ""
    print(f"BUILT {NAME} ({len(objs)} mesh{'es' if len(objs) > 1 else ''}): {dims.x:.2f} x {dims.y:.2f} x {dims.z:.2f} studs, {tris} triangles (budget {TRI_BUDGET}){over}")
    print(f"FILES {out}")

main()
