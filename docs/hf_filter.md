# Hugging Face push filter

Protect the Hub from unsigned / tampered adapters by rejecting them **before they leave your machine**.

## One‑time setup

```bash
# inside your adapter repo
git config filter.loraprov-clean.clean "python -m loraprov.hf_filter clean %f"
git config filter.loraprov-clean.smudge cat
echo "*.safetensors filter=loraprov-clean" >> .gitattributes
```

After this, any attempt to `git push` a `.safetensors` file without a valid signature will fail like:

```text
[loraprov] adapter_sha256 mismatch (file tampered?)
error: failed to push some refs
```

## How it works

1. Git‑LFS invokes the *clean* filter before uploading each file.  
2. The filter calls `loraprov verify <file>`.  
3. If verification fails, the push is aborted with a clear message.
