import QtQuick
import QtQuick3D
import QtQuick3D.Helpers

// Original dormant surface study. The caller owns phase and supporting rim.
Node {
    id: root
    property bool enabled: false
    property bool reflectionsEnabled: false
    property real phase: 0
    property color theme: "#36d3f3"
    property vector3d eyePosition:Qt.vector3d(50,76,220)
    visible: enabled
    y: -.6
    readonly property alias floor: floor
    readonly property alias waterMaterial: waterMaterial
    readonly property alias probe: probe
    readonly property var ripples: [ripple0,ripple1,ripple2]
    // Fixed radial geometry; phase never rebuilds vertices or creates a timer.
    readonly property var disc: makeDisc()
    function makeDisc() {
        const positions=[Qt.vector3d(0,0,0)],normals=[Qt.vector3d(0,1,0)],
              colors=[Qt.vector4d(1,1,1,1)],indexes=[]
        const radii=[25,38,50,60,64,68],alphas=[1,1,.85,.3,.12,0],segments=128
        for(let ring=0;ring<radii.length;ring++) {
            for(let s=0;s<=segments;s++) {
                const angle=2*Math.PI*s/segments
                positions.push(Qt.vector3d(radii[ring]*Math.cos(angle),0,radii[ring]*Math.sin(angle)))
                normals.push(Qt.vector3d(0,1,0));colors.push(Qt.vector4d(1,1,1,alphas[ring]))
            }
            const start=1+ring*(segments+1)
            for(let s=0;s<segments;s++) {
                if(ring===0) indexes.push(0,start+s+1,start+s)
                else {
                    const inner=start-segments-1
                    indexes.push(inner+s,start+s+1,start+s,inner+s,inner+s+1,start+s+1)
                }
            }
        }
        return {positions,normals,colors,indexes}
    }
    function wave(offset) {
        const p=Number.isFinite(phase)?Math.max(0,Math.min(1,phase)):0
        return (p+offset)%1
    }
    function capture() {if(enabled&&reflectionsEnabled)probe.scheduleUpdate()}
    function mirroredEye() {
        const n=up.normalized(),d=eyePosition.minus(scenePosition)
        return eyePosition.minus(n.times(2*(d.x*n.x+d.y*n.y+d.z*n.z)))
    }
    ReflectionProbe {
        id:probe
        visible:root.reflectionsEnabled
        position: {
            const p=root.scenePosition,r=root.sceneRotation
            return root.mapPositionFromScene(root.mirroredEye())
        }
        boxSize:Qt.vector3d(140*Math.abs(root.up.y)+4*Math.abs(root.up.x),
                            140*Math.abs(root.up.x)+4*Math.abs(root.up.y),115)
        boxOffset:root.scenePosition.minus(probe.scenePosition)
        parallaxCorrection:false
        quality:ReflectionProbe.Medium
        refreshMode:ReflectionProbe.FirstFrame
        timeSlicing:ReflectionProbe.None
        clearColor:Qt.rgba(root.theme.r*.025,root.theme.g*.025,root.theme.b*.025,1)
    }
    PrincipledMaterial {
        id: waterMaterial
        baseColor:Qt.rgba(root.theme.r*.10,root.theme.g*.10,root.theme.b*.10,1)
        metalness:.15;roughness:.08
        specularAmount:.8;clearcoatAmount:1;clearcoatRoughnessAmount:.04
        alphaMode:PrincipledMaterial.Blend
        vertexColorsEnabled:true
        cullMode:Material.NoCulling
    }
    PrincipledMaterial {
        id: waveMaterial
        baseColor:root.theme
        emissiveFactor:Qt.vector3d(root.theme.r*1.5,root.theme.g*1.5,root.theme.b*1.5)
        metalness:.12;roughness:.2
    }
    Model {
        id: floor
        geometry:ProceduralMesh {
            positions:root.disc.positions;normals:root.disc.normals
            colors:root.disc.colors;indexes:root.disc.indexes
        }
        scale:Qt.vector3d(1,1,.82)
        materials:[waterMaterial]
        castsShadows:false
        castsReflections:false
        receivesReflections:true
    }
    TorusGeometry {id: waveGeometry;radius:1;tubeRadius:.008;rings:96;segments:8;asynchronous:false}
    component Ripple: Model {
        property real offset: 0
        readonly property real progress:root.wave(offset)
        readonly property real radius:28+38*progress
        scale:Qt.vector3d(radius,radius*.6,radius*.82)
        opacity:(1-progress)*.6
        y:.24
        geometry:waveGeometry
        materials:[waveMaterial]
        castsShadows:false
        castsReflections:false
        receivesReflections:false
    }
    Ripple {id:ripple0;offset:0}
    Ripple {id:ripple1;offset:.24}
    Ripple {id:ripple2;offset:.48}
}
