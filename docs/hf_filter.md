## Hugging Face push protection

```bash
git config filter.loraprov-clean.clean "python -m loraprov.hf_filter clean %f"
git config filter.loraprov-clean.smudge cat
echo "*.safetensors filter=loraprov-clean" >> .gitattributes
