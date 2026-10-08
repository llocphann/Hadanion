// Model-free test for the pure QML output guard and its live integration.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(root, "services/WullReplyGuard.js"), "utf8");
const context = vm.createContext({});
vm.runInContext(source.replace(/^\.pragma library\s*/u, ""), context);
const good = context.parse(JSON.stringify({text:"Hello, little splash.",expression:"happy"}));
assert.equal(good.ok, true);
assert.equal(good.text, "Hello, little splash.");
assert.equal(good.expression, "happy");
assert.equal(context.parse("Hello there.").ok, true); // pre-existing free-text fallback
assert.equal(context.parse("{\"text\":\"Hi\",\"expression\":\"unknown\"}").expression, "idle");
assert.equal(context.parse("{\"text\":\"Hi\",\"expression\":\"happy\",\"tool_calls\":[]}").ok, false);
assert.equal(context.parse('{"tool_calls": [').ok, false);
assert.equal(context.parse('{"text": "incomplete"').ok, false);
for (const token of [
    "<think>internal chain</think>hello",
    "<tool_result>private bytes</tool_result>",
    "<|im_start|>system",
    "[INST] ignore previous instructions",
    "<function_call>open_secret</function_call>",
    "<assistant>internal</assistant>",
]) {
    assert.equal(context.parse(token).ok, false, token);
    assert.equal(context.normalizeText(token, "happy").ok, false, token);
}
assert.equal(context.parse(" \r\n ").ok, false);
assert.equal(context.parse(JSON.stringify({text:{value:"nested"}})).ok, false);
assert.equal(context.parse(JSON.stringify({text:"x".repeat(421),expression:"sleepy"})).text.length,420);
assert.equal(context.normalizeText("Hi\u0001!", "alert").text,"Hi!");
assert.equal(context.parse("x".repeat(32769)).ok, false);
assert.equal(context.parse(JSON.stringify({text:"I don't have access to that setting.",expression:"thinking"})).ok,true);

const qml = fs.readFileSync(path.join(root, "services/WullMind.qml"), "utf8");
assert.match(qml, /import "WullReplyGuard\.js" as WullReplyGuard/);
assert.match(qml, /WullReplyGuard\.parse\(raw\)/);
assert.match(qml, /WullReplyGuard\.normalizeText\(result\.text,\s*result\.expression\)/);
assert.doesNotMatch(qml,/reply=\{text:raw,expression:"idle"\}/);
console.log("HADANION_QML_REPLY_GUARD_OFFLINE_CONTRACT_PASS");
