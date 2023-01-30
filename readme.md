# md.persistence.yaml

md.persistence.yaml component provides implementation to persist (save, read) python runtime data,
using YAML format, and few useful tools out from box.

## Architecture overview

[![Architecture overview][architecture-overview]][architecture-overview]

## Install

```sh
pip install md.persistence.yaml --index-url https://source.md.land/python/  
pip intall pyyaml  # optional dependency (to use `md.persistence.yaml.PyYamlLoad`) 
pip intall strictyaml  # optional dependency (to use `md.persistence.yaml.StrictYamlLoad`) 
```

## [Documentation](docs/index.md)

Read documentation with examples: https://development.md.land/python/md.persistence.yaml/

## [Changelog](changelog.md)
## [License (MIT)](license.md)

[architecture-overview]: docs/_static/architecture-overview.class-diagram.svg
