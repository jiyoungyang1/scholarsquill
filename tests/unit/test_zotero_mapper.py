"""
Unit tests for Zotero ’ ScholarsQuill metadata mapping
Tests MUST fail until implementation is complete (TDD)
"""

import pytest
from src.zotero.mapper import ZoteroMetadataMapper
from src.models import PaperMetadata


class TestZoteroMetadataMapping:
    """Test mapping Zotero items to ScholarsQuill metadata"""

    @pytest.fixture
    def mapper(self):
        """Create mapper instance"""
        return ZoteroMetadataMapper()

    def test_map_journal_article(self, mapper):
        """Test map_zotero_item() for journalArticle type"""
        zotero_item = {
            'key': 'ABC123',
            'version': 1,
            'data': {
                'itemType': 'journalArticle',
                'title': 'Machine Learning for Protein Stability',
                'creators': [
                    {'creatorType': 'author', 'firstName': 'John', 'lastName': 'Smith'},
                    {'creatorType': 'author', 'firstName': 'Jane', 'lastName': 'Doe'}
                ],
                'date': '2023',
                'DOI': '10.1234/example',
                'abstractNote': 'This paper investigates...',
                'publicationTitle': 'Nature',
                'volume': '42',
                'issue': '3',
                'pages': '123-145',
                'tags': [
                    {'tag': 'machine-learning'},
                    {'tag': 'protein-stability'}
                ],
                'collections': ['COLL1', 'COLL2']
            }
        }

        metadata = mapper.map_zotero_item(zotero_item)

        assert isinstance(metadata, PaperMetadata)
        assert metadata.title == 'Machine Learning for Protein Stability'
        assert metadata.first_author == 'Smith'
        assert len(metadata.authors) == 2
        assert metadata.year == 2023
        assert metadata.doi == '10.1234/example'
        assert metadata.journal == 'Nature'
        assert metadata.volume == '42'
        assert metadata.pages == '123-145'
        # Extended fields
        assert metadata.zotero_key == 'ABC123'
        assert 'machine-learning' in metadata.zotero_tags
        assert len(metadata.zotero_collections) == 2

    def test_map_book_type(self, mapper):
        """Test mapping for book item type"""
        zotero_item = {
            'key': 'BOOK123',
            'data': {
                'itemType': 'book',
                'title': 'Computational Biology Methods',
                'creators': [
                    {'creatorType': 'author', 'firstName': 'Alice', 'lastName': 'Brown'}
                ],
                'date': '2022',
                'publisher': 'Academic Press',
                'ISBN': '978-1234567890'
            }
        }

        metadata = mapper.map_zotero_item(zotero_item)

        assert metadata.item_type == 'book'
        assert metadata.title == 'Computational Biology Methods'
        assert metadata.first_author == 'Brown'

    def test_map_conference_paper(self, mapper):
        """Test mapping for conferencePaper type"""
        zotero_item = {
            'key': 'CONF123',
            'data': {
                'itemType': 'conferencePaper',
                'title': 'Deep Learning Applications',
                'creators': [
                    {'creatorType': 'author', 'firstName': 'Bob', 'lastName': 'Chen'}
                ],
                'date': '2024',
                'proceedingsTitle': 'NeurIPS 2024'
            }
        }

        metadata = mapper.map_zotero_item(zotero_item)

        assert metadata.item_type == 'conferencePaper'
        assert metadata.journal == 'NeurIPS 2024'

    def test_map_thesis(self, mapper):
        """Test mapping for thesis type"""
        zotero_item = {
            'key': 'THESIS123',
            'data': {
                'itemType': 'thesis',
                'title': 'Novel Protein Folding Algorithms',
                'creators': [
                    {'creatorType': 'author', 'firstName': 'Carol', 'lastName': 'Davis'}
                ],
                'date': '2021',
                'university': 'MIT'
            }
        }

        metadata = mapper.map_zotero_item(zotero_item)

        assert metadata.item_type == 'thesis'

    def test_tag_preservation(self, mapper):
        """Test that Zotero tags are preserved"""
        zotero_item = {
            'key': 'TAG123',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Test Paper',
                'creators': [{'creatorType': 'author', 'lastName': 'Test'}],
                'date': '2023',
                'tags': [
                    {'tag': 'neural-networks'},
                    {'tag': 'deep-learning'},
                    {'tag': 'computer-vision'}
                ]
            }
        }

        metadata = mapper.map_zotero_item(zotero_item)

        assert len(metadata.zotero_tags) == 3
        assert 'neural-networks' in metadata.zotero_tags
        assert 'deep-learning' in metadata.zotero_tags

    def test_collection_hierarchy_mapping(self, mapper):
        """Test collection hierarchy is preserved"""
        zotero_item = {
            'key': 'HIER123',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Test Paper',
                'creators': [{'creatorType': 'author', 'lastName': 'Test'}],
                'date': '2023',
                'collections': ['ROOT', 'ROOT/SUBFOLDER', 'ROOT/SUBFOLDER/DEEP']
            }
        }

        metadata = mapper.map_zotero_item(zotero_item)

        assert 'ROOT/SUBFOLDER/DEEP' in metadata.zotero_collections


class TestCitekeyGeneration:
    """Test citekey generation from Zotero metadata"""

    @pytest.fixture
    def mapper(self):
        """Create mapper instance"""
        return ZoteroMetadataMapper()

    def test_generate_citekey_unique(self, mapper):
        """Test generate_citekey() with unique author/year"""
        zotero_item = {
            'key': 'ABC123',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Machine Learning for Neural Networks',
                'creators': [
                    {'creatorType': 'author', 'firstName': 'John', 'lastName': 'Smith'}
                ],
                'date': '2023'
            }
        }

        citekey = mapper.generate_citekey(zotero_item)

        # Format: authorYEARkeyword
        assert citekey.startswith('smith2023')
        assert 'machine' in citekey or 'neural' in citekey or 'learning' in citekey

    def test_collision_detection(self, mapper):
        """Test collision detection when citekey exists"""
        existing_citekeys = ['smith2023machine', 'smith2023neural']

        zotero_item = {
            'key': 'NEW123',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Machine Learning Applications',
                'creators': [
                    {'creatorType': 'author', 'lastName': 'Smith'}
                ],
                'date': '2023'
            }
        }

        # Should detect collision and return different citekey
        citekey = mapper.generate_citekey(zotero_item, existing_citekeys)

        assert citekey not in existing_citekeys
        assert citekey.startswith('smith2023')

    def test_numeric_suffix_appending(self, mapper):
        """Test numeric suffix for collision resolution (smith2023-2, smith2023-3)"""
        # Simulate collisions
        existing_citekeys = [
            'smith2023machine',
            'smith2023machine-2'
        ]

        zotero_item = {
            'key': 'COLL123',
            'data': {
                'itemType': 'journalArticle',
                'title': 'Machine Learning Methods',  # Same keyword
                'creators': [
                    {'creatorType': 'author', 'lastName': 'Smith'}
                ],
                'date': '2023'
            }
        }

        citekey = mapper.generate_citekey(zotero_item, existing_citekeys)

        # Should append -3 to avoid collision
        assert citekey == 'smith2023machine-3'
