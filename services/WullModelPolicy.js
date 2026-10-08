.pragma library

// Companion policy only; catalog and inference transport remain Hadalis-owned.
function isLocal(model) {
    if (!model || model.local !== true) return false
    if (model.api_format === "gguf")
        return typeof model.gguf_path === "string" && model.gguf_path.startsWith("/")
    if (!["openai", "openai-responses"].includes(model.api_format)) return false
    const match = /^https?:\/\/([^/?#\s\\]+)(?:[/?#]|$)/i.exec(String(model.endpoint ?? ""))
    if (!match) return false
    const authority = /^(localhost|127\.\d{1,3}\.\d{1,3}\.\d{1,3}|\[::1\])(?::(\d{1,5}))?$/i.exec(match[1])
    if (!authority || (authority[2] && (Number(authority[2]) < 1 || Number(authority[2]) > 65535))) return false
    return !authority[1].startsWith("127.") || authority[1].split(".").every(part => Number(part) <= 255 && String(Number(part)) === part)
}

function allowed(model, localOnly) { return !!model && (!localOnly || isLocal(model)) }
