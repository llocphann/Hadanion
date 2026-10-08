const assert=require("node:assert/strict");
const fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const policy=vm.createContext({});
vm.runInContext(fs.readFileSync(path.join(__dirname,"../services/WullModelPolicy.js"),"utf8").replace(/^\.pragma library\s*/,""),policy);
const model=endpoint=>({local:true,api_format:"openai",endpoint});
for(const endpoint of ["http://localhost:11434/v1","http://127.0.0.1:8000/v1","http://127.4.5.6/v1","http://[::1]:1234/v1","https://LOCALHOST/v1"]) {
    assert.equal(policy.isLocal(model(endpoint)),true,endpoint);
}
for(const endpoint of ["https://example.com/v1","http://localhost.evil/v1","http://localhost@evil/v1", "http://user@localhost/v1",
                      "http://127.0.0.999/v1","http://127.0.0.1:0/v1","http://127.0.0.1:65536/v1","http://localhost\\@evil/v1",
                      "http://192.168.1.2/v1","http://[::ffff:192.168.1.2]/v1","file:///tmp/a","http://%6cocalhost/v1","http://127.00.0.08/v1"]) {
    assert.equal(policy.isLocal(model(endpoint)),false,endpoint);
}
assert.equal(policy.isLocal({...model("http://127.0.0.1"),local:false}),false);
assert.equal(policy.isLocal({local:true,api_format:"gguf",gguf_path:"/fixture/model.gguf"}),true);
assert.equal(policy.isLocal({local:true,api_format:"gguf",gguf_path:"https://cloud/model.gguf"}),false);
assert.equal(policy.isLocal({...model("http://localhost"),api_format:"unknown"}),false);
assert.equal(policy.allowed(model("https://cloud.example"),true),false);
assert.equal(policy.allowed(model("https://cloud.example"),false),true);
assert.equal(policy.allowed(null,false),false);
console.log("HADANION_LOCAL_MODEL_POLICY_PASS loopback gguf failClosed explicitCloudOptIn");
