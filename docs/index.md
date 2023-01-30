# Documentation

md.persistence.yaml component provides implementation to persist (save, read) python runtime data,
using YAML format.

## Architecture overview

[![Architecture overview][architecture-overview]][architecture-overview]

## Component overview

```python3
def parse_clean_imports(raw_content: str) -> typing.Tuple[typing.List[typing.Tuple[str, str]], str]: ...
def parse_dirty_imports(content: typing.Any) -> typing.Tuple[typing.List[typing.Tuple[str, str]], dict]: ...
```

## Install

```sh
pip install md.persistence.yaml --index-url https://source.md.land/python/
```

## Usage
### pyyaml driver

`md.persistence.yaml.PyYamlLoad` implements 
`md.persistence.LoadInterface` and provides YAML file loading 
with `clean` and `dirty` import features, using `pyyaml` functions.

Using `md.persistence.yaml.PyYamlLoad` requires `pyyaml` package to be installed:

```sh
pip install pyyaml
```

=== "Basic example (without import system)"
    
    ```python3
    import md.persistence.yaml
    
    if __name__ == '__main__':
        load_yaml = md.persistence.yaml.PyYamlLoad()
        
        try:
            content = load_yaml.load(filename='etc/container.yaml')
        except md.persistence.LoadException as e:
            ...

        # use `content` data ...
    ```

=== "Advanced example (within import system)"
    
    ```python3
    import md.persistence.yaml
    import md.python.dict
    
    if __name__ == '__main__':
        load_yaml = md.persistence.yaml.PyYamlLoad.__new__(
            md.persistence.yaml.PyYamlLoad
        )  # 1. create instance without initialization

        import_ = md.persistence.DefaultImport(
            load=load_yaml,  # 2. inject instance
            merge_dictionary=md.python.dict.DefaultMergeDictionary(),
        )
    
        load_yaml.__init__(  # 3. initialize instance
            use_clean_import=True,  # default: True
            use_dirty_import=True,  # default: False
            import_=import_,
        )
    
        try:
            content = load_yaml.load(filename='etc/container.yaml')
        except md.persistence.LoadException as e:
            ...

        # use `content` data ...
    ```

    !!! notice
        
        1. In example above is used a hack to solve circular reference issue,
        accessing to not initialized instance may lead to issue in some cases.
        2. Instances initialization this way may not be needed when caching 
        substem is used between `import` and `load` action subsystems.

### strictyaml driver

`md.persistence.yaml.StrictYamlLoad` implements 
`md.persistence.LoadInterface` and provides YAML file loading 
with `clean` and `dirty` import features, using `strictyaml` functions.

Using `md.persistence.yaml.StrictYamlLoad` requires `strictyaml` package to be installed:

```sh
pip install strictyaml
```

=== "Basic example (without import system)"
    
    ```python3
    import md.persistence.yaml
    
    if __name__ == '__main__':
        load_yaml = md.persistence.yaml.StrictYamlLoad()
        
        try:
            content = load_yaml.load(filename='etc/container.yaml')
        except md.persistence.LoadException as e:
            ...

        # use `content` data ...
    ```

=== "Advanced example (within import system)"
    
    ```python3
    import md.persistence.yaml
    import md.python.dict
    
    if __name__ == '__main__':
        load_yaml = md.persistence.yaml.StrictYamlLoad.__new__(
            md.persistence.yaml.StrictYamlLoad
        )  # 1. create instance without initialization

        import_ = md.persistence.DefaultImport(
            load=load_yaml,  # 2. inject instance
            merge_dictionary=md.python.dict.DefaultMergeDictionary(),
        )
    
        load_yaml.__init__(  # 3. initialize instance
            use_clean_import=True,  # default: True
            use_dirty_import=True,  # default: False
            import_=import_,
        )
    
        try:
            content = load_yaml.load(filename='etc/container.yaml')
        except md.persistence.LoadException as e:
            ...

        # use `content` data ...
    ```

    !!! notice
        
        1. In example above is used a hack to solve circular reference issue,
        accessing to not initialized instance may lead to issue in some cases.
        2. Instances initialization this way may not be needed when caching 
        substem is used between `import` and `load` action subsystems.

See a [strictyaml documentation](https://hitchdev.com/strictyaml/) for more details.

### Import system

Both `md.persistence.yaml.PyYamlLoad`, `md.persistence.yaml.StrictYamlLoad`
implementation supports import system using `dirty` and `clean` style.

#### Clean import style

Clean import represents transparent for content metadata statements,
represented as `!import` YAML tags. Both of `pyyaml` and `strictyaml` parsers have no
tag support feature from out of box. Provided in this package parser expects `!import`
statements in the beginning of the YAML file, then after all `!import` tags consumed,
parsing process is delegates for 3rd party implementation.

```yaml
!import services.yaml
!import parameters.yaml

services: {}
parameters: {}
```

!!! warning
    
    If `use_clean_import` is disabled and `!import` tag is presented in the file,
    all it content will be passed into 3rd party parser as is, 
    what may lead to a parse issue.

All `!import` statements must satisfy regular expression:

```regexp
^!import\s+(?P<filename>[^'"#]*[^#\s]+)\s*(?P<comment>#.+|)$
```

for example:

```yaml
!import filename.yaml  # # ok
!import filename.yaml  # <comment here> # ok

!import 'filename.yaml'  # NOT ok
!import "filename.yaml"  # NOT ok
!ImPoRt filename.yaml  # NOT ok
```

#### Dirty import style

!!! deprecated
    
    Dirty import style marked as deprecated and will be removed in future releases.
    Consider to avoid using it in favor of [Clean import style](#clean-import-style).

Dirty import style represents a reserved `imports` key at root of file,
for example:

```yaml
imports:
  - resource: filename.yaml
  - resource: filename2.yaml  # just as same as `- { resource: filename2.yaml }`
```

Unlike *clean import style* this parser delegates all content parsing 
to 3rd party implementation, without preprocessing it. After file parsed,
import processing starts, then `imports` statement will be removed.

[architecture-overview]: _static/architecture-overview.class-diagram.svg
