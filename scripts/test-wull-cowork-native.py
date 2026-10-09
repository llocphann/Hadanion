#!/usr/bin/env python3
"""Owned native mesh/material/Timeline proof; no actual Companion or AI hooks.

--bundle is the output of companion-export-cowork-native.py. With no bundle,
test the bounded converter offline. Native captures use a new owned compositor,
fixed sampled poses and one Loader3D actor. They are not G0/G1 or input proof.
"""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cowork_native", ROOT / "scripts/companion-cowork-native.py")
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


def offline(folder):
    source = folder / "fixture.gltf"
    binary = source.with_suffix(".bin")
    binary.write_bytes(struct.pack("<9f", 0,0,0, 1,0,0, 0,1,0))
    value = {"asset":{"version":"2.0"},"buffers":[{"uri":binary.name,"byteLength":36}],
             "bufferViews":[{"buffer":0,"byteLength":36}],
             "accessors":[{"bufferView":0,"componentType":5126,"type":"VEC3","count":3}]}
    source.write_text(json.dumps(value))
    asset = converter.Asset(source)
    assert asset.read(0) == [[0,0,0],[1,0,0],[0,1,0]]
    for index in (-1,True,2):
        try: asset.read(index)
        except ValueError: pass
        else: raise AssertionError("invalid accessor index accepted")
    for mutation in ({"count":200001},{"count":True},{"byteOffset":32},{"byteOffset":-1}):
        broken = json.loads(json.dumps(value))
        broken["accessors"][0].update(mutation)
        source.write_text(json.dumps(broken))
        try: converter.Asset(source).read(0)
        except ValueError: pass
        else: raise AssertionError("invalid accessor accepted")
    for uri in ("../fixture.bin", "https://example.invalid/weights.bin", "file:///fixture.bin"):
        broken = json.loads(json.dumps(value))
        broken["buffers"][0]["uri"] = uri
        source.write_text(json.dumps(broken))
        try: converter.Asset(source)
        except ValueError: pass
        else: raise AssertionError("external buffer accepted")
    for invalid in (float("nan"),float("inf"),True):
        try: converter.number(invalid)
        except ValueError: pass
        else: raise AssertionError("invalid keyframe accepted")
    print("COMPANION_NATIVE_CONVERTER_PASS boundedBuffers finiteValues")


QML = '''import QtQuick
import QtQuick.Window
import QtQuick3D
import Quickshell
Window {
    id: root
    width: 420; height: 420; visible: true; color: "#061119"
    property var cases: CASES
    property int index: 0
    property var current: cases[index]
    property var proofs: []
    readonly property var actor: actorLoader.item
    function check(ok, why) { if(!ok) throw new Error(why) }
    function configure() {
        if(current.hidden) {settle.restart();return}
        if(!actor) return
        actor.clip=current.clip;actor.phase=current.phase
        actor.theme=current.theme;actor.propVisible=current.prop
        settle.restart()
    }
    function vector(p) {return [p.x,p.y,p.z]}
    function inspect() {
        if(current.hidden) {
            check(!actor,"disabled loader retained a model")
            proofs.push({name:current.name,character:current.character,hidden:true,actorCount:0})
            return
        }
        check(actor && actor.visible,"missing single actor")
        const prop=actor.named("Laptop root"),hinge=actor.named("Laptop hinge")
        check(prop.visible===current.prop,"prop lifecycle mismatch")
        const proof={name:current.name,character:current.character,clip:current.clip,phase:current.phase,
            rim:current.rim,theme:String(actor.theme),propVisible:prop.visible,
            materials:actor.materials.map(m=>({name:m.objectName,color:String(m.baseColor),alpha:m.baseColor.a,transmission:m.transmissionFactor})),
            hinge:vector(hinge.eulerRotation),lid:vector(actor.named("Laptop lid").scenePosition)}
        if(current.character==="aqua") {
            proof.left=vector(actor.named("Left water arm").scenePosition)
            proof.right=vector(actor.named("Right water arm").scenePosition)
        } else {
            const arm=actor.named("Tentacle 1")
            proof.weights=arm.morphWeights
            proof.tip=vector(arm.tapTip)
            proof.cup=vector(actor.named("Suction cup 1.4").scenePosition)
        }
        proofs.push(proof)
    }
    onCurrentChanged: configure()
    Item {
        id: canvas;width:420;height:420;anchors.centerIn:parent
        Rectangle {anchors.fill:parent;color:"#061119"}
        View3D {
            anchors.fill:parent
            environment: SceneEnvironment {
                backgroundMode: SceneEnvironment.Transparent
                lightProbe: Texture {source: STUDIO}
                probeExposure: 1
                antialiasingMode: SceneEnvironment.MSAA
                antialiasingQuality: SceneEnvironment.High
            }
            camera: camera
            OrthographicCamera {
                id:camera;position:Qt.vector3d(50,76,220)
                horizontalMagnification: 2.9;verticalMagnification:2.9
                Component.onCompleted:lookAt(Qt.vector3d(0,36,0))
            }
            DirectionalLight {eulerRotation:Qt.vector3d(-30,-35,0);brightness:1.8;color:"#e6f7ff"}
            DirectionalLight {eulerRotation:Qt.vector3d(-20,110,0);brightness:1.3;color:"#84c5ff"}
            DirectionalLight {eulerRotation:Qt.vector3d(30,180,0);brightness:1.6;color:"#c8eaff"}
            Node {
                position:Qt.vector3d(0,36,0)
                eulerRotation.z:root.current.rim
                Loader3D {
                    id:actorLoader;y:-36
                    active: !root.current.hidden
                    source: root.current.character==="aqua" ? "AquaCowork.qml" : "OctoCowork.qml"
                    onLoaded:root.configure()
                    onStatusChanged:if(status===Loader3D.Error) {
                        console.log("COMPANION_NATIVE_FAIL actor import");Qt.callLater(Qt.quit)
                    }
                }
            }
        }
    }
    Timer {
        id:settle;interval:root.current.video&&!root.current.firstFrame?35:350;repeat:false
        onTriggered: {
            try {
                root.inspect()
                const saved=root.current.name
                check(canvas.grabToImage(result=>{
                    if(!result.saveToFile(OUT+"/"+saved+".png")) {
                        console.log("COMPANION_NATIVE_FAIL save "+saved);Qt.quit();return
                    }
                    if(root.index+1===root.cases.length) {
                        console.log("COMPANION_NATIVE_PROOFS "+JSON.stringify(root.proofs))
                        console.log("COMPANION_NATIVE_CAPTURE_DONE")
                        Qt.quit()
                    } else {root.index++}
                }),"grab scheduling failed")
            } catch(error) {console.log("COMPANION_NATIVE_FAIL "+error);Qt.quit()}
        }
    }
}
'''


def native(bundle, output, host, video=False):
    output.mkdir(mode=0o700,parents=True,exist_ok=False)
    receipt = converter.convert(bundle,output/"qt")
    session_spec = importlib.util.spec_from_file_location("native_session",host/"scripts/native_test_session.py")
    session = importlib.util.module_from_spec(session_spec)
    session_spec.loader.exec_module(session)
    cases=[]
    clips=json.loads((bundle/"export.json").read_text())["characters"]["aqua"]["clips"]
    for character in ("aqua","octo"):
        for clip in clips:
            cases.append(dict(name=character+"-"+clip,character=character,clip=clip,phase=.5,rim=0,theme="#36d3f3",prop=True))
        for phase in (0,.12,.38,1):
            cases.append(dict(name=character+"-typing-"+str(phase),character=character,
                clip="laptop_typing_loop",phase=phase,rim=0,theme="#36d3f3",prop=True))
        for rim in (90,180,270):
            cases.append(dict(name=character+"-rim-"+str(rim),character=character,
                clip="laptop_typing_loop",phase=.12,rim=rim,theme="#36d3f3",prop=True))
        for theme,label in (("#ffb967","amber"),("#ae84ff","purple"),("#24dfba","green")):
            cases.append(dict(name=character+"-"+label,character=character,
                clip="laptop_typing_loop",phase=.12,rim=0,theme=theme,prop=True))
        cases.append(dict(name=character+"-closed",character=character,
            clip="laptop_close",phase=1,rim=0,theme="#36d3f3",prop=False))
        cases.append(dict(name=character+"-off",character=character,hidden=True,
            clip="laptop_close",phase=1,rim=0,theme="#36d3f3",prop=False))
    static_cases=list(cases)
    if video:
        if not shutil.which("ffmpeg"):
            raise SystemExit("ffmpeg is required for the optional review movie")
        for character in ("aqua","octo"):
            frame=0
            for clip,seconds in (("laptop_open",1.45),("laptop_typing_loop",1.8),
                    ("laptop_thinking_loop",1.6),("laptop_agent_loop",1.2),
                    ("laptop_pause",.6),("laptop_success",1.1),
                    ("laptop_alert",1.2),("laptop_close",1.2)):
                duration=clips[clip]["duration"]/1000
                for j in range(round(seconds*24)+1):
                    phase=min(j/24/duration,1)
                    visible=clip!="laptop_open" or phase>=.13
                    visible=visible and (clip!="laptop_close" or phase<.93)
                    cases.append(dict(name=character+"-video-"+format(frame,"04d"),
                        character=character,clip=clip,phase=phase,rim=0,theme="#36d3f3",prop=visible,
                        video=True,firstFrame=frame==0))
                    frame+=1
    frames=output/"frames";frames.mkdir()
    qml=QML.replace("CASES",json.dumps(cases)).replace("STUDIO",json.dumps(str(bundle/"studio.hdr")))
    qml=qml.replace("OUT",json.dumps(str(frames)))
    (output/"qt/shell.qml").write_text(qml)
    compositor=output/"compositor";compositor.mkdir()
    with session.private_wayland(compositor) as env:
        if env is None:
            raise SystemExit("SKIP: Native laptop proof requires owned Niri/Wayland")
        env.update(QT_QUICK_BACKEND="rhi",QSG_RHI_BACKEND="opengl",QT_QUICK_CONTROLS_STYLE="Basic",
                   QT_QPA_PLATFORMTHEME="generic",QT_NO_XDG_DESKTOP_PORTAL="1")
        result=session.run_qs(output/"qt",env,timeout=max(55,math.ceil(len(cases)*.14+12)))
    log=result.stdout
    if result.returncode or "COMPANION_NATIVE_CAPTURE_DONE" not in log or any(bad in log for bad in
        ("COMPANION_NATIVE_FAIL","ReferenceError:","TypeError:","Unable to assign","Binding loop")):
        raise SystemExit("Native laptop fixture failed: "+log[-7000:])
    proofs=json.loads(next(line.split("COMPANION_NATIVE_PROOFS ",1)[1] for line in log.splitlines()
                          if "COMPANION_NATIVE_PROOFS " in line))
    assert len(proofs)==len(cases)
    for proof in proofs:
        if proof.get("hidden"):
            assert proof["actorCount"]==0
            continue
        for material in proof["materials"]:
            if any(word in material["name"].lower() for word in ("liquid","theme accent","cyan iris","opaque glossy tentacles")):
                assert material["color"]==proof["theme"],"theme did not recolor all original volumes"
            if "opaque glossy tentacles" in material["name"].lower():
                assert material["alpha"]==1 and material["transmission"]==0,"Octo limb depth/opacity mismatch"
    for character in ("aqua","octo"):
        paired=[p for p in proofs if p["name"].startswith(character+"-typing-")]
        zero,tap,other,end=paired
        if character=="aqua":
            distance=lambda a,b:math.dist(a,b)
            assert distance(zero["left"],tap["left"])>2.5 and distance(zero["right"],tap["right"])<.05
            assert distance(zero["right"],other["right"])>2.5 and distance(zero["left"],other["left"])<.05
            assert distance(zero["left"],end["left"])<.01
        else:
            assert tap["weights"]!=zero["weights"] and math.dist(tap["tip"],zero["tip"])>2.5
            assert math.dist(tap["cup"],zero["cup"])>1.5
            assert math.dist(zero["cup"],end["cup"])<.01
        assert not next(p for p in proofs if p["name"]==character+"-closed")["propVisible"]
    for case in cases:
        data=(frames/(case["name"]+".png")).read_bytes()
        assert data.startswith(b"\x89PNG\r\n\x1a\n") and struct.unpack(">II",data[16:24])==(420,420)
        assert len(data)>(256 if case.get("hidden") else 1500)
    # File existence/size alone cannot prove Qt painted a real model. Inspect
    # only the fixed matrix, never choose/retry movie frames by their pixels.
    from PIL import Image
    painted = {}
    for case in static_cases:
        with Image.open(frames/(case["name"]+".png")) as image:
            pixels=image.convert("RGBA").tobytes()
        background=bytes((6,17,25,255))
        count=sum(pixels[i:i+4]!=background for i in range(0,len(pixels),4))
        assert count==0 if case.get("hidden") else count>3000,"empty or retained native model paint"
        painted[case["name"]]=count
    movies=[]
    if video:
        for character in ("aqua","octo"):
            path=output/(character+"-cowork.mp4")
            subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-framerate","24",
                "-i",str(frames/(character+"-video-%04d.png")),"-c:v","libx264","-crf","18",
                "-pix_fmt","yuv420p","-threads","2","-movflags","+faststart",str(path)],
                check=True,timeout=30)
            assert path.stat().st_size>5000
            movies.append(str(path))
    receipt.update(scope="Original staged mesh/material/Timeline only; not production, G0/G1 or input acceptance",
                   frames=len(cases),staticFrames=len(static_cases),paintedPixels=painted,
                   movies=movies,proofs=proofs,exitCode=result.returncode)
    (output/"result.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("COMPANION_NATIVE_QML_PASS "+str(len(cases))+" fixedFrames oneLoader pairedClips fourRims fourThemes propYield")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle",type=Path)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--video",action="store_true",help="also retain two short original 3D review movies")
    parser.add_argument("--hadalis-root",type=Path,default=Path(os.environ.get("HADALIS_ROOT",ROOT.parent/"Hadalis")))
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="hadanion-cowork-converter-") as temporary:
        offline(Path(temporary))
    if bool(args.bundle)!=bool(args.output):parser.error("--bundle and --output must be supplied together")
    if args.video and not args.bundle:parser.error("--video requires the owned --bundle and --output")
    if args.bundle:native(args.bundle.resolve(),args.output.resolve(),args.hadalis_root.resolve(),args.video)
