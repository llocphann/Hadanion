#!/usr/bin/env python3
"""Convert our own Blender glTF exports to a dormant Qt Quick 3D fixture.

The fixture uses installed ProceduralMesh/Timeline types and needs no Assimp
importer or new system package. It is not a general untrusted-asset loader,
runtime package, event source, resource benchmark or production actor.
"""
import hashlib
import json
import math
from pathlib import Path
import struct


def number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError("non-finite geometry or keyframe")
    return format(value, ".9g")


def vector(values, quaternion=False):
    if quaternion:
        values = [values[3], *values[:3]]
    return "Qt." + ("quaternion" if quaternion else "vector3d") + "(" + ",".join(map(number, values)) + ")"


class Asset:
    """Bounded local generated glTF data; external paths/textures are rejected."""
    def __init__(self, path):
        self.path = Path(path)
        if self.path.stat().st_size > 4 * 1024 * 1024:
            raise ValueError("oversized glTF fixture")
        self.g = json.loads(self.path.read_text())
        if self.g.get("asset", {}).get("version") != "2.0" or len(self.g.get("buffers", [])) != 1:
            raise ValueError("unexpected generated asset")
        if self.g.get("images") or self.g.get("textures") or self.g.get("skins"):
            raise ValueError("only original untextured object/morph geometry is allowed")
        buffer = self.g["buffers"][0]
        if buffer.get("uri") != self.path.with_suffix(".bin").name or buffer["byteLength"] > 8 * 1024 * 1024:
            raise ValueError("non-local or oversized fixture buffer")
        self.raw = self.path.with_suffix(".bin").read_bytes()
        if len(self.raw) != buffer["byteLength"]:
            raise ValueError("truncated fixture buffer")

    def read(self, index):
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(self.g["accessors"]):
            raise ValueError("invalid accessor index")
        accessor = self.g["accessors"][index]
        if accessor.get("sparse") or accessor.get("normalized"):
            raise ValueError("unsupported generated accessor")
        size = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[accessor["type"]]
        code, width = {5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}[accessor["componentType"]]
        view = self.g["bufferViews"][accessor["bufferView"]]
        if view.get("buffer", 0) != 0:
            raise ValueError("unexpected buffer")
        offset = accessor.get("byteOffset", 0)
        stride = view.get("byteStride", width * size)
        count = accessor["count"]
        if not isinstance(count, int) or isinstance(count, bool) or not 0 < count <= 200000:
            raise ValueError("oversized accessor")
        end = offset + (count-1)*stride + width*size
        start = view.get("byteOffset", 0)
        if offset < 0 or stride < width*size or end > view["byteLength"] or start < 0 or start+end > len(self.raw):
            raise ValueError("out-of-bounds accessor")
        values = [list(struct.unpack_from("<" + code*size, self.raw, start+offset+i*stride)) for i in range(count)]
        for row in values:
            for value in row:
                number(value)
        return values

    def geometry(self):
        meshes = []
        for mesh in self.g["meshes"]:
            if len(mesh["primitives"]) != 1:
                raise ValueError("unexpected multi-material mesh")
            primitive = mesh["primitives"][0]
            if primitive.get("mode", 4) != 4:
                raise ValueError("only triangles are supported")
            positions = self.read(primitive["attributes"]["POSITION"])
            normals = self.read(primitive["attributes"]["NORMAL"])
            indexes = [row[0] for row in self.read(primitive["indices"])]
            if len(normals) != len(positions) or len(indexes) % 3 or any(i >= len(positions) for i in indexes):
                raise ValueError("invalid mesh topology")
            targets = [{k: self.read(v) for k, v in target.items() if k in ("POSITION", "NORMAL")}
                       for target in primitive.get("targets", [])]
            if any(len(values) != len(positions) for target in targets for values in target.values()):
                raise ValueError("morph topology mismatch")
            meshes.append(dict(positions=positions, normals=normals, indexes=indexes,
                               targets=targets, material=primitive["material"]))
        return meshes


def qml_component(character, folder, output):
    receipt = json.loads((folder.parent / "export.json").read_text())["characters"][character]
    assets = {name: Asset(folder / (name+".gltf")) for name in receipt["clips"]}
    for name, asset in assets.items():
        expected = receipt["clips"][name]
        if (hashlib.sha256(asset.path.read_bytes()).hexdigest() != expected["gltfSha256"] or
                hashlib.sha256(asset.raw).hexdigest() != expected["binSha256"]):
            raise ValueError("generated asset digest mismatch")
    base = assets["laptop_typing_loop"]
    geometry = base.geometry()
    names = [node.get("name", "") for node in base.g["nodes"]]
    if len(set(names)) != len(names):
        raise ValueError("ambiguous original object names")
    core_nodes=[i for i,name in enumerate(names) if name in ('Liquid body','Octo liquid head')]
    if len(core_nodes)!=1:raise ValueError('one original body volume is required')
    for asset in assets.values():
        if [n.get("name", "") for n in asset.g["nodes"]] != names or asset.geometry() != geometry:
            raise ValueError("geometry changed across a baked performance")
    mesh_js = [".pragma library", "var meshes=" + json.dumps(geometry, separators=(",", ":"))]
    mesh_js.append('''function vectors(data) { return data.map(v=>Qt.vector3d(v[0],v[1],v[2])) }
function morph(base,targets,weights,channel,normal) {
    return base.map((v,i)=>{
        let x=v[0],y=v[1],z=v[2]
        for(let j=0;j<targets.length;j++) {
            const d=targets[j][channel]?.[i],w=weights[j]??0
            if(d&&w){x+=d[0]*w;y+=d[1]*w;z+=d[2]*w}
        }
        const p=Qt.vector3d(x,y,z)
        return normal ? p.normalized() : p
    })
}''')
    (output / (character.title()+"Geometry.js")).write_text("\n".join(mesh_js)+"\n")
    lines = ["import QtQuick", "import QtQuick3D", "import QtQuick3D.Helpers", "import QtQuick.Timeline",
             'import "'+character.title()+'Geometry.js" as Data', "Node {", "id: root",
             'property string clip: "laptop_typing_loop"', "property real phase: 0", "property bool propVisible: true",
             'readonly property string character: '+json.dumps(character),
             'property color theme: "#36d3f3"', "property bool active: true", "visible: active",
             'property string opticsProfile: "studio"',
             "property var blendFrom: null", "property real blendProgress: 1",
             '''function fraction() {return Math.max(0,Math.min(1,blendProgress))}
function blendedVector(index,channel,current) {
    const a=blendFrom?.[index]?.[channel],t=fraction()
    return !a||t>=1 ? current : Qt.vector3d(a[0]*(1-t)+current.x*t,a[1]*(1-t)+current.y*t,a[2]*(1-t)+current.z*t)
}
function blendedRotation(index,current) {
    const a=blendFrom?.[index]?.rotation,t=fraction()
    if(!a||t>=1)return current
    const dot=a[0]*current.scalar+a[1]*current.x+a[2]*current.y+a[3]*current.z
    const sign=dot<0?-1:1
    const q=[a[0]*(1-t)+current.scalar*t*sign,a[1]*(1-t)+current.x*t*sign,
        a[2]*(1-t)+current.y*t*sign,a[3]*(1-t)+current.z*t*sign]
    const length=Math.hypot(...q)
    return length>0 ? Qt.quaternion(...q.map(v=>v/length)) : current
}
function blendedWeight(index,channel,current) {
    const a=blendFrom?.[index]?.weights?.[channel],t=fraction()
    return a===undefined||t>=1 ? current : a*(1-t)+current*t
}
function snapshot() {
    return objects.map(n=>({position:[n.position.x,n.position.y,n.position.z],
        scale:[n.scale.x,n.scale.y,n.scale.z],rotation:[n.rotation.scalar,n.rotation.x,n.rotation.y,n.rotation.z],
        weights:n.morphWeights?n.morphWeights.slice():[]}))
}''',
             "function step(times,values,t) {let i=0;while(i+1<times.length&&times[i+1]<=t+.0001)i++;return values[i]}",
             "function named(name) { return objects.find(n=>n.objectName===name)??null }",
             "readonly property var materials: ["+",".join("mat"+str(i) for i in range(len(base.g["materials"])))+",matCore]",
             "readonly property var coreVolumes: [core"+str(core_nodes[0])+"]",
             "readonly property var objects: ["+",".join("n"+str(i) for i in range(len(names)))+"]"]
    for i, material in enumerate(base.g["materials"]):
        name = material["name"]
        pbr = material.get("pbrMetallicRoughness", {})
        extensions = material.get("extensions", {})
        original = pbr.get("baseColorFactor", [1,1,1,1])
        liquid = "liquid" in name.lower()
        iris = "cyan iris" in name.lower()
        limb = "opaque glossy tentacles" in name.lower()
        if any(word in name.lower() for word in ("liquid", "theme accent", "cyan iris", "opaque glossy tentacles")):
            factor = .12 if iris else .9 if liquid else .65 if limb else 1
            color = "root.opticsProfile===\"abyss\" ? Qt.rgba(root.theme.r*"+number(factor)+",root.theme.g*"+number(factor)+",root.theme.b*"+number(factor)+",1) : root.theme"
        elif "anodized" in name.lower():
            color = "Qt.rgba(root.theme.r*.075,root.theme.g*.075,root.theme.b*.075,1)"
        else:
            color = "Qt.rgba("+",".join(map(number,original))+")"
        # Use the desktop's mild optical transmission for this native prototype;
        # its material mapping is a proposal, not Blender/production pixel parity.
        transmission = extensions.get("KHR_materials_transmission", {}).get("transmissionFactor", 0)
        if "liquid" in name.lower():
            transmission = .16
        if "opaque glossy tentacles" in name.lower():
            transmission = 0
        emission = vector(material.get("emissiveFactor", [0,0,0]))
        if iris or "theme accent" in name.lower():
            gain = .025 if iris else .5
            emission = "root.opticsProfile===\"abyss\" ? Qt.vector3d(root.theme.r*"+number(gain)+",root.theme.g*"+number(gain)+",root.theme.b*"+number(gain)+") : "+emission
        lines += ["PrincipledMaterial { id: mat"+str(i), "objectName: "+json.dumps(name), "baseColor: "+color,
                  "metalness: "+number(pbr.get("metallicFactor", 1)),
                  "roughness: "+("root.opticsProfile===\"abyss\" ? .045 : " if liquid else "")+number(pbr.get("roughnessFactor", 1)),
                  "clearcoatAmount: "+("root.opticsProfile===\"abyss\" ? .75 : " if liquid or limb else "")+number(extensions.get("KHR_materials_clearcoat", {}).get("clearcoatFactor", 0)),
                  "clearcoatRoughnessAmount: .08",
                  "transmissionFactor: "+("root.opticsProfile===\"abyss\" ? .3 : " if liquid else "")+number(transmission),
                  "thicknessFactor: "+("root.opticsProfile===\"abyss\" ? 8 : 0" if liquid else "0"),
                  "attenuationDistance: 60", "attenuationColor: root.theme",
                  "indexOfRefraction: "+number(extensions.get("KHR_materials_ior", {}).get("ior", 1.5)),
                  "emissiveFactor: "+emission, "}"]
    lines += ['''PrincipledMaterial {
    id:matCore;objectName:"Staged inner core"
    baseColor:Qt.rgba(root.theme.r*.8,root.theme.g*.8,root.theme.b*.8,1)
    emissiveFactor:Qt.vector3d(root.theme.r*.8,root.theme.g*.8,root.theme.b*.8)
    roughness:.16;metalness:0;clearcoatAmount:.25
}''']
    parents = {}
    for i, node in enumerate(base.g["nodes"]):
        for child in node.get("children", []):
            if child in parents:
                raise ValueError("multiple object parents")
            parents[child] = i
    def node_lines(index, ancestors=()):
        if index in ancestors:
            raise ValueError("cyclic object parents")
        node = base.g["nodes"][index]
        if "matrix" in node:
            raise ValueError("unexpected matrix transform")
        result = ["Node { id: n"+str(index), "objectName: "+json.dumps(names[index]),
                  "property vector3d rawPosition: "+vector(node.get("translation", [0,0,0])),
                  "property vector3d rawScale: "+vector(node.get("scale", [1,1,1])),
                  "property quaternion rawRotation: "+vector(node.get("rotation", [0,0,0,1]), True),
                  "position: root.blendedVector("+str(index)+",\"position\",rawPosition)",
                  "scale: root.blendedVector("+str(index)+",\"scale\",rawScale)",
                  "rotation: root.blendedRotation("+str(index)+",rawRotation)"]
        if names[index] == "Laptop root":
            result.append("visible: root.propVisible")
        if "mesh" in node:
            mesh_index = node["mesh"]
            mesh = geometry[mesh_index]
            targets = mesh["targets"]
            for j in range(len(targets)):
                value = node.get("weights", base.g["meshes"][mesh_index].get("weights", [0]*len(targets)))[j]
                result.append("property real w"+str(j)+": "+number(value))
            weights = "["+",".join("root.blendedWeight("+str(index)+","+str(j)+",n"+str(index)+".w"+str(j)+")" for j in range(len(targets)))+"]"
            result += ["readonly property var morphWeights: "+weights]
            if names[index] in ("Tentacle 1", "Tentacle 2"):
                target_names = base.g["meshes"][mesh_index]["extras"]["targetNames"]
                tap = targets[target_names.index("LaptopTap")]["POSITION"]
                endpoint = max(range(len(tap)), key=lambda j: abs(tap[j][1]))
                result += ["readonly property vector3d tapTip: n"+str(index)+".mapPositionToScene(geo"+str(index)+".positions["+str(endpoint)+"])"]
            result += ["Model {", "objectName: "+json.dumps(names[index]+" mesh"), "materials: [mat"+str(mesh["material"])+"]",
                       "geometry: ProceduralMesh { id: geo"+str(index), "property var data: Data.meshes["+str(mesh_index)+"]",
                       "indexes: data.indexes"]
            if targets:
                result += ["positions: Data.morph(data.positions,data.targets,"+weights+",\"POSITION\",false)",
                           "normals: Data.morph(data.normals,data.targets,"+weights+",\"NORMAL\",true)"]
            else:
                result += ["positions: Data.vectors(data.positions)", "normals: Data.vectors(data.normals)"]
            result += ["}", "}"]
            if names[index] in ("Liquid body","Octo liquid head"):
                result += ['Model { id:core'+str(index)+'''
                    objectName:"Staged liquid core volume"
                    visible:root.opticsProfile==="abyss"
                    scale:Qt.vector3d(.90,.74,.84);y:-2.5
                    materials:[matCore];geometry:geo'''+str(index)+"\n}"]
        for child in node.get("children", []):
            result += node_lines(child, (*ancestors,index))
        return result+["}"]
    for i in range(len(names)):
        if i not in parents:
            lines += node_lines(i)
    keyframes = 0
    for clip, asset in assets.items():
        animation = asset.g["animations"][0]
        step_bindings = []
        duration = receipt["clips"][clip]["duration"]
        # Blender frame 1 is 1/60 s in glTF. Shift the common scene origin,
        # preserving the complete verified interval and all relative timings.
        origin = asset.read(animation["samplers"][0]["input"])[0][0]
        lines += ["Timeline {", "enabled: root.active && root.clip==="+json.dumps(clip),
                  "startFrame: 0", "endFrame: "+str(duration), "currentFrame: root.phase*"+str(duration)]
        for channel in animation["channels"]:
            sampler = animation["samplers"][channel["sampler"]]
            interpolation = sampler.get("interpolation", "LINEAR")
            if interpolation not in ("LINEAR", "STEP"):
                raise ValueError("unsupported interpolation")
            times = [(r[0]-origin)*1000 for r in asset.read(sampler["input"])]
            if abs(times[0]) > .001 or abs(times[-1]-duration) > .01 or any(b<=a for a,b in zip(times,times[1:])):
                raise ValueError("invalid performance times")
            node_index = channel["target"]["node"]
            path = channel["target"]["path"]
            values = asset.read(sampler["output"])
            if path == "weights":
                count = len(geometry[asset.g["nodes"][node_index]["mesh"]]["targets"])
                if len(values) != len(times)*count:
                    raise ValueError("invalid morph key count")
                tracks = [("w"+str(j), [number(values[i*count+j][0]) for i in range(len(times))]) for j in range(count)]
            else:
                if len(values) != len(times):
                    raise ValueError("invalid transform key count")
                tracks = [({"translation":"rawPosition","rotation":"rawRotation","scale":"rawScale"}[path],
                           [vector(v,path=="rotation") for v in values])]
            for property_name, keys in tracks:
                if interpolation == "STEP":
                    # Blender optimizes static tracks to STEP, sometimes with
                    # distinct Float32 endpoints. Preserve that interpolation;
                    # never turn a tiny difference into a pixel tolerance.
                    step_bindings += ["Binding { target: n"+str(node_index), "property: "+json.dumps(property_name),
                              "when: root.active && root.clip==="+json.dumps(clip),
                              "restoreMode: Binding.RestoreNone",
                              "value: root.step(["+",".join(map(number,times))+"],["+",".join(keys)+"],root.phase*"+str(duration)+")", "}"]
                    keyframes += len(keys)
                    continue
                lines += ["KeyframeGroup { target: n"+str(node_index), "property: "+json.dumps(property_name)]
                for t, value in zip(times, keys):
                    lines.append("Keyframe { frame: "+number(t)+"; value: "+value+" }")
                    keyframes += 1
                lines += ["}"]
        lines += ["}"]
        lines += step_bindings
    lines += ["}"]
    component = output / (character.title()+"Cowork.qml")
    component.write_text("\n".join(lines)+"\n")
    return {"nodes":len(names),"meshes":len(geometry),"vertices":sum(len(m["positions"]) for m in geometry),
            "keyframes":keyframes,"clips":len(assets),"qmlSha256":hashlib.sha256(component.read_bytes()).hexdigest()}


def convert(bundle, output):
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    receipt = {character: qml_component(character, bundle/character, output) for character in ("aqua","octo")}
    (output / "native.json").write_text(json.dumps(receipt,indent=2)+"\n")
    return receipt


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print("COMPANION_NATIVE_CONVERT_PASS "+json.dumps(convert(args.bundle.resolve(),args.output.resolve())))
