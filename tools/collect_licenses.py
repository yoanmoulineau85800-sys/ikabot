"""Copie les notices installées sans lire de configuration ni de secrets."""
from importlib import metadata
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
target = root / "packaging" / "licences"
target.mkdir(parents=True, exist_ok=True)
report = []
for dist in sorted(metadata.distributions(), key=lambda d: d.metadata.get("Name", "").lower()):
    name = dist.metadata.get("Name", "unknown")
    report.append(f"{name}=={dist.version}\nLicence : {dist.metadata.get('License-Expression') or dist.metadata.get('License') or 'Voir les notices jointes / vérifier en amont'}\n")
    for file in dist.files or []:
        relative = Path(str(file))
        if ".dist-info" not in str(relative) or not any(x in relative.name.lower() for x in ("license", "copying", "notice")):
            continue
        source = Path(dist.locate_file(file))
        if source.is_file():
            destination = target / name / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
(target / "INDEX.txt").write_text("\n".join(report), encoding="utf-8")
print("Notices copiées dans", target)
