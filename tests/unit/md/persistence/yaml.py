import typing

import md.persistence.yaml
import pytest


class TestParseCleanImports:
    def test_empty_content(self) -> None:
        # arrange
        content = ""

        # act
        import_list, raw_content = md.persistence.yaml.parse_clean_imports(raw_content=content)

        # assert
        assert isinstance(import_list, list)
        assert import_list == []
        assert raw_content == ''

    def test_only_imports_content(self) -> None:
        # arrange
        content = "!import file.yaml\n!import file2.yaml"

        # act
        import_list, raw_content = md.persistence.yaml.parse_clean_imports(raw_content=content)

        # assert
        assert isinstance(import_list, list)
        assert import_list == [
            ('file', 'file.yaml'),
            ('file', 'file2.yaml')
        ]
        assert raw_content == ''

    @pytest.mark.skip()
    def test_only_imports_content_with_comment_in_the_beginning(self) -> None:
        # arrange
        content = "# some comment ...\n!import file.yaml\n!import file2.yaml"

        # act
        import_list, raw_content = md.persistence.yaml.parse_clean_imports(raw_content=content)

        # assert
        assert isinstance(import_list, list)
        assert import_list == [
            ('file', 'file.yaml'),
            ('file', 'file2.yaml')
        ]
        assert raw_content == ''

    def test_only_imports_content_with_comment(self) -> None:
        # arrange
        content = "!import file.yaml#comment\n!import file2.yaml # comment"

        # act
        import_list, raw_content = md.persistence.yaml.parse_clean_imports(raw_content=content)

        # assert
        assert isinstance(import_list, list)
        assert import_list == [
            ('file', 'file.yaml'),
            ('file', 'file2.yaml')
        ]
        assert raw_content == ''

    def test_only_content(self) -> None:
        # arrange
        content = "content: 42"

        # act
        import_list, raw_content = md.persistence.yaml.parse_clean_imports(raw_content=content)

        # assert
        assert isinstance(import_list, list)
        assert import_list == []
        assert raw_content == 'content: 42'

    def test_with_content_and_imports(self) -> None:
        # arrange
        content = "!import file.yaml\n!import file2.yaml\ncontent: 42"

        # act
        import_list, raw_content = md.persistence.yaml.parse_clean_imports(raw_content=content)

        # assert
        assert isinstance(import_list, list)
        assert import_list == [
            ('file', 'file.yaml'),
            ('file', 'file2.yaml')
        ]
        assert raw_content == 'content: 42'

    def test_raises_for_tag(self) -> None:
        # arrange
        content = "!!import file.yaml"

        # act
        try:
            md.persistence.yaml.parse_clean_imports(raw_content=content)
        except md.persistence.LoadException as e:
            # assert
            assert e.code == 2

    @pytest.mark.parametrize('content', ['!import "file".yaml', "!import 'file.yaml'"])
    def test_raises_for_invalid_import(self, content: str) -> None:
        # act
        try:
            md.persistence.yaml.parse_clean_imports(raw_content=content)
        except md.persistence.LoadException as e:
            # assert
            assert e.code == 1

    def test_raises_for_unsupported_resource_type(self) -> None:
        # act
        try:
            md.persistence.yaml.parse_clean_imports(raw_content='!import directory/')
        except md.persistence.LoadException as e:
            # assert
            assert e.code == 3


class TestParseDirtyImports:
    @pytest.mark.parametrize('content', [{4, 8}, (5, ), "16", [23], 42, 0.4815162342])
    def test_not_supported_content_type(self, content: typing.Any) -> None:  # white/negative
        # act
        import_list, content_ = md.persistence.yaml.parse_dirty_imports(content=content)

        # assert
        assert import_list == []
        assert content_ == content

    def test_empty_content(self) -> None:  # white/negative
        # act
        import_list, content_ = md.persistence.yaml.parse_dirty_imports(content={})

        # assert
        assert import_list == []
        assert content_ == {}

    def test_only_content(self) -> None:
        # arrange
        content = {
            'content': 42
        }

        # act
        import_list, content_ = md.persistence.yaml.parse_dirty_imports(content=content)

        # assert
        assert 'imports' not in content_
        assert import_list == []
        assert content_ == {'content': 42}

    def test_only_imports_content(self) -> None:
        # arrange
        content = {
            'imports': [
                {'resource': 'file1.yaml'},
                {'resource': 'file2.yaml'},
            ]
        }

        # act
        import_list, content_ = md.persistence.yaml.parse_dirty_imports(content=content)

        # assert
        assert 'imports' not in content_
        assert import_list == [
            ('file', 'file1.yaml'),
            ('file', 'file2.yaml')
        ]
        assert content_ == {}

    def test_imports_and_content(self) -> None:
        # arrange
        content = {
            'imports': [
                {'resource': 'file1.yaml'},
                {'resource': 'file2.yaml'},
            ],
            'content': 42
        }

        # act
        import_list, content_ = md.persistence.yaml.parse_dirty_imports(content=content)

        # assert
        assert 'imports' not in content_
        assert import_list == [
            ('file', 'file1.yaml'),
            ('file', 'file2.yaml')
        ]
        assert content_ == {'content': 42}
