import re
import typing

import md.persistence


# Metadata
__version__ = '0.1.0'
__author__ = 'https://md.land/md'
__all__ = (
    # Metadata
    '__version__',
    '__author__',
    # Implementation
    'parse_clean_imports',
    'parse_dirty_imports',
    'PyYamlLoad',
    'StrictYamlLoad',
)


# Import
_RE_IMPORT_BASIC_TAG = re.compile(r'^!import\s+(?P<filename>[^\'\"#]*[^#\s]+)\s*(?P<comment>#.+|)$')  # warning: case-sensitive, no quotes support
_RE_EMPTY_LINE = re.compile(r'^\s*$')
_RE_YAML_FILE_EXTENSION = re.compile(r'^.+\.ya?ml$', flags=re.IGNORECASE)


# Exception
def parse_clean_imports(raw_content: str) -> typing.Tuple[typing.List[typing.Tuple[str, str]], str]:
    """
    Parses clean imports, for example:
        !import filename1.yaml
        !import filename2.yaml

        content: ~
    """
    import_list: typing.List[typing.Tuple[str, str]] = []
    content_offset = 0  # len(`\n`) -> 1

    for line_content in raw_content.split('\n'):
        if _RE_EMPTY_LINE.match(line_content):
            content_offset += 1
            continue

        if line_content.lower().startswith('!!import'):
            raise md.persistence.LoadException.as_parse_error(
                'Yaml `!!import` tag is not supported, use `!import` instead'
            )

        if not line_content.startswith('!import'):
            break

        basic_import_tag_match = _RE_IMPORT_BASIC_TAG.match(line_content)
        if not basic_import_tag_match:
            raise md.persistence.LoadException.as_parse_error(
                'Advanced `!import` syntax is not supported yet, use `!import filename` syntax instead'
            )

        match_dict = basic_import_tag_match.groupdict()
        if match_dict['filename'].endswith('/'):  # if not os.path.isfile(match_dict['filename']):
            raise md.persistence.LoadException.as_not_supported('Yaml `!import` tag supports only filename')

        import_list.append(('file', match_dict['filename']))
        content_offset += len(line_content) + 1
    return import_list, raw_content[content_offset:]


def parse_dirty_imports(content: typing.Any) -> typing.Tuple[typing.List[typing.Tuple[str, str]], dict]:
    """
    Parses dirty imports, returns new content with removed `imports` statement for example:
        imports:
            - resource: filename1.yaml
            - resource: filename2.yaml
        content: ~
    """
    if not isinstance(content, dict):
        return [], content

    if 'imports' not in content:
        return [], content

    imports = content['imports']
    del content['imports']

    import_list = []

    for import_ in imports:
        assert 'type' not in import_ or isinstance(import_['type'], str)
        assert 'resource' in import_
        import_list.append((import_['type'] if 'type' in import_ else 'file', import_['resource']))

    return import_list, content


# Yaml loader
class PyYamlLoad(md.persistence.LoadInterface):
    def __init__(
        self,
        schema: typing.Optional[str] = None,
        use_clean_import: bool = True,
        use_dirty_import: bool = False,
        import_: md.persistence.ImportInterface = None
    ) -> None:
        assert import_ or not (use_clean_import or use_dirty_import), 'Using import options requires `import_` driver'

        try:
            import yaml
        except ImportError as e:
            raise md.persistence.LoadException.as_requirement_missed() from e

        self._yaml = yaml
        self._import = import_
        self._use_clean_import = use_clean_import
        self._use_dirty_import = use_dirty_import
        self._schema = schema

    def supports(self, filename: str) -> bool:
        return bool(_RE_YAML_FILE_EXTENSION.match(filename))

    def load(self, filename: str) -> typing.Tuple[typing.Any, typing.Dict[str, typing.List[str]]]:
        if not self.supports(filename=filename):
            raise md.persistence.LoadException.as_not_supported(f'File type is not supported: `{filename!s}`')

        with open(filename) as stream:
            raw_content = stream.read()

        import_list: typing.List[typing.Tuple[str, str]] = []

        if self._use_clean_import:
            import_list_, raw_content = parse_clean_imports(raw_content=raw_content)
            import_list.extend(import_list_)

        content = {}
        if raw_content:  # ... content file may consist only import tags
            content = self._yaml.load(stream=raw_content, Loader=self._yaml.FullLoader)
            assert isinstance(content, dict)

            if self._schema:  # todo implement schema validation
                raise NotImplementedError('Schema validation is not implemented yet')

        if self._use_dirty_import:
            import_list_, content = parse_dirty_imports(content=content)
            import_list.extend(import_list_)

        return md.persistence.do_load(
            filename=filename,
            content=content,
            import_list=import_list,
            import_=self._import,
        )


class StrictYamlLoad(md.persistence.LoadInterface):
    def __init__(
        self,
        schema: typing.Optional[str] = None,
        use_clean_import: bool = True,
        use_dirty_import: bool = False,
        import_: md.persistence.ImportInterface = None,
        load_options: typing.Dict[str, typing.Any] = None
    ) -> None:
        try:
            import strictyaml
        except ImportError as e:
            raise md.persistence.LoadException.as_requirement_missed() from e

        self._strictyaml = strictyaml

        self._import = import_
        self._use_clean_import = use_clean_import
        self._use_dirty_import = use_dirty_import
        self._schema = schema
        self._load_options = load_options or dict(allow_flow_style=True)

    def supports(self, filename: str) -> bool:
        return bool(_RE_YAML_FILE_EXTENSION.match(filename))

    def load(self, filename: str) -> typing.Tuple[typing.Any, typing.Dict[str, typing.List[str]]]:
        if not self.supports(filename=filename):
            raise md.persistence.LoadException.as_not_supported(f'File type is not supported: `{filename!s}`')

        with open(filename) as stream:
            raw_content = stream.read()

        import_list: typing.List[typing.Tuple[str, str]] = []

        if self._use_clean_import:
            import_list_, raw_content = parse_clean_imports(raw_content=raw_content)
            import_list.extend(import_list_)

        content = self._strictyaml.dirty_load(yaml_string=raw_content, schema=self._schema, **self._load_options).data

        if self._use_dirty_import:
            import_list_, content = parse_dirty_imports(content)
            import_list.extend(import_list_)

        return md.persistence.do_load(
            content=content,
            import_list=import_list,
            filename=filename,
            import_=self._import,
        )
