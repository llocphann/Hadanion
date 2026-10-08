#!/usr/bin/env python3
"""Pure offline guards for source-pinned Hadanion dual-QSB visual comparison."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
tool = ROOT / "scripts/wull-shader-ab.py"
spec = importlib.util.spec_from_file_location("shader_ab", tool)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

assert len(module.cases()) >= 10
assert {"aqua_faceplant", "octo_head", "cornea", "foot", "aqua_theme_shift"} <= {
    state["name"] for state in module.cases()
}
assert module.QML.count('fragmentShader: Qt.resolvedUrl(') == 2
assert '"baseline/WaterDropletMaterial.frag.qsb"' in module.QML
assert '"candidate/WaterDropletMaterial.frag.qsb"' in module.QML
assert 'Math.min(currentIndex, cases.length - 1)' in module.QML
original = module.NEGATIVE_TARGET
altered = module.negative_variant(original)
assert original != altered and module.NEGATIVE_REPLACEMENT in altered
for source in ("", original + original):
    try:
        module.negative_variant(source)
    except RuntimeError:
        pass
    else:
        raise AssertionError("non-unique negative control must fail closed")

assert module.classify("self", [{"changed_pixels": 0}]) == ("PASS_SAME_SOURCE", 0)
assert module.classify("self", [{"changed_pixels": 1}]) == ("INCONCLUSIVE_SELF_CONTROL", 2)
assert module.classify("negative", [{"changed_pixels": 1}]) == ("PASS_DIFFERENCE_DETECTED", 0)
assert module.classify("negative", [{"changed_pixels": 0}]) == ("FAIL_NEGATIVE_UNDETECTED", 3)
assert module.classify("compare", [{"changed_pixels": 0}]) == ("PASS_PIXEL_EQUAL", 0)
assert module.classify("compare", [{"changed_pixels": 5}]) == ("FAIL_PIXEL_DIFFERENCE", 1)
control = dict(status="PASS_SAME_SOURCE", mode="self",
               baseline_source_sha256="baseline-source",
               baseline_qsb_sha256="baseline-qsb", qsb_version="qsb version",
               graphics=dict(backend="opengl"))
assert module.qualified_control(control, "baseline-source", "baseline-qsb",
                                "qsb version", dict(backend="opengl"))
for changed in (dict(control, status="INCONCLUSIVE_SELF_CONTROL"),
                dict(control, baseline_qsb_sha256="other"),
                dict(control, graphics=dict(backend="vulkan"))):
    assert not module.qualified_control(changed, "baseline-source", "baseline-qsb",
                                        "qsb version", dict(backend="opengl"))

# Invalid/unsupported commands may not allocate evidence directories.
with tempfile.TemporaryDirectory() as root:
    folder = Path(root) / "never-created"
    run = subprocess.run([sys.executable, str(tool), "--mode", "compare",
                          "--output", str(folder)], capture_output=True, text=True)
    assert run.returncode != 0 and "requires" in run.stderr and not folder.exists()
    run = subprocess.run([sys.executable, str(tool), "--mode", "self",
                          "--control-report", str(Path(root) / "forged.json"),
                          "--output", str(folder)], capture_output=True, text=True)
    assert run.returncode != 0 and not folder.exists()

print("HADANION_SHADER_AB_OFFLINE_CONTRACT_PASS")
