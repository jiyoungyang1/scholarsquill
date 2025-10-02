"""
Zotero to ScholarsQuill metadata mapper
Maps Zotero item data to PaperMetadata structure
"""

import re
from typing import Dict, Any, List, Optional
from src.models import PaperMetadata


class ZoteroMetadataMapper:
    """Maps Zotero items to ScholarsQuill PaperMetadata"""

    def map_zotero_item(self, zotero_item: Dict[str, Any]) -> PaperMetadata:
        """
        Map a Zotero item to PaperMetadata

        Args:
            zotero_item: Zotero item dictionary with 'key', 'version', 'data' fields

        Returns:
            PaperMetadata with mapped fields
        """
        data = zotero_item.get('data', {})
        item_type = data.get('itemType', 'journalArticle')

        # Extract creators (authors)
        creators = data.get('creators', [])
        authors = self._extract_authors(creators)
        first_author = self._extract_first_author(creators)

        # Extract year from date field
        year = self._extract_year(data.get('date', ''))

        # Extract title
        title = data.get('title', 'Untitled')

        # Generate citekey
        citekey = self.generate_citekey(zotero_item)

        # Extract publication info based on item type
        journal = self._extract_journal(data, item_type)

        # Extract tags
        tags = [tag['tag'] for tag in data.get('tags', [])]

        # Extract collections
        collections = data.get('collections', [])

        # Build Zotero URL
        zotero_key = zotero_item.get('key', '')
        zotero_url = f"zotero://select/library/items/{zotero_key}" if zotero_key else None

        # Create PaperMetadata
        metadata = PaperMetadata(
            title=title,
            first_author=first_author,
            authors=authors,
            year=year,
            citekey=citekey,
            item_type=item_type,
            journal=journal,
            volume=data.get('volume'),
            issue=data.get('issue'),
            pages=data.get('pages'),
            doi=data.get('DOI'),
            abstract=data.get('abstractNote'),
            page_count=0,  # Not available from Zotero
            file_path="",  # Will be set later if PDF attached
            # Zotero-specific fields
            zotero_key=zotero_key,
            zotero_url=zotero_url,
            zotero_tags=tags if tags else None,
            zotero_collections=collections if collections else None,
            date_added=data.get('dateAdded'),
            date_modified=data.get('dateModified')
        )

        return metadata

    def _extract_authors(self, creators: List[Dict[str, str]]) -> List[str]:
        """Extract formatted author list from Zotero creators"""
        authors = []
        for creator in creators:
            if creator.get('creatorType') == 'author':
                last = creator.get('lastName', '')
                first = creator.get('firstName', '')
                if last and first:
                    authors.append(f"{last}, {first}")
                elif last:
                    authors.append(last)
        return authors if authors else ['Unknown']

    def _extract_first_author(self, creators: List[Dict[str, str]]) -> str:
        """Extract first author's last name"""
        for creator in creators:
            if creator.get('creatorType') == 'author':
                return creator.get('lastName', 'Unknown')
        return 'Unknown'

    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from Zotero date field"""
        if not date_str:
            return None

        # Try to extract 4-digit year
        match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if match:
            return int(match.group(0))

        return None

    def _extract_journal(self, data: Dict[str, Any], item_type: str) -> str:
        """Extract journal/publication name based on item type"""
        if item_type == 'journalArticle':
            return data.get('publicationTitle', '')
        elif item_type == 'conferencePaper':
            return data.get('proceedingsTitle', '')
        elif item_type == 'book':
            return data.get('publisher', '')
        elif item_type == 'thesis':
            return data.get('university', '')
        else:
            return data.get('publicationTitle', '')

    def generate_citekey(self, zotero_item: Dict[str, Any], existing_citekeys: Optional[List[str]] = None) -> str:
        """
        Generate citekey in authorYEARkeyword format

        Args:
            zotero_item: Zotero item dictionary
            existing_citekeys: List of existing citekeys to check for collisions

        Returns:
            Unique citekey string
        """
        data = zotero_item.get('data', {})

        # Extract author
        creators = data.get('creators', [])
        first_author = self._extract_first_author(creators)
        author_part = re.sub(r'[^a-zA-Z]', '', first_author).lower()
        if not author_part:
            author_part = 'unknown'

        # Extract year
        year = self._extract_year(data.get('date', ''))
        year_part = str(year) if year else 'nodate'

        # Extract keyword from title
        title = data.get('title', '')
        keyword = self._generate_keyword(title)

        # Build base citekey
        base_citekey = f"{author_part}{year_part}{keyword}"

        # Check for collisions
        if existing_citekeys is None:
            return base_citekey

        # Handle collisions with numeric suffix
        if base_citekey not in existing_citekeys:
            return base_citekey

        # Find next available suffix
        suffix = 2
        while f"{base_citekey}-{suffix}" in existing_citekeys:
            suffix += 1

        return f"{base_citekey}-{suffix}"

    def _generate_keyword(self, title: str) -> str:
        """
        Extract meaningful keyword from title

        Args:
            title: Paper title

        Returns:
            Keyword (lowercase, alphabetic only)
        """
        if not title:
            return 'notitle'

        # Common stop words to skip
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }

        # Clean and split title
        words = re.findall(r'\b[a-zA-Z]+\b', title.lower())

        # Find first meaningful word
        for word in words:
            if len(word) >= 4 and word not in stop_words:
                return word[:10]  # Limit keyword length

        # Fallback: use first word if no meaningful word found
        if words:
            return words[0][:10]

        return 'notitle'
