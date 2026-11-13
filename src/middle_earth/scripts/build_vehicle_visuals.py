#!/usr/bin/env python3
"""Generate the photo-inspired SAURCON appearance (standard library only).

Run from any directory. Writes reusable COLLADA visual meshes and replaces only
<visual> elements in the vehicle and OAK-D models. The non-visual SDF trees are
checked before writing: link/frame poses, mass/inertia, collisions, joints,
plugins and sensors must remain identical. Dimensions are metres.
"""
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

MODELS = Path(__file__).resolve().parents[1] / 'models'
TAU = 2 * math.pi


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])


def unit(a):
    n = math.sqrt(sum(x*x for x in a))
    return tuple(x / n for x in a)


class Mesh:
    def __init__(self):
        self.triangles = []

    def tri(self, a, b, c):
        if sum(x*x for x in cross(sub(b, a), sub(c, a))) > 1e-24:
            self.triangles.append((a, b, c))

    def quad(self, a, b, c, d):
        self.tri(a, b, c); self.tri(a, c, d)

    def add(self, other, transform=lambda p: p):
        for tri in other.triangles:
            self.tri(*(transform(p) for p in tri))

    def plate(self, xy, bottom, top):
        """Extrude a convex CCW polygon; separate bars form the open frame/trusses."""
        lo = [(x, y, bottom) for x, y in xy]
        hi = [(x, y, top) for x, y in xy]
        for i in range(1, len(xy) - 1):
            self.tri(lo[0], lo[i+1], lo[i]); self.tri(hi[0], hi[i], hi[i+1])
        for i in range(len(xy)):
            j = (i + 1) % len(xy)
            self.quad(lo[i], lo[j], hi[j], hi[i])

    def box(self, center, size, radius=0.0, yaw=0.0):
        x, y, z = center; sx, sy, sz = size
        r = min(radius, sx/2, sy/2)
        if r:
            xy = []
            for cx, cy, angle in ((sx/2-r, sy/2-r, 0), (-sx/2+r, sy/2-r, 90),
                                  (-sx/2+r, -sy/2+r, 180), (sx/2-r, -sy/2+r, 270)):
                for i in range(9):
                    a = math.radians(angle + i*90/8)
                    xy.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        else:
            xy = [(-sx/2, -sy/2), (sx/2, -sy/2), (sx/2, sy/2), (-sx/2, sy/2)]
        c, s = math.cos(yaw), math.sin(yaw)
        self.plate([(x + c*u - s*v, y + s*u + c*v) for u, v in xy], z - sz/2, z + sz/2)

    def beam(self, a, b, width, height):
        dx, dy = b[0]-a[0], b[1]-a[1]
        self.box(((a[0]+b[0])/2, (a[1]+b[1])/2, a[2]),
                 (math.hypot(dx, dy) + width, width, height), width/2, math.atan2(dy, dx))

    def lathe(self, profile, center=(0, 0, 0), axis=(0, 0, 1), segments=96):
        w = unit(axis)
        u = unit(cross((0, 0, 1) if abs(w[2]) < .9 else (0, 1, 0), w))
        v = cross(w, u)
        def p(r, z, a):
            return tuple(center[k] + r*math.cos(a)*u[k] + r*math.sin(a)*v[k] + z*w[k] for k in range(3))
        for j in range(len(profile) - 1):
            r0, z0 = profile[j]; r1, z1 = profile[j+1]
            for i in range(segments):
                a, b = TAU*i/segments, TAU*(i+1)/segments
                self.quad(p(r0, z0, a), p(r0, z0, b), p(r1, z1, b), p(r1, z1, a))

    def cylinder(self, center, radius, length, axis=(0, 0, 1), segments=32):
        self.lathe([(0, -length/2), (radius, -length/2), (radius, length/2), (0, length/2)],
                   center, axis, segments)

    def tube(self, a, b, radius, segments=12):
        d = sub(b, a)
        self.cylinder(tuple((x+y)/2 for x, y in zip(a, b)), radius,
                      math.sqrt(sum(x*x for x in d)), d, segments)

    def cable(self, points, radius=.001):
        for a, b in zip(points, points[1:]):
            self.tube(a, b, radius)

    def write(self, path):
        vertices, normals, faces = {}, {}, []
        for tri in self.triangles:
            n = tuple(round(x, 7) for x in unit(cross(sub(tri[1], tri[0]), sub(tri[2], tri[0]))))
            ni = normals.setdefault(n, len(normals))
            for p in tri:
                vi = vertices.setdefault(tuple(round(x, 7) for x in p), len(vertices))
                faces.extend((vi, ni))
        def source(name, values):
            flat = ' '.join(f'{x:.7g}' for p in values for x in p)
            return (f'<source id="{name}"><float_array id="{name}-array" count="{len(values)*3}">{flat}</float_array>'
                    f'<technique_common><accessor source="#{name}-array" count="{len(values)}" stride="3">'
                    '<param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/>'
                    '</accessor></technique_common></source>')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('<?xml version="1.0"?>\n'
            '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">\n'
            '<asset><contributor><authoring_tool>SAURCON build_vehicle_visuals.py</authoring_tool></contributor>'
            '<created>2026-11-13T00:00:00Z</created><modified>2026-11-13T00:00:00Z</modified>'
            '<unit name="meter" meter="1"/><up_axis>Z_UP</up_axis></asset>\n'
            '<library_geometries><geometry id="mesh"><mesh>' + source('positions', vertices) + source('normals', normals) +
            '<vertices id="vertices"><input semantic="POSITION" source="#positions"/></vertices>'
            f'<triangles count="{len(self.triangles)}"><input semantic="VERTEX" source="#vertices" offset="0"/>'
            '<input semantic="NORMAL" source="#normals" offset="1"/><p>' + ' '.join(map(str, faces)) +
            '</p></triangles></mesh></geometry></library_geometries>\n'
            '<library_visual_scenes><visual_scene id="scene"><node id="part"><instance_geometry url="#mesh"/>'
            '</node></visual_scene></library_visual_scenes><scene><instance_visual_scene url="#scene"/></scene></COLLADA>\n')


# Matte printed plastic, rubber, electronics and restrained metal highlights.
MATERIALS = {
    'white': ((.88, .89, .85), .15), 'red': ((.86, .018, .012), .20),
    'black': ((.018, .021, .025), .18), 'rubber': ((.025, .028, .031), .06),
    'rim': ((.032, .036, .043), .42), 'metal': ((.48, .50, .52), .65),
    'green': ((.025, .46, .14), .16), 'pink': ((.66, .025, .22), .15),
    'yellow': ((.9, .63, .02), .12), 'glass': ((.008, .016, .028), .75),
}


def visual(name, model, material, pose='0 0 0 0 0 0'):
    rgb, specular = MATERIALS[material]
    color = ' '.join(map(str, (*rgb, 1)))
    return (f'      <visual name="{name}">\n'
            f'        <pose>{pose}</pose>\n'
            f'        <geometry><mesh><uri>model://{model}/meshes/{name}.dae</uri></mesh></geometry>\n'
            f'        <material><ambient>{color}</ambient><diffuse>{color}</diffuse>'
            f'<specular>{specular} {specular} {specular} 1</specular></material>\n'
            '      </visual>')


def signature(element):
    """Everything except visual elements, comments and formatting is immutable."""
    return (element.tag, tuple(sorted(element.attrib.items())), (element.text or '').strip(),
            tuple(signature(child) for child in element if child.tag != 'visual'))


def replace_visuals(path, by_link):
    before = path.read_text()
    after = before
    for link, visuals in by_link.items():
        pattern = rf'(<link name="{re.escape(link)}">)(.*?)(</link>)'
        def replace(match):
            content = re.sub(r'\s*<visual\b.*?</visual>', '', match[2], flags=re.S).rstrip()
            return match[1] + content + '\n' + '\n'.join(visuals) + '\n    ' + match[3]
        after, count = re.subn(pattern, replace, after, flags=re.S)
        if count != 1:
            raise RuntimeError(f'Expected one link {link} in {path}, found {count}')
    if signature(ET.fromstring(before)) != signature(ET.fromstring(after)):
        raise RuntimeError(f'Refusing to change non-visual SDF in {path}')
    path.write_text(after)


def vehicle():
    parts = {key: Mesh() for key in ('frame', 'bumper', 'electronics', 'hardware', 'bracket',
                                    'servo_label', 'battery_label', 'wire_red', 'wire_yellow')}
    white, red, black, metal = (parts[k] for k in ('frame', 'bumper', 'electronics', 'hardware'))
    green, pink = parts['bracket'], parts['servo_label']
    # Geometry below uses model coordinates; the chassis visual pose subtracts
    # its existing 40 mm link offset. The simulated camera remains at (.092,0,.13).
    white.box((-.028, 0, .025), (.25, .106, .006), .008)
    for y in (-.050, .050):
        for z in (.031, .055):
            white.box((-.030, y, z), (.25, .007, .008), .003)
        for x in (-.150, -.025, .090):
            white.box((x, y, .043), (.010, .007, .032), .003)
        white.box((-.030, y, .081), (.25, .010, .007), .004)
    for x in (-.150, .090):
        white.box((x, 0, .081), (.012, .110, .007), .004)
    # Open upper deck, front camera mounting crossmember, four black standoffs.
    white.box((.068, 0, .081), (.026, .108, .007), .004)
    for x in (-.134, .077):
        for y in (-.045, .045):
            black.cylinder((x, y, .063), .0032, .031)
            black.cylinder((x, y, .0855), .0028, .002, segments=6)
    # Battery can, restraint straps and a multi-line label beneath the deck.
    metal.box((-.025, 0, .048), (.143, .082, .033), .004)
    for x in (-.075, .024):
        black.box((x, 0, .065), (.010, .084, .002), .001)
        for y in (-.042, .042):
            black.box((x, y, .048), (.010, .002, .034), .0008)
    parts['battery_label'].box((.047, 0, .048), (.001, .069, .025), .0004)
    for z in (.041, .044, .047, .050, .053):
        black.box((.0476, 0, z), (.0005, .058, .00065))
    # White computer enclosure and the distinctive green carrier behind OAK-D.
    green.box((-.026, 0, .088), (.139, .091, .006), .006)
    white.box((-.029, 0, .105), (.120, .077, .030), .006)
    for y in (-.041, .041):
        green.box((-.015, y, .097), (.105, .004, .018), .0015)
        for x in (-.057, .024):
            black.cylinder((x, y, .108), .0018, .002, segments=6)
    for x in (-.064, -.050, -.036, -.022):
        black.box((x, -.0388, .104), (.008, .0008, .003))
    # Camera's printed stand: it is geometry on the chassis, not a new frame.
    for y in (-.027, .027):
        white.box((.076, y, .097), (.010, .008, .026), .002)
        metal.cylinder((.081, y, .091), .002, .003, axis=(1, 0, 0), segments=16)
    white.box((.075, 0, .1095), (.020, .079, .004), .002)
    # Front and rear crossmembers; exposed printed wishbones and steering rods.
    white.box((.125, 0, .035), (.028, .113, .007), .004)
    white.box((-.127, 0, .032), (.028, .123, .012), .004)
    for side in (-1, 1):
        for z in (.025, .044):
            tip = (.127, side*.062, z)
            for x in (.094, .158):
                white.beam((x, side*.025, z), tip, .008, .005)
                black.cylinder((x, side*.025, z+.003), .0025, .0015, segments=6)
        metal.tube((.142, side*.009, .049), (.140, side*.065, .040), .0014)
        white.beam((-.140, side*.025, .037), (-.127, side*.062, .037), .009, .008)
    # MG90S-style steering servo: black upright case, pink label and mounting ears.
    black.box((.122, 0, .064), (.023, .013, .028), .0014)
    black.box((.122, 0, .052), (.033, .018, .003), .001)
    pink.box((.134, 0, .064), (.0008, .011, .013), .0003)
    for z in (.060, .063, .067):
        parts['battery_label'].box((.1345, 0, z), (.0003, .008, .0006))
    black.cylinder((.123, 0, .080), .003, .004)
    white.beam((.123, -.010, .082), (.123, .010, .082), .004, .002)
    # Broad red bow bumper with three open triangular truss sections.
    ys = [-.108 + i*.216/24 for i in range(25)]
    front = [(.207 - .018*(y/.108)**2, y, .025) for y in ys]
    for a, b in zip(front, front[1:]):
        red.beam(a, b, .006, .014)
    red.beam((.160, -.060, .025), (.160, .060, .025), .007, .014)
    for side in (-1, 1):
        red.beam((.160, side*.060, .025), (.189, side*.108, .025), .006, .014)
        red.beam((.160, side*.060, .025), (.205, side*.032, .025), .006, .014)
        red.beam((.160, 0, .025), (.205, side*.032, .025), .006, .014)
        white.box((.161, side*.041, .037), (.028, .010, .010), .003)
        black.cylinder((.170, side*.041, .043), .0025, .002, segments=6)
    # Short visible wire looms, tucked below the lens plane.
    parts['wire_red'].cable([(.111, -.007, .063), (.099, -.018, .070), (.065, -.030, .069),
                             (.052, -.031, .086), (.030, -.031, .091)], .0012)
    parts['wire_yellow'].cable([(.111, -.009, .063), (.095, -.022, .069), (.066, -.033, .070),
                               (.049, -.034, .084), (.028, -.034, .091)], .0008)
    black.cable([(.110, -.011, .063), (.098, -.024, .066), (.060, -.035, .071),
                 (.048, -.036, .083), (.026, -.036, .091)], .001)
    colors = dict(frame='white', bumper='red', electronics='black', hardware='metal', bracket='green',
                  servo_label='pink', battery_label='white', wire_red='red', wire_yellow='yellow')
    model = 'rc_ackermann_vehicle'
    visuals = []
    for name, mesh in parts.items():
        mesh.write(MODELS / model / 'meshes' / f'{name}.dae')
        visuals.append(visual(name, model, colors[name], '0 0 -0.04 0 0 0'))
    by_link = {'chassis': visuals, 'chassis_front': [], 'chassis_middle': [], 'chassis_back': []}
    # All four wheels reuse the same meshes in their existing rotating link frames.
    tyre, rim, hub = Mesh(), Mesh(), Mesh()
    tyre.lathe([(.021, -.020), (.026, -.020), (.030, -.018), (.0317, -.014),
                (.0320, -.009), (.0320, .009), (.0317, .014), (.030, .018),
                (.026, .020), (.021, .020), (.021, -.020)], segments=128)
    # Directional chevron blocks leave narrow recessed channels between treads.
    for i in range(48):
        for side in (-1, 1):
            for j in range(5):
                z0, z1 = side*(.0008 + j*.0032), side*(.0008 + (j+1)*.0032)
                def p(z, edge, depth):
                    a = TAU*i/48 + .18*(abs(z)/.017)**1.2 + edge*.042
                    r = .033 - max(0, abs(z)-.009)*.16 - depth
                    return (r*math.cos(a), r*math.sin(a), z)
                a, b, c, d = p(z0, -1, 0), p(z0, 1, 0), p(z1, 1, 0), p(z1, -1, 0)
                if side > 0: tyre.quad(a, b, c, d)
                else: tyre.quad(d, c, b, a)
                for edge in (-1, 1):
                    tyre.quad(p(z0, edge, .0012), p(z1, edge, .0012), p(z1, edge, 0), p(z0, edge, 0))
    rim.lathe([(.019, -.0203), (.0228, -.0203), (.0236, -.0185), (.021, -.016),
               (.021, .016), (.0236, .0185), (.0228, .0203), (.019, .0203), (.019, -.0203)])
    for face in (-1, 1):
        for i in range(10):
            a = TAU*i/10
            pts = [(r*math.cos(a+da), r*math.sin(a+da))
                   for r, da in ((.005, -.12), (.022, .13), (.022, .23), (.005, .12))]
            rim.plate(pts, face*.018 - .001, face*.018 + .001)
        rim.cylinder((0, 0, face*.018), .006, .004)
        hub.cylinder((0, 0, face*.0204), .0023, .0018, segments=6)
        for i in range(5):
            a = TAU*i/5
            hub.cylinder((.0041*math.cos(a), .0041*math.sin(a), face*.0202), .00065, .001, segments=12)
    for name, mesh in (('tyre', tyre), ('rim', rim), ('wheel_hardware', hub)):
        mesh.write(MODELS / model / 'meshes' / f'{name}.dae')
    wheel_visuals = [visual('tyre', model, 'rubber'), visual('rim', model, 'rim'), visual('wheel_hardware', model, 'metal')]
    for end in ('front', 'rear'):
        for side in ('left', 'right'):
            by_link[f'{end}_{side}_wheel'] = wheel_visuals
    for side, sign in (('left', 1), ('right', -1)):
        knuckle = Mesh()
        knuckle.box((0, -sign*.023, -.008), (.018, .008, .027), .003)
        name = f'{side}_knuckle'
        knuckle.write(MODELS / model / 'meshes' / f'{name}.dae')
        by_link[f'front_{side}_steer'] = [visual(name, model, 'white')]
    replace_visuals(MODELS / model / 'model.sdf', by_link)


def camera():
    model = 'oak_d_lite'
    housing, face, rings, lenses = Mesh(), Mesh(), Mesh(), Mesh()
    # The entire camera shell stays behind the optical origin (x=0). Rounded
    # YZ rectangles form the white cradle and dark, recessed three-lens face.
    def panel(mesh, x, width, height, depth, radius):
        p = Mesh(); p.box((0, 0, x), (width, height, depth), radius)
        mesh.add(p, lambda v: (v[2], v[0], v[1]))
    panel(housing, -.013, .104, .038, .023, .0045)
    panel(face, -.0015, .094, .029, .0015, .0035)
    for y, r in ((-.0375, .0046), (0, .0038), (.0375, .0046)):
        rings.cylinder((-.0006, y, .001), r, .0005, axis=(1, 0, 0), segments=48)
        lenses.cylinder((-.00025, y, .001), r*.67, .0003, axis=(1, 0, 0), segments=48)
    # Small mounting feet below the camera, also strictly visual.
    for y in (-.031, .031):
        housing.box((-.013, y, -.021), (.014, .009, .006), .002)
    visuals = []
    for name, mesh, color in (('housing', housing, 'white'), ('face', face, 'black'),
                              ('lens_rings', rings, 'rim'), ('lenses', lenses, 'glass')):
        mesh.write(MODELS / model / 'meshes' / f'{name}.dae')
        visuals.append(visual(name, model, color))
    replace_visuals(MODELS / model / 'model.sdf', {'oak': visuals})


if __name__ == '__main__':
    vehicle()
    camera()
    print('Updated vehicle and camera visuals; all non-visual SDF properties preserved.')
