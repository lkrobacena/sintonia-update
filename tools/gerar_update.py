import hashlib, json, os, sys

REPO = os.environ.get("GITHUB_REPOSITORY", "lkrobacena/sintonia-update")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(RAIZ, "data")

with open(os.path.join(RAIZ, "config.json"), encoding="utf-8") as f:
    cfg = json.load(f)

def sha1(caminho):
    h = hashlib.sha1()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()

arquivos = []
for pasta, _, nomes in os.walk(DATA):
    for nome in sorted(nomes):
        if nome == ".gitkeep":
            continue
        completo = os.path.join(pasta, nome)
        rel = os.path.relpath(completo, DATA).replace(os.sep, "/")
        arquivos.append({"path": rel, "size": os.path.getsize(completo), "sha1": sha1(completo)})
arquivos.sort(key=lambda a: a["path"])

saida = {
    "versionCode": cfg["versionCode"],
    "versionName": cfg["versionName"],
    "url": cfg["apkUrl"],
    "notes": cfg.get("notes", ""),
    "force": cfg.get("force", False),
    "data": {
        "version": cfg.get("dataVersion", 1),
        "baseUrl": "https://raw.githubusercontent.com/%s/%s/data/" % (REPO, BRANCH),
        "files": arquivos,
    },
}
if cfg.get("dataZipUrl"):
    saida["dataZipUrl"] = cfg["dataZipUrl"]

with open(os.path.join(RAIZ, "update.json"), "w", encoding="utf-8") as f:
    json.dump(saida, f, indent=2, ensure_ascii=False)
print("update.json gerado com %d arquivo(s)" % len(arquivos))
