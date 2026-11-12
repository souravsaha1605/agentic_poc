"""Build the Teams-independent learning API without state, secrets or notebooks."""
import argparse
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT = Path(__file__).resolve().parents[2]

def build(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        sources = list(ROOT.glob('*.py'))
        for folder in ('agents', 'services', 'tools'):
            sources.extend((ROOT / folder).rglob('*.py'))
        sources += [Path(__file__).with_name('web_api.py'), Path(__file__).with_name('index.html')]
        for source in sources:
            archive.write(source, source.relative_to(ROOT))
        archive.writestr('requirements.txt', (ROOT / 'requirements.txt').read_text() +
                        '\ngunicorn>=23,<24\nazure-identity==1.25.3\nazure-storage-blob==12.31.0\n')
    output.chmod(0o600)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(build(parser.parse_args().output))
