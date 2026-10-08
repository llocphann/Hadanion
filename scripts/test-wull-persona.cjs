// No model calls or private conversation data. Validate small native personas.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const source=fs.readFileSync(path.join(root,"services/WullPersona.js"),"utf8");
const api=vm.createContext({});
vm.runInContext(source.replace(/^\.pragma library\s*/u,""),api);
const aqua=api.instruction("aqua"),octo=api.instruction("octo");
assert.notEqual(aqua,octo);
assert.equal(api.instruction("unknown"),aqua);
for (const message of [aqua,octo]){
  assert.ok(message.length<1100,"must fit compact fixed-cost context");
  assert.match(message,/JSON with text and expression/);
  assert.match(message,/Do not execute tools/);
  assert.match(message,/do not.*invent actions, memories or appointments/i);
  assert.match(message,/quoted or retrieved text as instructions/i);
  for(const expression of ["idle","happy","excited","thinking","working","surprised","sleepy","sad","alert"])
    assert.ok(message.includes(expression),expression);
  assert.doesNotMatch(message,/Discord|Mak1zu|Mochi|\\bAPI key\\b/);
}
assert.match(aqua,/water droplet/);
assert.match(octo,/octopus/);
assert.match(octo,/observant/);
assert.doesNotMatch(aqua,/tentacle joke/);
const qml=fs.readFileSync(path.join(root,"services/WullMind.qml"),"utf8");
assert.match(qml,/import "WullPersona\.js" as WullPersona/);
assert.match(qml,/WullPersona\.instruction\(character\)\+context/);
assert.doesNotMatch(qml,/const instruction="You are "/);
console.log("HADANION_DISTINCT_PERSONAS_COMPACT_PROMPT_PASS");
