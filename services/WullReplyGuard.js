.pragma library

// Pure, bounded public-output adapter for shared-AI Companion replies.
// No tools, permissions, disk access, model retries or side effects.
// Original Hadanion code; no Mak1zu implementation imported.
var expressions = ["idle", "happy", "excited", "thinking", "working",
                   "surprised", "sleepy", "sad", "alert"]
var internalTag = /<\/?\s*(think(?:ing)?|tool_call|tool_result|function_call|system|assistant)\b/i
var protocolToken = /<\|(?:im_start|im_end|assistant|system|tool)[^>]*\|>|\[\s*\/?\s*INST\s*\]/i
var controlBytes = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g

function normalizeText(text, expression) {
    if (typeof text !== "string") return {ok:false,reason:"invalid_text"}
    if (internalTag.test(text) || protocolToken.test(text))
        return {ok:false,reason:"internal_protocol"}
    const value = text.replace(controlBytes,"").trim().slice(0,420)
    if (!value) return {ok:false,reason:"empty_text"}
    const semantic = expressions.indexOf(expression) >= 0 ? expression : "idle"
    return {ok:true,text:value,expression:semantic}
}

function parse(raw) {
    if (typeof raw !== "string" || raw.length > 32768)
        return {ok:false,reason:"invalid_envelope"}
    const cleaned = raw.trim().replace(/^\x60{3}(?:json)?\s*|\s*\x60{3}$/g,"")
    let parsed
    try { parsed=JSON.parse(cleaned) } catch(e) {
        // Never echo a malformed structured JSON/tool envelope as a user reply.
        if (/^[\[{]/.test(cleaned))
            return {ok:false,reason:"malformed_structured_output"}
        // Keep the pre-existing plain-text fallback for real plain prose.
        return normalizeText(cleaned,"idle")
    }
    if (parsed===null || typeof parsed !== "object" || Array.isArray(parsed)
            || Object.keys(parsed).some(key=>key!=="text" && key!=="expression"))
        return {ok:false,reason:"invalid_response_object"}
    return normalizeText(parsed.text, parsed.expression)
}
