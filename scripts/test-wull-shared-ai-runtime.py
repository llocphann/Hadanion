#!/usr/bin/env python3
"""Wull uses the real Ai service with a private loopback protocol fixture."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, os, shutil, sqlite3, subprocess, tempfile, threading, time
from native_test_session import private_wayland, run_qs

ROOT=Path(__file__).resolve().parents[1]
if not shutil.which("qs"):
    print("SKIP: Wull shared AI runtime requires Quickshell")
    raise SystemExit(0)
requests=[]
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_POST(self):
        data=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        requests.append((self.path,data,dict(self.headers)))
        if self.path=="/slow":time.sleep(.7)
        failure=self.path=="/failure"
        self.send_response(429 if failure else 200)
        self.send_header("Content-Type","text/event-stream");self.end_headers()
        content={
            '/extra':json.dumps({'text':'Not public','tool_calls':[{'name':'open_file'}]}),
            '/tokens':json.dumps({'text':'<|channel|>analysis secret','expression':'happy'}),
            '/malformed':'{"text":"unfinished"',
        }.get(self.path,json.dumps({'text':'Fixture hello','expression':'happy'}))
        payload={"error":{"message":"fixture rate limit"}} if failure else {
            "choices":[{"delta":{"content":content},"finish_reason":"stop"}]}
        try:self.wfile.write(("data: "+json.dumps(payload)+"\n\ndata: [DONE]\n\n").encode())
        except (BrokenPipeError,ConnectionResetError):pass

server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with tempfile.TemporaryDirectory(prefix="hadalis-wull-ai-") as name:
    folder=Path(name)
    for entry in ["modules","services","GlobalStates.qml","qmldir","assets","scripts","defaults","translations","optional"]:
        (folder/entry).symlink_to(ROOT/entry)
    config=folder/"config/illogical-impulse";config.mkdir(parents=True)
    shutil.copy(ROOT/"defaults/config.json",config/"config.json")
    (folder/"shell.qml").write_text(r'''
pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import qs.modules.common
import qs.services
import "optional/hadanion/services"
import qs.services.deferred
ShellRoot {
 id:root
 property var optionalHost:Hadanion
 Component.onCompleted: Quickshell.watchFiles=false
 property int step:0
 property int ticks:0
 property var mainIDs:[]
 property var invalidModels:["fixture-extra","fixture-tokens","fixture-malformed"]
 property int invalidIndex:0
 property string previousText:""
 property int assistantCount:0
 function check(ok,message): bool {
  if(ok)return true
  console.error("WULL_SHARED_AI_FAIL",message);Qt.quit();return false
 }
 function add(id,path): void {
  Ai.addModel(id,{name:id,model:id,endpoint:Quickshell.env("AI_FIXTURE_URL")+path,
   local:true,requires_key:false,provider_id:"fixture",api_format:"openai",
   capabilities:{chat:"supported",reasoning:"supported"}})
 }
 FloatingWindow {visible:true;implicitWidth:360;implicitHeight:180;color:"#111820"}
 Timer {
  interval:100;running:true;repeat:true
  onTriggered:{
   if(++root.ticks>160){root.check(false,"requests did not settle");return}
   if(!Config.ready || !Hadanion.available)return
   if(root.step===0){
    Ai._initialized=true
    const originalPrompt=Config.options.ai.systemPrompt
    const substitutions=Ai.promptSubstitutions
    Config.setNestedValue("ai.systemPrompt","{DISTRO}/{DISTRO}|{DATETIME}|{WINDOWCLASS}|{DE}|$& literal")
    if(!root.check(Ai.systemPrompt===substitutions["{DISTRO}"]+"/"+substitutions["{DISTRO}"]+"|"+substitutions["{DATETIME}"]+"|"+substitutions["{WINDOWCLASS}"]+"|"+substitutions["{DE}"]+"|$& literal","live repeated context substitutions preserve literal text"))return
    Config.setNestedValue("ai.systemPrompt","")
    if(!root.check(Ai.systemPrompt==="","clearing the AI prompt leaves an empty typed prompt"))return
    Config.setNestedValue("ai.systemPrompt",originalPrompt)
    KeyringStorage.keyringData=({apiKeys:{fixture:"fixture-credential"}});KeyringStorage.loaded=true
    root.add("fixture-main","/ok");root.add("fixture-wull","/ok")
    root.add("fixture-failure","/failure");root.add("fixture-slow","/slow")
    root.add("fixture-extra","/extra");root.add("fixture-tokens","/tokens");root.add("fixture-malformed","/malformed")
    root.add("fixture-cloud","/cloud");Ai.models["fixture-cloud"].local=false
    root.add("fixture-spoof","/spoof");Ai.models["fixture-spoof"].endpoint="http://localhost@cloud.invalid/v1"
    Ai.modelList=Object.keys(Ai.models)
    Ai.models["fixture-wull"].requires_key=true
    Ai.models["fixture-wull"].key_id="fixture";Ai.models["fixture-wull"].auth_scheme="bearer"
    Ai.currentModelId="fixture-main";Ai.addMessage("Ordinary AI history","user")
    root.mainIDs=Ai.messageIDs.slice()
    if(!root.check(WullMind.localOnly && !WullMind.selectableModels.some(entry=>["fixture-cloud","fixture-spoof"].includes(entry.name)),"local default lists a remote/spoofed model"))return
    for(const id of ["fixture-cloud","fixture-spoof"]){
     Config.setNestedValue("abyss.companionMind.model",id)
     if(!root.check(!WullMind.available && !WullMind.sendMessage("Never send this fixture"),"local-only request accepted a cloud or spoofed model"))return
    }
    Config.setNestedValue("abyss.companionMind.model","")
    Ai.currentModelId="fixture-cloud"
    if(!root.check(WullMind.model!=="fixture-cloud" && WullMind.available && Ai.currentModelId==="fixture-cloud","automatic local selection modified the main AI model or fell back to cloud"))return
    Ai.currentModelId="fixture-main"
    Config.setNestedValues({"abyss.companionMind.model":"fixture-wull",
     "abyss.companionMind.endpoint":"http://127.0.0.1:1",
     "abyss.companionMind.thinkingEffort":"high"})
    WullMind.historyLoaded=true;WullMind.openChat()
    if(!root.check(WullMind.selectableModels.some(entry=>entry.name==="fixture-wull"),"Wull exposes the AI catalog"))return
    if(!root.check(WullMind.sendMessage("Hello fixture"),"shared request accepted"))return
    root.step++
   }else if(root.step===1 && !WullMind.busy){
    if(!root.check(WullMind.history[WullMind.history.length-1]?.content==="Fixture hello"
        && WullMind.history[WullMind.history.length-1]?.persisted,"shared reply is rendered and persisted"))return
    if(!root.check(Ai.currentModelId==="fixture-main" && JSON.stringify(Ai.messageIDs)===JSON.stringify(root.mainIDs)
        && Ai.messageByID[root.mainIDs[0]].rawContent==="Ordinary AI history", "main AI conversation/model stay intact"))return
    Config.setNestedValue("abyss.companionMind.model","fixture-failure")
    if(!root.check(WullMind.sendMessage("Fail fixture"),"failure request accepted"))return
    root.step++
   }else if(root.step===2 && !WullMind.busy){
    if(!root.check(WullMind.connectionStatus==="error" && WullMind.errorMessage.includes("429"),"HTTP errors do not become successful replies"))return
    Config.setNestedValue("abyss.companionMind.model","fixture-slow")
    if(!root.check(WullMind.sendMessage("Cancel fixture"),"cancellable request accepted"))return
    root.step++
   }else if(root.step===3){WullMind.cancel();root.step++
   }else if(root.step===4 && !WullMind.aiSession.busy){
    if(!root.check(!WullMind.history.some(entry=>entry.content==="Cancel fixture"),"cancelled pending message is released"))return
    Config.setNestedValue("abyss.companionMind.model","")
    if(!root.check(WullMind.model===Ai.currentModelId,"empty override follows the AI tab model"))return
    if(!root.check(WullMind.sendMessage("Retry fixture"),"request works after cancellation"))return
    root.step++
   }else if(root.step===5 && !WullMind.busy){
    if(!root.check(WullMind.history[WullMind.history.length-1]?.content==="Fixture hello" && Ai.messageIDs.length===root.mainIDs.length,"retry preserves both conversations"))return
    root.previousText=WullMind.text
    root.assistantCount=WullMind.history.filter(entry=>entry.role==="assistant").length
    Config.setNestedValue("abyss.companionMind.model",root.invalidModels[0])
    if(!root.check(WullMind.sendMessage("Reject fixture 0"),"invalid-output request accepted"))return
    root.step=6
   }else if(root.step===6 && !WullMind.busy){
    if(!root.check(WullMind.connectionStatus==="error"
        && WullMind.history.filter(entry=>entry.role==="assistant").length===root.assistantCount
        && WullMind.text===root.previousText,"invalid model output was displayed or appended"))return
    if(++root.invalidIndex<root.invalidModels.length){
     Config.setNestedValue("abyss.companionMind.model",root.invalidModels[root.invalidIndex])
     if(!root.check(WullMind.sendMessage("Reject fixture "+root.invalidIndex),"next invalid-output request accepted"))return
    }else{
     Config.setNestedValue("abyss.companionMind.model","")
     if(!root.check(WullMind.sendMessage("Recovery fixture"),"valid request after rejected outputs"))return
     root.step=7
    }
   }else if(root.step===7 && !WullMind.busy){
    if(!root.check(WullMind.history[WullMind.history.length-1]?.content==="Fixture hello"
        && WullMind.history[WullMind.history.length-1]?.persisted
        && Ai.messageIDs.length===root.mainIDs.length,"rejected outputs prevented valid recovery"))return
    Config.setNestedValue("abyss.companionMind.localOnly",false)
    Config.setNestedValue("abyss.companionMind.model","fixture-cloud")
    if(!root.check(WullMind.selectableModels.some(entry=>entry.name==="fixture-cloud") && WullMind.sendMessage("Queued cloud fixture"),"explicit cloud opt-in is unavailable"))return
    Config.setNestedValue("abyss.companionMind.localOnly",true)
    if(!root.check(!WullMind.busy && !WullMind.aiSession.busy && !WullMind.history.some(entry=>entry.content==="Queued cloud fixture"),"revoking cloud opt-in did not cancel the queued request"))return
    Config.setNestedValue("abyss.companionMind.model","")
    console.info("WULL_SHARED_AI_PASS catalog request history-isolation persistence HTTP-error cancel retry model-follow output-rejection recovery localDefault cloudBlock spoofBlock localAutoFallback consentRevoke");Qt.quit()
   }
  }
 }
}
''')
    with private_wayland(folder) as env:
        if env is None:
            print("SKIP: Wull shared AI runtime requires a private Niri session")
            raise SystemExit(0)
        env["AI_FIXTURE_URL"]=f"http://127.0.0.1:{server.server_port}"
        env.update(http_proxy="http://127.0.0.1:1",HTTP_PROXY="http://127.0.0.1:1",
                   ALL_PROXY="http://127.0.0.1:1",all_proxy="http://127.0.0.1:1",NO_PROXY="",no_proxy="")
        result=run_qs(folder,env)
    output=result.stdout+result.stderr
    errors=["WULL_SHARED_AI_FAIL","ReferenceError:","TypeError:","Binding loop","Unable to assign","is not a type"]
    if result.returncode or "WULL_SHARED_AI_PASS" not in output or any(word in output for word in errors):
        print(output);raise SystemExit(1)
    for line in output.splitlines():
        if "WULL_SHARED_AI_PASS" in line:print(line)
    ok=[row for path,row,headers in requests if path=="/ok"]
    assert len(ok)==3 and ok[0]["reasoning_effort"]=="high"
    assert all("Ordinary AI history" not in json.dumps(row) and "tools" not in row for row in ok)
    headers=[headers for path,row,headers in requests if path=="/ok"]
    assert headers[0].get("Authorization")=="Bearer fixture-credential"
    assert "Authorization" not in headers[1], "previous provider credential survived a keyless switch"
    assert len([row for path,row,headers in requests if path in ('/extra','/tokens','/malformed')])==3
    assert not any(path in ('/cloud','/spoof') for path,row,headers in requests), 'blocked or revoked request reached transport'
    with sqlite3.connect(Path(env['XDG_STATE_HOME'])/'inir/wull/chat.sqlite3') as db:
        rows=db.execute('SELECT role,content FROM messages ORDER BY id').fetchall()
    assert rows==[('user','Hello fixture'),('assistant','Fixture hello'),
                  ('user','Retry fixture'),('assistant','Fixture hello'),
                  ('user','Recovery fixture'),('assistant','Fixture hello')], 'rejected output entered persistent history'
finally:
    server.shutdown();server.server_close()
