# Purpose: Build a minimal App Service deployment archive
# Learn: Separate deployable application files from course materials and credentials.
# Run: From project root: python scripts/package_deployment.py. Produces outputs/app-deploy.zip; it does not deploy anything.

from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
out=root/'outputs'
out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/'app-deploy.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths=[root/'requirements.txt']+list((root/'requirements').glob('*.txt'))
    paths+=list((root/'src').rglob('*.py'))+list((root/'data').rglob('*.json'))
    for p in paths:
        z.write(p,p.relative_to(root))
print(out/'app-deploy.zip')
