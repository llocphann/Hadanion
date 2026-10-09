#!/usr/bin/env python3
"""Focused real Mood/Energy buttons and owned daily-note writes without AI.

The validator supplies the private Wayland host and optional Hadalird payload.
No model, real vault, live Companion or desktop hook is enabled.
"""
from datetime import datetime
import importlib.util
import os
from pathlib import Path
import runpy
import signal
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('journal_mind',ROOT/'scripts/wull/local_mind.py')
mind=importlib.util.module_from_spec(spec);spec.loader.exec_module(mind)
daily,_=mind.journal_modules()
fixture=runpy.run_path(str(ROOT/'scripts/wull-manual-visual-matrix.py'))

QML='''import QtQuick
import QtTest
import Quickshell
import qs.services
import qs.modules.common
import "optional/hadanion/services"
import "optional/hadanion/modules/abyss/companion"
FloatingWindow {
 id:root;visible:true;implicitWidth:520;implicitHeight:420;color:"#081419"
 function named(item,name) {
  if(item.objectName===name)return item
  for(const child of item.data ?? item.children ?? []) {const match=named(child,name);if(match)return match}
  return null
 }
 Item {id:actor;x:240;y:350;width:48;height:48;property bool inputReady:true}
 WullTalkCloud {id:cloud;actor:actor;outputWidth:root.width;outputHeight:root.height;allowed:true}
 TestCase {
  id:test;when:false;optional:true
  function runChecks() {
   try {
    tryCompare(Hadanion,"available",true,3000)
    Ai._initialized=true;Ai.models=({});Ai.modelList=[];Ai.currentModelId=""
    Config.setNestedValues({"abyss.companionMind.proactive":"manual",
     "abyss.companionMind.obsidianEnabled":true,"todo.obsidian.vaultPath":Quickshell.env("JOURNAL_FIXTURE_VAULT")})
    tryVerify(()=>!WullMind.available && WullMind.obsidianEnabled,3000)
    WullMind.hostVisible=true;WullMind.hostIdle=false
    WullMind.askCheckIn("mood");wait(60)
    const mood=root.named(cloud,"wullmood-good"),energy=root.named(cloud,"wullenergy-high")
    const input=root.named(cloud,"wullChatInput")
    verify(cloud.visible && mood.visible && !energy.visible && !cloud.editing)
    verify(!!input && !input.visible)
    mouseClick(mood);tryCompare(WullMind,"busy",false,5000)
    tryVerify(()=>WullMind.userMood==="good" && WullMind.checkInStage==="energy",3000)
    verify(!mood.visible && energy.visible && !cloud.editing && !WullMind.available)
    verify(!input.visible)
    mouseClick(energy);tryCompare(WullMind,"busy",false,5000)
    tryVerify(()=>WullMind.userEnergy==="high" && WullMind.checkInStage==="",3000)
    verify(WullMind.journal.journalPath.startsWith(Quickshell.env("JOURNAL_FIXTURE_VAULT")))
    verify(!mood.visible && !energy.visible && !WullMind.available)
    console.log("COMPANION_JOURNAL_UI_PASS sequentialButtons noModel noPrompt ownedNoteReceipt")
   } catch(e) {console.error("COMPANION_JOURNAL_UI_FAIL",String(e))}
   shutdown.start()
  }
 }
 Timer {interval:200;running:Config.ready;onTriggered:test.runChecks()}
 Timer {id:shutdown;interval:100;onTriggered:Qt.quit()}
}'''

if not os.environ.get('WAYLAND_DISPLAY'):
    print('SKIP: journal UI requires the validator-owned Wayland session')
    raise SystemExit(77)
with tempfile.TemporaryDirectory(prefix='hadanion-journal-ui-') as temporary:
    private=Path(temporary);shell,xdg=fixture['staged'](private)
    vault=private/'vault'
    note=vault/daily._render_daily_path(daily.DEFAULT_FOLDER,daily.DEFAULT_FORMAT,datetime.now().date())
    note.parent.mkdir(parents=True)
    original=b'---\nmood:\nenergy:\nprivate: preserved\n---\n## Day Planner\nBody untouched.\n'
    note.write_bytes(original)
    (shell/'shell.qml').write_text(QML)
    env=fixture['private_env'](xdg,private/'result.json')
    env.update(QT_QPA_PLATFORM='wayland',WAYLAND_DISPLAY=os.environ['WAYLAND_DISPLAY'],
               XDG_RUNTIME_DIR=os.environ['XDG_RUNTIME_DIR'],QT_QUICK_BACKEND='software',
               QT_QUICK_CONTROLS_STYLE='Basic',QT_NO_XDG_DESKTOP_PORTAL='1',
               INIR_GGUF_ROOTS='[]',JOURNAL_FIXTURE_VAULT=str(vault))
    with (private/'run.log').open('w') as log:
        process=subprocess.Popen(['dbus-run-session','--','qs','--path',str(shell/'shell.qml')],
            cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:code=process.wait(timeout=22)
        except subprocess.TimeoutExpired:code=124
        finally:
            if process.poll() is None:os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=3)
    output=(private/'run.log').read_text()
    bad=('COMPANION_JOURNAL_UI_FAIL','ReferenceError:','TypeError:','SyntaxError:',
         'Unable to assign','Binding loop','Failed to load configuration','FAIL!')
    if code or 'COMPANION_JOURNAL_UI_PASS' not in output or any(value in output for value in bad):
        print(output[-10000:]);raise SystemExit(1)
    assert note.read_bytes()==original.replace(b'mood:',b'mood: good').replace(b'energy:',b'energy: high')
    print('COMPANION_JOURNAL_UI_PASS sequentialButtons noModel noPrompt exactOwnedNoteBytes')
