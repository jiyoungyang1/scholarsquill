"""
Citation Context Mapping Processor for ScholarsQuill

This module implements the citemap functionality for analyzing citation contexts
and building reference networks within academic papers.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import logging
import networkx as nx
import plotly.graph_objects as go
import plotly.offline as pyo
from datetime import datetime

from .models import ProcessingOptions, CitationContext, ReferenceNetwork
from .pdf_processor import PDFProcessor
from .template_engine import TemplateProcessor
from .utils import generate_citekey, get_current_timestamp
from .batch_processor import BatchProcessor

logger = logging.getLogger(__name__)


class CitemapProcessor:
    """
    Processes PDFs to extract citation contexts and build reference networks.
    
    Creates detailed maps of how papers connect different ideas from different sources,
    showing citation contexts, reference purposes, and intellectual lineage.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the citation mapping processor."""
        self.pdf_processor = PDFProcessor()
        self.template_processor = TemplateProcessor(templates_dir)
        self.batch_processor = BatchProcessor()
        
        # Citation patterns for different reference formats
        self.citation_patterns = [
            r'\(([A-Za-z][A-Za-z\s&,]+\s+(?:et\s+al\.?\s+)?\d{4}[a-z]?(?:;\s*[A-Za-z][A-Za-z\s&,]+\s+(?:et\s+al\.?\s+)?\d{4}[a-z]?)*)\)',  # (Author 2020; Smith et al. 2019)
            r'\[(\d+(?:[-,\s]*\d+)*)\]',  # [1], [1-3], [1,2,5]
            r'([A-Za-z][A-Za-z\s&,]+\s+(?:et\s+al\.?\s+)?\(\d{4}[a-z]?\))',  # Author (2020), Smith et al. (2019)
            r'([A-Za-z][A-Za-z\s&,]+\s+(?:et\s+al\.?\s+)?\d{4}[a-z]?)',  # Author 2020, Smith et al. 2019
        ]
    
    async def create_citemap(
        self,
        pdf_path: Path,
        options: ProcessingOptions
    ) -> Dict[str, any]:
        """
        Create a citation context map for a given PDF.
        
        Args:
            pdf_path: Path to the PDF file
            options: Processing configuration options
            
        Returns:
            Dictionary containing citemap results and metadata
        """
        try:
            logger.info(f"Starting citemap analysis for: {pdf_path}")
            
            # Extract PDF content
            try:
                content = self.pdf_processor.extract_text(str(pdf_path))
                metadata = self.pdf_processor.extract_metadata(str(pdf_path))
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to extract PDF content: {str(e)}"
                }
            
            # Extract citation contexts
            citation_contexts = self._extract_citation_contexts(content)
            
            # Extract reference list
            references = self._extract_references(content)
            
            # Build reference network
            network = self._build_reference_network(citation_contexts, references)
            
            # Generate citemap content using template
            citemap_data = {
                "paper": {
                    "title": metadata.title if hasattr(metadata, 'title') else "Unknown Title",
                    "authors": metadata.authors if hasattr(metadata, 'authors') else ["Unknown Author"],
                    "year": metadata.year if hasattr(metadata, 'year') else "Unknown Year",
                    "citekey": generate_citekey(
                        self._extract_clean_first_author(metadata),
                        metadata.year if hasattr(metadata, 'year') else None,
                        metadata.title if hasattr(metadata, 'title') else "Unknown Title"
                    ),
                    "doi": metadata.doi if hasattr(metadata, 'doi') else "",
                    "journal": metadata.journal if hasattr(metadata, 'journal') else ""
                },
                "citation_analysis": {
                    "total_citations": len(citation_contexts),
                    "unique_references": len(references),
                    "citation_contexts": citation_contexts,
                    "references": references,
                    "network": network
                },
                "timestamp": get_current_timestamp(),
                "processing_info": {
                    "pdf_path": str(pdf_path),
                    "analysis_type": "citemap",
                    "template_used": "citemap"
                }
            }
            
            # Load and render template
            template = self.template_processor.load_template("citemap")
            rendered_content = self.template_processor.render_template(
                template, 
                citemap_data
            )
            
            # Generate output filename with consistent pattern
            citekey = generate_citekey(
                self._extract_clean_first_author(metadata),
                metadata.year if hasattr(metadata, 'year') else None,
                metadata.title if hasattr(metadata, 'title') else "Unknown Title"
            )
            safe_citekey = "".join(c for c in citekey if c.isalnum() or c in ('_', '-'))
            output_filename = f"{safe_citekey}_citemap.md"
            output_path = Path(options.output_dir) / output_filename
            
            # Write output file
            output_path.write_text(rendered_content, encoding="utf-8")
            
            # Generate interactive network visualization for single file too
            try:
                single_paper_data = {
                    citekey: {
                        "paper_info": {
                            "title": metadata.title if hasattr(metadata, 'title') else "Unknown Title",
                            "authors": metadata.authors if hasattr(metadata, 'authors') else ["Unknown Author"],
                            "year": metadata.year if hasattr(metadata, 'year') else "Unknown Year",
                            "citekey": citekey
                        },
                        "references": references,
                        "citation_contexts": citation_contexts
                    }
                }
                network_html_path = self._generate_interactive_network(single_paper_data, output_path)
                logger.info(f"Interactive network visualization generated: {network_html_path}")
            except Exception as e:
                logger.warning(f"Could not generate network visualization: {e}")
                network_html_path = None
            
            logger.info(f"Citemap analysis completed: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "network_html_path": network_html_path,
                "analysis_summary": {
                    "total_citations": len(citation_contexts),
                    "unique_references": len(references),
                    "network_nodes": len(network["nodes"]),
                    "network_edges": len(network["edges"])
                },
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error in citemap processing: {str(e)}")
            return {
                "success": False,
                "error": f"Citemap processing failed: {str(e)}"
            }
    
    def _extract_citation_contexts(self, content: str) -> List[CitationContext]:
        """
        Extract citation contexts from the paper content.
        
        Args:
            content: Full text content of the paper
            
        Returns:
            List of CitationContext objects
        """
        citation_contexts = []
        context_id = 1
        
        # Split content into sentences for context extraction
        sentences = re.split(r'[.!?]+', content)
        
        for sentence_idx, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            # Find citations in this sentence
            for pattern in self.citation_patterns:
                matches = re.finditer(pattern, sentence)
                
                for match in matches:
                    citation_text = match.group(1) if match.groups() else match.group(0)
                    
                    # Extract context (sentence + surrounding sentences)
                    context_start = max(0, sentence_idx - 1)
                    context_end = min(len(sentences), sentence_idx + 2)
                    context_sentences = sentences[context_start:context_end]
                    context = ". ".join([s.strip() for s in context_sentences if s.strip()]).strip()
                    
                    # Determine citation purpose
                    purpose = self._determine_citation_purpose(sentence)
                    
                    # Determine paper section
                    section = self._determine_section_context(sentence, content)
                    
                    citation_context = CitationContext(
                        id=context_id,
                        citation=citation_text,
                        context=context,
                        sentence=sentence,
                        purpose=purpose,
                        section=section,
                        position=match.start(),
                        surrounding_context=context
                    )
                    
                    citation_contexts.append(citation_context)
                    context_id += 1
        
        return citation_contexts
    
    def _extract_references(self, content: str) -> List[Dict[str, str]]:
        """
        Extract reference list from the paper content.
        
        Args:
            content: Full text content of the paper
            
        Returns:
            List of reference dictionaries
        """
        references = []
        
        # Find references section
        ref_section_patterns = [
            r'(?i)^references?\s*$',
            r'(?i)^bibliography\s*$',
            r'(?i)^works?\s+cited\s*$'
        ]
        
        lines = content.split('\n')
        ref_start = None
        
        for i, line in enumerate(lines):
            for pattern in ref_section_patterns:
                if re.match(pattern, line.strip()):
                    ref_start = i
                    break
            if ref_start:
                break
        
        if ref_start:
            # Extract references from the references section
            ref_lines = lines[ref_start+1:]
            
            current_ref = ""
            ref_number = 1
            
            for line in ref_lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    if current_ref:
                        raw_journal = self._parse_journal_from_reference(current_ref)
                        references.append({
                            "number": str(ref_number),
                            "text": current_ref.strip(),
                            "parsed_authors": self._parse_authors_from_reference(current_ref),
                            "parsed_year": self._parse_year_from_reference(current_ref),
                            "parsed_title": self._parse_title_from_reference(current_ref),
                            "parsed_doi": self._parse_doi_from_reference(current_ref),
                            "parsed_journal": raw_journal,
                            "normalized_journal": self._normalize_journal_name(raw_journal),
                            "parsed_volume": self._parse_volume_from_reference(current_ref),
                            "parsed_pages": self._parse_pages_from_reference(current_ref),
                            "reference_type": self._classify_reference_type(current_ref)
                        })
                        current_ref = ""
                        ref_number += 1
                    continue
                
                # Check if this line starts a new reference
                if re.match(r'^\[?\d+\]?\.?\s+', line) or re.match(r'^[A-Za-z]', line):
                    if current_ref:
                        raw_journal = self._parse_journal_from_reference(current_ref)
                        references.append({
                            "number": str(ref_number),
                            "text": current_ref.strip(),
                            "parsed_authors": self._parse_authors_from_reference(current_ref),
                            "parsed_year": self._parse_year_from_reference(current_ref),
                            "parsed_title": self._parse_title_from_reference(current_ref),
                            "parsed_doi": self._parse_doi_from_reference(current_ref),
                            "parsed_journal": raw_journal,
                            "normalized_journal": self._normalize_journal_name(raw_journal),
                            "parsed_volume": self._parse_volume_from_reference(current_ref),
                            "parsed_pages": self._parse_pages_from_reference(current_ref),
                            "reference_type": self._classify_reference_type(current_ref)
                        })
                        ref_number += 1
                    current_ref = line
                else:
                    # Continuation of current reference
                    current_ref += " " + line
            
            # Don't forget the last reference
            if current_ref:
                raw_journal = self._parse_journal_from_reference(current_ref)
                references.append({
                    "number": str(ref_number),
                    "text": current_ref.strip(),
                    "parsed_authors": self._parse_authors_from_reference(current_ref),
                    "parsed_year": self._parse_year_from_reference(current_ref),
                    "parsed_title": self._parse_title_from_reference(current_ref),
                    "parsed_doi": self._parse_doi_from_reference(current_ref),
                    "parsed_journal": raw_journal,
                    "normalized_journal": self._normalize_journal_name(raw_journal),
                    "parsed_volume": self._parse_volume_from_reference(current_ref),
                    "parsed_pages": self._parse_pages_from_reference(current_ref),
                    "reference_type": self._classify_reference_type(current_ref)
                })
        
        return references
    
    def _extract_citation_contexts_fast(self, content: str) -> List[CitationContext]:
        """
        Fast extraction of citation contexts with simplified processing.
        
        Args:
            content: Full text content of the paper
            
        Returns:
            List of CitationContext objects
        """
        citation_contexts = []
        context_id = 1
        
        # Use only the first two citation patterns for speed
        patterns = self.citation_patterns[:2]
        
        # Simple section detection
        sections = content.split('\n\n')
        
        for section_idx, section in enumerate(sections[:20]):  # Process first 20 sections only
            section_type = "body" if section_idx > 2 else "introduction"
            
            for pattern in patterns:
                for match in re.finditer(pattern, section):
                    sentence_start = max(0, section.rfind('.', 0, match.start()) + 1)
                    sentence_end = section.find('.', match.end())
                    if sentence_end == -1:
                        sentence_end = len(section)
                    
                    sentence = section[sentence_start:sentence_end].strip()
                    
                    citation_context = CitationContext(
                        id=f"ctx_{context_id}",
                        citation=match.group(0),
                        sentence=sentence,
                        purpose="general",
                        section=section_type,
                        position=match.start(),
                        surrounding_context=""
                    )
                    
                    citation_contexts.append(citation_context)
                    context_id += 1
                    
                    if len(citation_contexts) >= 50:  # Limit for speed
                        return citation_contexts
        
        return citation_contexts
    
    def _extract_references_fast(self, content: str) -> List[Dict[str, str]]:
        """
        Fast extraction of reference list with simplified processing.
        
        Args:
            content: Full text content of the paper
            
        Returns:
            List of reference dictionaries with basic metadata
        """
        references = []
        
        # Find references section with improved patterns
        ref_patterns = [
            r'(?i)references?\s*\n(.*?)(?:\n\s*\n|\Z)',
            r'(?i)bibliography\s*\n(.*?)(?:\n\s*\n|\Z)',
            r'(?i)works?\s+cited\s*\n(.*?)(?:\n\s*\n|\Z)'
        ]
        
        ref_text = None
        for pattern in ref_patterns:
            ref_match = re.search(pattern, content, re.DOTALL)
            if ref_match:
                ref_text = ref_match.group(1)
                break
        
        if not ref_text:
            return references
        
        # Parse references with improved logic
        ref_lines = [line.strip() for line in ref_text.split('\n') if line.strip()]
        
        current_ref = ""
        ref_number = 1
        
        for line in ref_lines:
            if len(references) >= 50:  # Speed limit
                break
                
            # Check if this starts a new reference
            is_new_ref = (
                re.match(r'^\[?\d+\]?\.?\s+', line) or
                (len(current_ref) > 40 and re.match(r'^[A-Z][a-z]+', line))
            )
            
            if is_new_ref and current_ref:
                # Process previous reference
                if len(current_ref) > 20:
                    raw_journal = self._parse_journal_from_reference(current_ref)
                    ref_dict = {
                        "number": str(ref_number),
                        "text": current_ref,
                        "parsed_authors": self._parse_authors_from_reference(current_ref),
                        "parsed_year": self._parse_year_from_reference(current_ref),
                        "parsed_title": self._parse_title_from_reference(current_ref),
                        "parsed_doi": self._parse_doi_from_reference(current_ref),
                        "parsed_journal": raw_journal,
                        "normalized_journal": self._normalize_journal_name(raw_journal),
                        "parsed_volume": self._parse_volume_from_reference(current_ref),
                        "parsed_pages": self._parse_pages_from_reference(current_ref),
                        "reference_type": self._classify_reference_type(current_ref),
                        "citekey": self._generate_reference_citekey({
                            "parsed_authors": self._parse_authors_from_reference(current_ref),
                            "parsed_year": self._parse_year_from_reference(current_ref),
                            "parsed_title": self._parse_title_from_reference(current_ref)
                        })
                    }
                    references.append(ref_dict)
                    ref_number += 1
                current_ref = line
            else:
                # Continuation or start
                if current_ref:
                    current_ref += " " + line
                else:
                    current_ref = line
        
        # Process last reference
        if current_ref and len(current_ref) > 20:
            raw_journal = self._parse_journal_from_reference(current_ref)
            ref_dict = {
                "number": str(ref_number),
                "text": current_ref,
                "parsed_authors": self._parse_authors_from_reference(current_ref),
                "parsed_year": self._parse_year_from_reference(current_ref),
                "parsed_title": self._parse_title_from_reference(current_ref),
                "parsed_doi": self._parse_doi_from_reference(current_ref),
                "parsed_journal": raw_journal,
                "normalized_journal": self._normalize_journal_name(raw_journal),
                "parsed_volume": self._parse_volume_from_reference(current_ref),
                "parsed_pages": self._parse_pages_from_reference(current_ref),
                "reference_type": self._classify_reference_type(current_ref),
                "citekey": self._generate_reference_citekey({
                    "parsed_authors": self._parse_authors_from_reference(current_ref),
                    "parsed_year": self._parse_year_from_reference(current_ref),
                    "parsed_title": self._parse_title_from_reference(current_ref)
                })
            }
            references.append(ref_dict)
        
        return references
    
    def _extract_clean_first_author(self, metadata) -> str:
        """
        Extract and clean the first author name for better citekey generation.
        
        Args:
            metadata: Paper metadata object
            
        Returns:
            Clean first author name
        """
        if not hasattr(metadata, 'authors') or not metadata.authors:
            return "Unknown"
        
        first_author = metadata.authors[0]
        
        # Handle common patterns in author extraction
        # Remove "et al." pattern
        first_author = re.sub(r'\s+et\s+al\.?.*$', '', first_author, flags=re.IGNORECASE)
        
        # Handle filename-based extraction (e.g., "Fukuda et al. - 2014")
        if ' - ' in first_author:
            first_author = first_author.split(' - ')[0].strip()
        
        # Handle comma-separated format: "LastName, FirstName"
        if ',' in first_author:
            parts = first_author.split(',')
            if len(parts) >= 2:
                # Return just the last name
                return parts[0].strip()
        
        # Handle space-separated format: "FirstName LastName" or "FirstName MiddleName LastName"
        parts = first_author.strip().split()
        if len(parts) >= 2:
            # Return the last part as surname
            return parts[-1]
        elif len(parts) == 1:
            # Single name, return as is
            return parts[0]
        
        # Fallback
        return first_author.strip() if first_author else "Unknown"
    
    def _normalize_authors(self, authors: List[str]) -> set:
        """
        Normalize author names for comparison by extracting last names.
        
        Args:
            authors: List of author names
            
        Returns:
            Set of normalized author names (last names)
        """
        normalized = set()
        
        for author in authors:
            if not author or author == "Unknown":
                continue
                
            # Clean the author name
            author_clean = re.sub(r'\s+et\s+al\.?.*$', '', author, flags=re.IGNORECASE)
            author_clean = re.sub(r'\s+-\s+\d{4}.*$', '', author_clean)  # Remove "- 2014" pattern
            
            # Extract last name
            if ',' in author_clean:
                # "LastName, FirstName" format
                last_name = author_clean.split(',')[0].strip()
            else:
                # "FirstName LastName" format - take last word
                parts = author_clean.strip().split()
                last_name = parts[-1] if parts else author_clean
            
            # Normalize: lowercase, remove special characters
            last_name = re.sub(r'[^a-zA-Z]', '', last_name).lower()
            
            if last_name and len(last_name) > 1:  # Avoid single characters
                normalized.add(last_name)
        
        return normalized
    
    def _generate_reference_citekey(self, reference: Dict[str, str]) -> str:
        """
        Generate a consistent citekey for a reference to enable matching across papers.
        
        Args:
            reference: Reference dictionary with parsed metadata
            
        Returns:
            Generated citekey for the reference
        """
        authors = reference.get('parsed_authors', 'Unknown').strip()
        year = reference.get('parsed_year', 'Unknown').strip()
        title = reference.get('parsed_title', reference.get('text', 'Unknown'))[:50]  # First 50 chars
        
        # Clean author name - get first author's last name
        if authors and authors != 'Unknown':
            # Remove reference numbers and clean
            authors_clean = re.sub(r'^\[?\d+\]?\.?\s*', '', authors)
            authors_clean = re.sub(r'\s+et\s+al\.?.*$', '', authors_clean, flags=re.IGNORECASE)
            
            if ',' in authors_clean:
                # "LastName, FirstName" format
                first_author = authors_clean.split(',')[0].strip()
            else:
                # "FirstName LastName" format - take first word as potential first name
                parts = authors_clean.strip().split()
                first_author = parts[-1] if len(parts) > 1 else parts[0] if parts else 'unknown'
            
            # Clean first author name
            first_author = re.sub(r'[^a-zA-Z]', '', first_author).lower()
        else:
            first_author = 'unknown'
        
        # Get first meaningful word from title
        title_words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
        title_word = title_words[0] if title_words else 'paper'
        
        return f"{first_author}{year}{title_word}"
    
    def _build_reference_network(
        self, 
        citation_contexts: List[CitationContext], 
        references: List[Dict[str, str]]
    ) -> Dict[str, any]:
        """
        Build a network representation of reference relationships.
        
        Args:
            citation_contexts: List of citation contexts
            references: List of references
            
        Returns:
            Network dictionary with nodes and edges
        """
        network = {
            "nodes": [],
            "edges": [],
            "clusters": {}
        }
        
        # Create nodes for each reference
        reference_nodes = {}
        for ref in references:
            node_id = f"ref_{ref['number']}"
            reference_nodes[ref['number']] = node_id
            
            network["nodes"].append({
                "id": node_id,
                "label": ref.get("parsed_authors", "Unknown"),
                "type": "reference",
                "year": ref.get("parsed_year", ""),
                "title": ref.get("parsed_title", ""),
                "full_text": ref["text"]
            })
        
        # Create edges based on citation contexts
        context_purposes = {}
        for context in citation_contexts:
            # Try to match citation to reference numbers
            matched_refs = self._match_citation_to_references(context.citation, references)
            
            for ref_num in matched_refs:
                if ref_num in reference_nodes:
                    edge_id = f"cite_{context.id}_{ref_num}"
                    
                    network["edges"].append({
                        "id": edge_id,
                        "source": "current_paper",
                        "target": reference_nodes[ref_num],
                        "type": "citation",
                        "context": context.context,
                        "purpose": context.purpose,
                        "section": context.section
                    })
                    
                    # Track citation purposes for clustering
                    purpose = context.purpose
                    if purpose not in context_purposes:
                        context_purposes[purpose] = []
                    context_purposes[purpose].append(reference_nodes[ref_num])
        
        # Create clusters based on citation purposes
        network["clusters"] = context_purposes
        
        # Add current paper as central node
        network["nodes"].append({
            "id": "current_paper",
            "label": "Current Paper",
            "type": "current_paper",
            "year": "",
            "title": "",
            "full_text": ""
        })
        
        return network
    
    def _determine_citation_purpose(self, sentence: str) -> str:
        """
        Determine the purpose of a citation based on context clues.
        
        Args:
            sentence: Sentence containing the citation
            
        Returns:
            Citation purpose category
        """
        sentence_lower = sentence.lower()
        
        # Supporting evidence patterns
        if any(phrase in sentence_lower for phrase in [
            "as shown by", "demonstrated by", "reported by", "found by",
            "according to", "consistent with", "in agreement with"
        ]):
            return "supporting_evidence"
        
        # Contrasting view patterns
        if any(phrase in sentence_lower for phrase in [
            "however", "in contrast", "unlike", "differs from",
            "contradicts", "challenges", "disputes"
        ]):
            return "contrasting_view"
        
        # Methodology source patterns
        if any(phrase in sentence_lower for phrase in [
            "method", "approach", "technique", "procedure",
            "protocol", "algorithm", "following"
        ]):
            return "methodology_source"
        
        # Background/context patterns
        if any(phrase in sentence_lower for phrase in [
            "previous", "prior", "earlier", "established",
            "known", "background", "context"
        ]):
            return "background_context"
        
        # Comparison patterns
        if any(phrase in sentence_lower for phrase in [
            "similar to", "compared to", "like", "as in",
            "comparable", "analogous"
        ]):
            return "comparison"
        
        return "general_reference"
    
    def _determine_section_context(self, sentence: str, full_content: str) -> str:
        """
        Determine which section of the paper contains this citation.
        
        Args:
            sentence: Sentence containing the citation
            full_content: Full paper content
            
        Returns:
            Section name
        """
        # Find the position of the sentence in the full content
        sentence_pos = full_content.find(sentence)
        if sentence_pos == -1:
            return "unknown"
        
        # Look backwards for section headers
        content_before = full_content[:sentence_pos]
        lines_before = content_before.split('\n')
        
        section_patterns = {
            r'(?i)^(abstract|summary)': 'abstract',
            r'(?i)^(introduction|background)': 'introduction',
            r'(?i)^(methods?|methodology|experimental)': 'methods',
            r'(?i)^(results?|findings?)': 'results',
            r'(?i)^(discussion|analysis)': 'discussion',
            r'(?i)^(conclusion|conclusions?)': 'conclusion',
            r'(?i)^(references?|bibliography)': 'references'
        }
        
        # Check recent lines for section headers
        for line in reversed(lines_before[-20:]):  # Check last 20 lines
            line = line.strip()
            if not line:
                continue
                
            for pattern, section in section_patterns.items():
                if re.match(pattern, line):
                    return section
        
        return "body"
    
    def _match_citation_to_references(
        self, 
        citation: str, 
        references: List[Dict[str, str]]
    ) -> List[str]:
        """
        Match a citation string to reference numbers with enhanced fuzzy matching.
        
        Args:
            citation: Citation text (e.g., "Smith 2020", "[1,2]")
            references: List of reference dictionaries
            
        Returns:
            List of matching reference numbers with confidence scores
        """
        matched_refs = []
        
        # Handle numbered citations like [1], [1-3], [1,2,5]
        number_match = re.match(r'^(\d+(?:[-,\s]*\d+)*)$', citation.strip('[]()'))
        if number_match:
            numbers_str = number_match.group(1)
            
            # Handle ranges like "1-3"
            if '-' in numbers_str:
                parts = numbers_str.split('-')
                if len(parts) == 2:
                    try:
                        start, end = int(parts[0]), int(parts[1])
                        matched_refs.extend([str(i) for i in range(start, end + 1)])
                    except ValueError:
                        pass
            
            # Handle comma-separated like "1,2,5"
            elif ',' in numbers_str:
                numbers = [n.strip() for n in numbers_str.split(',')]
                matched_refs.extend(numbers)
            
            # Single number
            else:
                matched_refs.append(numbers_str.strip())
        
        # Handle author-year citations with fuzzy matching
        else:
            citation_matches = []
            
            for ref in references:
                confidence_score = self._calculate_citation_match_confidence(citation, ref)
                if confidence_score > 0.6:  # Threshold for confident match
                    citation_matches.append((ref["number"], confidence_score))
            
            # Sort by confidence and return best matches
            citation_matches.sort(key=lambda x: x[1], reverse=True)
            matched_refs.extend([match[0] for match in citation_matches[:3]])  # Top 3 matches
        
        return matched_refs
    
    def _calculate_citation_match_confidence(self, citation: str, reference: Dict[str, str]) -> float:
        """
        Calculate confidence score for citation-reference matching using multiple strategies.
        
        Args:
            citation: Citation text
            reference: Reference dictionary with parsed metadata
            
        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.0
        citation_lower = citation.lower()
        
        ref_authors = reference.get("parsed_authors", "")
        ref_year = reference.get("parsed_year", "")
        ref_title = reference.get("parsed_title", "")
        ref_doi = reference.get("parsed_doi", "")
        
        # DOI matching (highest confidence)
        if ref_doi and ref_doi.lower() in citation_lower:
            confidence += 0.9
            return confidence  # DOI match is definitive
        
        # Year matching
        year_in_citation = re.search(r'\b(19|20)\d{2}[a-z]?\b', citation)
        if year_in_citation and ref_year:
            if year_in_citation.group(0)[:4] == ref_year[:4]:
                confidence += 0.3
        
        # Author matching with fuzzy logic
        if ref_authors:
            author_confidence = self._calculate_author_match_confidence(citation_lower, ref_authors.lower())
            confidence += author_confidence * 0.6
        
        # Title word matching (for longer citations)
        if ref_title and len(citation.split()) > 3:
            title_confidence = self._calculate_title_match_confidence(citation_lower, ref_title.lower())
            confidence += title_confidence * 0.2
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _calculate_author_match_confidence(self, citation: str, ref_authors: str) -> float:
        """Calculate confidence score for author name matching"""
        if not ref_authors:
            return 0.0
        
        # Extract potential author names from citation
        citation_words = re.findall(r'\b[A-Za-z]{2,}\b', citation)
        ref_words = re.findall(r'\b[A-Za-z]{2,}\b', ref_authors)
        
        if not citation_words or not ref_words:
            return 0.0
        
        # Check for exact matches
        exact_matches = len([word for word in citation_words if word.lower() in ref_authors])
        if exact_matches > 0:
            base_confidence = exact_matches / len(citation_words)
        else:
            base_confidence = 0.0
        
        # Check for partial matches (first few characters)
        partial_matches = 0
        for cit_word in citation_words:
            if len(cit_word) >= 3:
                for ref_word in ref_words:
                    if (len(ref_word) >= 3 and 
                        cit_word.lower()[:3] == ref_word.lower()[:3]):
                        partial_matches += 0.5
                        break
        
        partial_confidence = partial_matches / len(citation_words) if citation_words else 0
        
        # Check for "et al." pattern
        et_al_bonus = 0.2 if ('et al' in citation and 'et al' in ref_authors) else 0
        
        return min(base_confidence + partial_confidence * 0.5 + et_al_bonus, 1.0)
    
    def _calculate_title_match_confidence(self, citation: str, ref_title: str) -> float:
        """Calculate confidence score for title word matching"""
        if not ref_title or len(citation.split()) < 4:
            return 0.0
        
        # Extract meaningful words (length > 3, not common words)
        stop_words = {'the', 'and', 'for', 'with', 'from', 'this', 'that', 'they', 'have', 'been', 'were'}
        
        citation_words = set([word.lower() for word in re.findall(r'\b[A-Za-z]{4,}\b', citation) 
                             if word.lower() not in stop_words])
        title_words = set([word.lower() for word in re.findall(r'\b[A-Za-z]{4,}\b', ref_title) 
                          if word.lower() not in stop_words])
        
        if not citation_words or not title_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(citation_words.intersection(title_words))
        union = len(citation_words.union(title_words))
        
        return intersection / union if union > 0 else 0.0
    
    def _parse_authors_from_reference(self, ref_text: str) -> str:
        """Extract author names from reference text with improved parsing."""
        if not ref_text:
            return ""
        
        # Remove reference number if present
        clean_text = re.sub(r'^\[?\d+\]?\.?\s*', '', ref_text.strip())
        
        # Method 1: Extract authors before parenthetical year pattern
        paren_year_match = re.search(r'\((\d{4}[a-z]?)\)', clean_text)
        if paren_year_match:
            authors_part = clean_text[:paren_year_match.start()].strip()
            # Clean up common suffixes and validate
            authors_part = re.sub(r'[.,;:]\s*$', '', authors_part)
            if self._validate_author_segment(authors_part):
                return authors_part
        
        # Method 2: Extract authors before standalone year pattern
        year_match = re.search(r'\b(19[5-9]\d|20[0-2]\d)[a-z]?\b', clean_text)
        if year_match:
            # Make sure year isn't part of a DOI or URL
            year_context = clean_text[max(0, year_match.start()-10):year_match.end()+10]
            if not re.search(r'doi|10\.|http', year_context, re.IGNORECASE):
                authors_part = clean_text[:year_match.start()].strip()
                authors_part = re.sub(r'[.,;:]\s*$', '', authors_part)
                if self._validate_author_segment(authors_part):
                    return authors_part
        
        # Method 3: Look for "et al." patterns with preceding author
        et_al_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?)*(?:\s+[a-z]{2,3})?)(?:\s+et\s+al\.?)',  # LastName et al.
            r'([A-Z]\.\s*[A-Z][a-z]+)(?:\s+et\s+al\.?)',  # A. LastName et al.
            r'([A-Z][a-z]+,\s*[A-Z]\.?(?:\s*[A-Z]\.?)*)(?:\s+et\s+al\.?)'  # LastName, A.B. et al.
        ]
        
        for pattern in et_al_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                authors = match.group(1).strip()
                if len(authors) > 2:
                    return authors + " et al."
        
        # Method 4: Extract first segment before period (common format: "Authors. Title. Journal")
        segments = re.split(r'[.;]', clean_text)
        if segments:
            first_segment = segments[0].strip()
            if self._validate_author_segment(first_segment):
                return first_segment
        
        # Method 5: Extract first segment before title-like pattern
        title_indicators = r'\b(?:title|study|analysis|review|investigation|assessment|evaluation|comparison|development)\b'
        title_match = re.search(title_indicators, clean_text, re.IGNORECASE)
        if title_match:
            authors_part = clean_text[:title_match.start()].strip()
            authors_part = re.sub(r'[.,;:]\s*$', '', authors_part)
            if self._validate_author_segment(authors_part):
                return authors_part
        
        # Fallback: return first reasonable segment
        if len(clean_text) > 5:
            first_segment = clean_text[:100].strip()
            first_segment = re.sub(r'[.,;:]\s*$', '', first_segment)
            if self._validate_author_segment(first_segment):
                return first_segment
        
        return "Unknown"
    
    def _validate_author_segment(self, segment: str) -> bool:
        """Validate that a text segment looks like author names"""
        if not segment or len(segment) < 3 or len(segment) > 200:
            return False
        
        # Should have at least one proper name pattern
        if not re.search(r'[A-Z][a-z]{1,}', segment):
            return False
        
        # Exclude common non-author patterns
        exclude_patterns = [
            r'^\d+',  # Starts with numbers
            r'^http|^www|^doi',  # URLs/DOIs
            r'^abstract|^introduction|^keywords',  # Paper sections
            r'^journal|^proceedings|^conference',  # Publication venues
            r'^\d{4}\s',  # Starts with year
            r'^vol\.|^volume|^pp\.|^pages',  # Bibliographic info
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, segment.lower()):
                return False
        
        # Must contain actual letters (not just initials and punctuation)
        if len(re.findall(r'[a-zA-Z]', segment)) < 3:
            return False
        
        return True
    
    def _parse_year_from_reference(self, ref_text: str) -> str:
        """Extract publication year from reference text with improved accuracy."""
        if not ref_text:
            return "Unknown"
        
        # Look for 4-digit years in reasonable range
        year_pattern = r'\b(19[5-9]\d|20[0-2]\d)\b'
        matches = re.findall(year_pattern, ref_text)
        
        if matches:
            # If multiple years found, use contextual clues
            if len(matches) == 1:
                return matches[0]
            
            # Multiple years - prefer the one that appears in typical publication contexts
            for match in matches:
                year_int = int(match)
                # Check if it's in a reasonable publication year range
                if 1950 <= year_int <= 2025:
                    # Look for context clues around the year
                    year_index = ref_text.find(match)
                    context_before = ref_text[max(0, year_index-20):year_index].lower()
                    context_after = ref_text[year_index+4:year_index+24].lower()
                    
                    # Positive indicators for publication year
                    if any(indicator in context_before + context_after for indicator in 
                          ['vol', 'volume', 'pp', 'pages', 'journal', 'proc', 'conf']):
                        return match
            
            # Return the most recent reasonable year
            valid_years = [int(y) for y in matches if 1950 <= int(y) <= 2025]
            if valid_years:
                return str(max(valid_years))
        
        return "Unknown"
    
    def _parse_title_from_reference(self, ref_text: str) -> str:
        """Extract title from reference text with improved parsing."""
        if not ref_text:
            return "Unknown Title"
        
        # Remove reference number
        clean_text = re.sub(r'^\[?\d+\]?\.?\s*', '', ref_text.strip())
        
        # Method 1: Look for title between authors and journal/venue
        # Pattern: "Authors (year) Title. Journal" or "Authors. Title. Journal"
        
        # Split by periods and analyze segments
        segments = [s.strip() for s in clean_text.split('.') if s.strip()]
        
        if len(segments) >= 3:
            # Typical pattern: Authors. Title. Journal/Venue
            potential_title = segments[1]
            
            # Validate it looks like a title
            if (len(potential_title) > 10 and 
                not re.search(r'^\d{4}|^vol|^pp|^page|^in:|^journal', potential_title.lower()) and
                not potential_title.lower().endswith(' press') and
                not potential_title.lower().endswith(' publisher')):
                
                # Clean up the title
                title = re.sub(r'[""'']', '', potential_title)  # Remove quotes
                title = re.sub(r'\s+', ' ', title).strip()  # Normalize whitespace
                
                if len(title) > 5:
                    return title
        
        elif len(segments) >= 2:
            # Try second segment
            potential_title = segments[1]
            if len(potential_title) > 10:
                title = re.sub(r'[""'']', '', potential_title)
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) > 5:
                    return title
        
        # Method 2: Look for quoted titles
        quote_patterns = [
            r'[""'']([^""'']{10,200})[""'']\.?',
            r'"([^"]{10,200})"\.?',
        ]
        
        for pattern in quote_patterns:
            match = re.search(pattern, clean_text)
            if match:
                title = match.group(1).strip()
                if len(title) > 5:
                    return title
        
        # Method 3: Extract title after year pattern
        year_match = re.search(r'\b(19|20)\d{2}\b[a-z]?\.?\s*([^.]{10,200})', clean_text)
        if year_match:
            potential_title = year_match.group(2).strip()
            # Make sure it's not journal info
            if not re.search(r'^(in|journal|proc|conf|vol|pp)', potential_title.lower()):
                title = re.sub(r'[""'']', '', potential_title)
                title = re.sub(r'\s+', ' ', title).strip()
                if len(title) > 5:
                    return title
        
        # Method 4: Heuristic - find the longest segment that looks like a title
        for segment in segments:
            if (len(segment) > 15 and 
                len(segment) < 300 and
                not re.search(r'^\d{4}|^pp\.|^vol|^journal|^in:|http|www|doi', segment.lower()) and
                segment.count(' ') >= 2):  # Has multiple words
                
                title = re.sub(r'[""'']', '', segment)
                title = re.sub(r'\s+', ' ', title).strip()
                return title
        
        # Fallback: return first reasonable segment
        for segment in segments[:3]:
            if len(segment) > 5 and not re.search(r'^\d{4}|^vol|^pp', segment.lower()):
                return segment[:100]  # Limit length
        
        return "Unknown Title"
    
    def _parse_doi_from_reference(self, ref_text: str) -> str:
        """Extract DOI from reference text using enhanced patterns"""
        if not ref_text:
            return ""
        
        # Enhanced DOI patterns specifically for reference lists
        doi_patterns = [
            # Standard DOI patterns
            r'doi:?\s*(10\.\d+/[^\s,\]\)]+)',
            r'DOI:?\s*(10\.\d+/[^\s,\]\)]+)',
            
            # URL format DOIs
            r'https?://(?:dx\.)?doi\.org/(10\.\d+/[^\s,\]\)]+)',
            r'https?://doi\.org/(10\.\d+/[^\s,\]\)]+)',
            
            # Bare DOI patterns (more restrictive)
            r'\b(10\.\d{4,}/[A-Za-z0-9\-\._\(\)/]+)',
            
            # DOI in parentheses or at end of reference
            r'\(doi:?\s*(10\.\d+/[^\s,\)\]]+)\)',
            r'\.\s+doi:?\s*(10\.\d+/[^\s,\]\)]+)',
            
            # DOI with assignment operators
            r'doi\s*[:=]\s*(10\.\d+/[^\s,\]\)]+)',
            r'DOI\s*[:=]\s*(10\.\d+/[^\s,\]\)]+)'
        ]
        
        for pattern in doi_patterns:
            match = re.search(pattern, ref_text, re.IGNORECASE)
            if match:
                doi = match.group(1)
                # Clean and validate DOI
                cleaned_doi = self._clean_and_validate_doi(doi)
                if cleaned_doi:
                    return cleaned_doi
        
        return ""
    
    def _parse_journal_from_reference(self, ref_text: str) -> str:
        """Extract journal name from reference text"""
        if not ref_text:
            return ""
        
        # Remove reference number and author info
        clean_text = re.sub(r'^\[?\d+\]?\.?\s*', '', ref_text.strip())
        
        # Common journal patterns in references
        journal_patterns = [
            # After title, before volume/year
            r'[."""]\s*([A-Za-z][A-Za-z\s&:.-]{5,80}?)\s+(?:vol\.?|volume|\d+|pp\.?|\()',
            
            # Journal name followed by volume/issue
            r'[."""]\s*([A-Za-z][A-Za-z\s&:.-]{5,80}?)\s*,?\s*(?:vol\.?\s*\d+|\d+\s*\(\d+\))',
            
            # Common journal indicators
            r'[."""]\s*([A-Za-z][A-Za-z\s&:.-]*(?:Journal|Review|Letters|Proceedings|Nature|Science|Cell)[A-Za-z\s&:.-]*)',
            
            # After "In:" for conference proceedings
            r'In:?\s*([A-Za-z][A-Za-z\s&:.-]{5,80}?)(?:\.|,|\s+\d)',
        ]
        
        for pattern in journal_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                journal = match.group(1).strip()
                # Clean up journal name
                journal = re.sub(r'^[,.:;]|[,.:;]$', '', journal).strip()
                journal = re.sub(r'\s+', ' ', journal)
                
                # Validate journal name (reasonable length, not just numbers/punctuation)
                if 5 <= len(journal) <= 100 and re.search(r'[A-Za-z]{3,}', journal):
                    return journal
        
        return ""
    
    def _normalize_journal_name(self, journal_name: str) -> str:
        """Normalize and standardize journal names"""
        if not journal_name:
            return ""
        
        # Common journal name normalizations
        journal_mappings = {
            # Nature family
            'nature': 'Nature',
            'nat comms': 'Nature Communications',
            'nat commun': 'Nature Communications', 
            'nature communications': 'Nature Communications',
            'nat meth': 'Nature Methods',
            'nature methods': 'Nature Methods',
            'nat biotechnol': 'Nature Biotechnology',
            'nature biotechnology': 'Nature Biotechnology',
            
            # Science family
            'science': 'Science',
            'sci adv': 'Science Advances',
            'science advances': 'Science Advances',
            'sci transl med': 'Science Translational Medicine',
            'science translational medicine': 'Science Translational Medicine',
            
            # Cell family
            'cell': 'Cell',
            'cell rep': 'Cell Reports',
            'cell reports': 'Cell Reports',
            
            # PNAS
            'proc natl acad sci usa': 'Proceedings of the National Academy of Sciences',
            'proc natl acad sci': 'Proceedings of the National Academy of Sciences',
            'pnas': 'Proceedings of the National Academy of Sciences',
            
            # Physical chemistry
            'j phys chem': 'Journal of Physical Chemistry',
            'j phys chem b': 'Journal of Physical Chemistry B',
            'j phys chem lett': 'Journal of Physical Chemistry Letters',
            'jpcb': 'Journal of Physical Chemistry B',
            'jpcl': 'Journal of Physical Chemistry Letters',
            
            # Biophysics
            'biophys j': 'Biophysical Journal',
            'biophysical journal': 'Biophysical Journal',
            'j mol biol': 'Journal of Molecular Biology',
            'journal of molecular biology': 'Journal of Molecular Biology',
            
            # Biochemistry
            'biochemistry': 'Biochemistry',
            'j biol chem': 'Journal of Biological Chemistry',
            'journal of biological chemistry': 'Journal of Biological Chemistry',
            'jbc': 'Journal of Biological Chemistry',
        }
        
        # Normalize to lowercase for matching
        journal_lower = journal_name.lower().strip()
        
        # Remove common prefixes and suffixes
        journal_lower = re.sub(r'^the\s+', '', journal_lower)
        journal_lower = re.sub(r'\s+journal$', '', journal_lower)
        journal_lower = re.sub(r'^journal\s+of\s+', 'j ', journal_lower)
        
        # Check for exact matches in mappings
        if journal_lower in journal_mappings:
            return journal_mappings[journal_lower]
        
        # Check for partial matches
        for pattern, standard_name in journal_mappings.items():
            if pattern in journal_lower or journal_lower in pattern:
                return standard_name
        
        # If no mapping found, return cleaned version with proper capitalization
        return self._capitalize_journal_name(journal_name)
    
    def _capitalize_journal_name(self, journal_name: str) -> str:
        """Apply proper capitalization to journal names"""
        if not journal_name:
            return ""
        
        # Words that should remain lowercase (prepositions, articles, conjunctions)
        lowercase_words = {'of', 'the', 'and', 'for', 'in', 'on', 'at', 'to', 'by', 'with', 'from'}
        
        words = journal_name.split()
        capitalized_words = []
        
        for i, word in enumerate(words):
            word = word.lower()
            # Capitalize first word, proper nouns, and words not in lowercase set
            if i == 0 or word not in lowercase_words or len(word) < 3:
                capitalized_words.append(word.capitalize())
            else:
                capitalized_words.append(word)
        
        return ' '.join(capitalized_words)
    
    def _classify_reference_type(self, ref_text: str) -> str:
        """Classify the type of reference (journal article, conference paper, book, etc.)"""
        if not ref_text:
            return "unknown"
        
        ref_lower = ref_text.lower()
        
        # Book patterns
        book_indicators = [
            r'\bpress\b', r'\bpublisher\b', r'\bpublishing\b', r'\bbook\b',
            r'\bedition\b', r'\bchapter\b', r'\bpp\.\s*\d+-\d+.*\d{4}',
            r'\bisbn\b', r'\b\d+th\s+edition\b'
        ]
        
        for pattern in book_indicators:
            if re.search(pattern, ref_lower):
                # Further classify books
                if re.search(r'\bchapter\b', ref_lower):
                    return "book_chapter"
                return "book"
        
        # Conference/proceedings patterns
        conference_indicators = [
            r'\bproceedings\b', r'\bproc\.\s+of\b', r'\bconference\b', r'\bconf\.\b',
            r'\bsymposium\b', r'\bworkshop\b', r'\bmeeting\b', r'\bcongress\b',
            r'\binternational\s+conference\b', r'\bieee\b.*\bconference\b'
        ]
        
        for pattern in conference_indicators:
            if re.search(pattern, ref_lower):
                return "conference_paper"
        
        # Thesis patterns
        thesis_indicators = [
            r'\bthesis\b', r'\bdissertation\b', r'\bphd\b.*\bthesis\b',
            r'\bmaster.*thesis\b', r'\bms\s+thesis\b'
        ]
        
        for pattern in thesis_indicators:
            if re.search(pattern, ref_lower):
                return "thesis"
        
        # Patent patterns
        patent_indicators = [
            r'\bpatent\b', r'\bus\s+patent\b', r'\bpatent\s+no\b'
        ]
        
        for pattern in patent_indicators:
            if re.search(pattern, ref_lower):
                return "patent"
        
        # Web/online resource patterns
        web_indicators = [
            r'\bhttp\b', r'\bwww\b', r'\burl\b', r'\bonline\b', r'\bwebsite\b',
            r'\bavailable\s+at\b'
        ]
        
        for pattern in web_indicators:
            if re.search(pattern, ref_lower):
                return "web_resource"
        
        # Preprint patterns
        preprint_indicators = [
            r'\barxiv\b', r'\bbiorxiv\b', r'\bmedrxiv\b', r'\bpreprint\b'
        ]
        
        for pattern in preprint_indicators:
            if re.search(pattern, ref_lower):
                return "preprint"
        
        # Journal article indicators (default for academic references)
        journal_indicators = [
            r'\bjournal\b', r'\bj\.\s+\w+', r'\bnature\b', r'\bscience\b',
            r'\bcell\b', r'\bvol\.\s*\d+', r'\bvolume\s+\d+',
            r'\bpp\.\s*\d+-\d+', r'\bpages\s+\d+-\d+',
            r'\bissn\b', r'\bdoi\s*:\s*10\.'
        ]
        
        for pattern in journal_indicators:
            if re.search(pattern, ref_lower):
                return "journal_article"
        
        # If has typical journal citation format (Author. Title. Journal Vol:Pages Year)
        if re.search(r'\.\s+\d+\s*[(:]\d*[-–]\d+', ref_text):
            return "journal_article"
        
        # Default classification
        return "journal_article"
    
    def _parse_volume_from_reference(self, ref_text: str) -> str:
        """Extract volume information from reference text"""
        if not ref_text:
            return ""
        
        # Volume patterns
        volume_patterns = [
            r'(?:vol\.?|volume)\s*(\d+)',
            r'\b(\d+)\s*\(\d+\)',  # Volume(issue)
            r'[,.\s]\s*(\d+)\s*[:,-]\s*\d+[-–]\d+',  # Vol:pages pattern
        ]
        
        for pattern in volume_patterns:
            match = re.search(pattern, ref_text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ""
    
    def _parse_pages_from_reference(self, ref_text: str) -> str:
        """Extract page information from reference text"""
        if not ref_text:
            return ""
        
        # Page patterns
        page_patterns = [
            r'(?:pp?\.?|pages?)\s*([\d-–]+)',
            r'\b(\d+)\s*[-–]\s*(\d+)',  # page-page
            r'[,:\s]\s*([\d]+-[\d]+)',  # Simple page range
        ]
        
        for pattern in page_patterns:
            match = re.search(pattern, ref_text, re.IGNORECASE)
            if match:
                if match.groups() and len(match.groups()) > 1:
                    # Handle multiple groups (start-end pages)
                    return f"{match.group(1)}-{match.group(2)}"
                else:
                    return match.group(1)
        
        return ""
    
    def _clean_and_validate_doi(self, doi: str) -> Optional[str]:
        """Clean and validate DOI format (reused from metadata_extractor logic)"""
        if not doi:
            return None
        
        # Remove common prefixes and suffixes
        doi = re.sub(r'^(?:doi:|DOI:)\s*', '', doi, flags=re.IGNORECASE)
        doi = re.sub(r'^(?:https?://)?(?:dx\.)?doi\.org/', '', doi, flags=re.IGNORECASE)
        
        # Remove trailing punctuation that's not part of DOI
        doi = re.sub(r'[.,;:\]\)\s]+$', '', doi)
        
        # Basic DOI format validation: should start with 10. and have reasonable length
        if re.match(r'^10\.\d{4,}/[^\s]{6,}$', doi) and len(doi) < 200:
            return doi
        
        return None
    
    async def create_batch_citemap(
        self,
        input_path: Path,
        options: ProcessingOptions
    ) -> Dict[str, any]:
        """
        Create citation context maps for multiple PDFs and generate a comprehensive
        cross-reference analysis showing how papers cite each other and common sources.
        
        Args:
            input_path: Path to directory containing PDF files
            options: Processing configuration options
            
        Returns:
            Dictionary containing batch citemap results and metadata
        """
        try:
            logger.info(f"Starting batch citemap analysis for directory: {input_path}")
            
            # Find all PDF files in the directory
            pdf_files = list(input_path.glob("*.pdf"))
            
            if not pdf_files:
                return {
                    "success": False,
                    "error": f"No PDF files found in directory: {input_path}"
                }
            
            logger.info(f"Found {len(pdf_files)} PDF files for citemap analysis")
            
            # Process PDFs in smaller batches with checkpoints
            all_references = {}  # Track all references across papers
            all_citation_contexts = []
            processed_count = 0
            
            # Process in batches of 5 papers for better memory management
            batch_size = 5
            for batch_start in range(0, len(pdf_files), batch_size):
                batch_end = min(batch_start + batch_size, len(pdf_files))
                batch_files = pdf_files[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start//batch_size + 1}: papers {batch_start + 1}-{batch_end}")
                
                for pdf_path in batch_files:
                    logger.info(f"Processing citemap for: {pdf_path.name}")
                    
                    try:
                        # Extract references and contexts - optimized processing
                        content = self.pdf_processor.extract_text(str(pdf_path))
                        metadata = self.pdf_processor.extract_metadata(str(pdf_path))
                        # Improve author extraction for better citekeys
                        first_author = self._extract_clean_first_author(metadata)
                        citekey = generate_citekey(
                            first_author,
                            metadata.year if hasattr(metadata, 'year') else None,
                            metadata.title if hasattr(metadata, 'title') else "Unknown Title"
                        )
                        
                        # Fast citation extraction (simplified for speed)
                        citation_contexts = self._extract_citation_contexts_fast(content)
                        references = self._extract_references_fast(content)
                        
                        # Store for cross-analysis
                        all_references[citekey] = {
                            "paper_info": {
                                "title": metadata.title if hasattr(metadata, 'title') else "Unknown Title",
                                "authors": metadata.authors if hasattr(metadata, 'authors') else ["Unknown Author"],
                                "year": metadata.year if hasattr(metadata, 'year') else "Unknown Year",
                                "citekey": citekey
                            },
                            "references": references,
                            "citation_contexts": citation_contexts
                        }
                        
                        all_citation_contexts.extend([
                            {**ctx.__dict__, "source_paper": citekey} 
                            for ctx in citation_contexts
                        ])
                        
                        processed_count += 1
                        logger.info(f"Successfully processed {pdf_path.name} ({processed_count}/{len(pdf_files)})")
                        
                    except Exception as e:
                        logger.warning(f"Failed to process {pdf_path.name}: {str(e)}")
                
                # Checkpoint: Save intermediate results every batch
                if processed_count >= batch_size:
                    logger.info(f"Checkpoint: {processed_count} papers processed, generating intermediate analysis...")
            
            # Perform cross-reference analysis
            cross_analysis = self._perform_cross_reference_analysis(all_references)
            
            # Generate comprehensive batch citemap
            batch_data = {
                "batch_info": {
                    "total_papers": len(pdf_files),
                    "processed_papers": processed_count,
                    "failed_papers": len(pdf_files) - processed_count,
                    "total_references": sum(len(data["references"]) for data in all_references.values()),
                    "total_citation_contexts": len(all_citation_contexts),
                    "input_directory": str(input_path),
                    "analysis_timestamp": get_current_timestamp()
                },
                "papers": [data["paper_info"] for data in all_references.values()],
                "cross_reference_analysis": cross_analysis,
                "top_cited_papers": self._identify_top_cited_papers(all_references),
                "common_sources": self._identify_common_sources(all_references),
                "citation_patterns": self._analyze_citation_patterns(all_citation_contexts),
                "intellectual_lineage": self._trace_intellectual_lineage(all_references),
                "reference_network": self._build_cross_paper_network(all_references)
            }
            
            # Load and render batch template
            template = self.template_processor.load_template("citemap_batch")
            rendered_content = self.template_processor.render_template(
                template, 
                batch_data
            )
            
            # Generate batch output filename with consistent pattern
            if hasattr(options, 'keyword') and options.keyword:
                safe_keyword = "".join(c for c in options.keyword if c.isalnum() or c in ('_', '-'))
                output_filename = f"{safe_keyword}_{processed_count}_citemap.md"
            else:
                folder_name = input_path.name if hasattr(input_path, 'name') else str(input_path).split('/')[-1]
                safe_folder_name = "".join(c for c in folder_name if c.isalnum() or c in ('_', '-'))
                output_filename = f"{safe_folder_name}_{processed_count}_citemap.md"
            output_path = Path(options.output_dir) / output_filename
            
            # Write batch output file
            output_path.write_text(rendered_content, encoding="utf-8")
            
            # Generate interactive network visualization
            try:
                network_html_path = self._generate_interactive_network(all_references, output_path)
                logger.info(f"Interactive network visualization generated: {network_html_path}")
            except ImportError as e:
                logger.warning(f"Could not generate interactive network visualization - missing dependencies: {e}")
                network_html_path = None
            except Exception as e:
                logger.warning(f"Failed to generate interactive network visualization: {e}")
                network_html_path = None
            
            logger.info(f"Batch citemap analysis completed: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
                "batch_summary": {
                    "total_papers": len(pdf_files),
                    "processed_papers": processed_count,
                    "total_references": batch_data["batch_info"]["total_references"],
                    "total_citation_contexts": batch_data["batch_info"]["total_citation_contexts"],
                    "common_sources_found": len(batch_data["common_sources"]),
                    "cross_references_identified": len(cross_analysis["direct_cross_references"])
                }
            }
            
        except Exception as e:
            logger.error(f"Error in batch citemap processing: {str(e)}")
            return {
                "success": False,
                "error": f"Batch citemap processing failed: {str(e)}"
            }
    
    def _perform_cross_reference_analysis(self, all_references: Dict[str, Dict]) -> Dict[str, any]:
        """
        Analyze cross-references between papers in the batch.
        
        Args:
            all_references: Dictionary of all paper references keyed by citekey
            
        Returns:
            Cross-reference analysis results
        """
        cross_analysis = {
            "direct_cross_references": [],
            "indirect_connections": [],
            "citation_chains": [],
            "author_networks": {}
        }
        
        paper_keys = list(all_references.keys())
        
        # Find direct cross-references (papers citing each other)
        for i, paper1_key in enumerate(paper_keys):
            paper1 = all_references[paper1_key]
            
            for j, paper2_key in enumerate(paper_keys):
                if i >= j:  # Avoid duplicates and self-references
                    continue
                    
                paper2 = all_references[paper2_key]
                
                # Check if paper1 cites paper2 or vice versa
                paper1_cites_paper2 = self._check_paper_citations(paper1, paper2["paper_info"])
                paper2_cites_paper1 = self._check_paper_citations(paper2, paper1["paper_info"])
                
                if paper1_cites_paper2 or paper2_cites_paper1:
                    cross_analysis["direct_cross_references"].append({
                        "paper1": paper1["paper_info"],
                        "paper2": paper2["paper_info"],
                        "paper1_cites_paper2": paper1_cites_paper2,
                        "paper2_cites_paper1": paper2_cites_paper1,
                        "bidirectional": paper1_cites_paper2 and paper2_cites_paper1
                    })
        
        return cross_analysis
    
    def _check_paper_citations(self, citing_paper: Dict, cited_paper_info: Dict) -> bool:
        """
        Check if one paper cites another based on author names and year.
        
        Args:
            citing_paper: Paper that might be doing the citing
            cited_paper_info: Information about potentially cited paper
            
        Returns:
            True if citing_paper appears to cite cited_paper_info
        """
        cited_authors = cited_paper_info.get("authors", [])
        cited_year = str(cited_paper_info.get("year", ""))
        
        if not cited_authors or not cited_year:
            return False
        
        # Get primary author surname
        primary_author = cited_authors[0] if cited_authors else ""
        author_surname = primary_author.split()[-1] if primary_author else ""
        
        # Check citation contexts for mentions of this author and year
        for context in citing_paper.get("citation_contexts", []):
            context_text = context.context.lower()
            if author_surname.lower() in context_text and cited_year in context_text:
                return True
        
        # Check references list
        for ref in citing_paper.get("references", []):
            ref_text = ref["text"].lower()
            if author_surname.lower() in ref_text and cited_year in ref_text:
                return True
        
        return False
    
    def _identify_common_sources(self, all_references: Dict[str, Dict]) -> List[Dict]:
        """
        Identify sources that are commonly cited across multiple papers.
        
        Args:
            all_references: Dictionary of all paper references
            
        Returns:
            List of common sources with citation frequency
        """
        # Track references by author-year combination
        reference_frequency = {}
        
        for paper_key, paper_data in all_references.items():
            for ref in paper_data["references"]:
                author = ref.get("parsed_authors", "").lower().strip()
                year = ref.get("parsed_year", "").strip()
                
                if author and year:
                    key = f"{author}_{year}"
                    
                    if key not in reference_frequency:
                        reference_frequency[key] = {
                            "author": ref.get("parsed_authors", ""),
                            "year": year,
                            "title": ref.get("parsed_title", ""),
                            "cited_by": [],
                            "citation_count": 0
                        }
                    
                    reference_frequency[key]["cited_by"].append({
                        "paper": paper_data["paper_info"]["citekey"],
                        "title": paper_data["paper_info"]["title"]
                    })
                    reference_frequency[key]["citation_count"] += 1
        
        # Return sources cited by multiple papers, sorted by frequency
        common_sources = [
            source for source in reference_frequency.values() 
            if source["citation_count"] > 1
        ]
        
        return sorted(common_sources, key=lambda x: x["citation_count"], reverse=True)
    
    def _analyze_citation_patterns(self, all_citation_contexts: List[Dict]) -> Dict[str, any]:
        """
        Analyze patterns in how citations are used across all papers.
        
        Args:
            all_citation_contexts: List of all citation contexts from all papers
            
        Returns:
            Citation pattern analysis
        """
        patterns = {
            "purpose_distribution": {},
            "section_distribution": {},
            "common_citation_phrases": [],
            "citation_density_by_section": {}
        }
        
        # Analyze citation purposes
        for context in all_citation_contexts:
            purpose = context.get("purpose", "unknown")
            patterns["purpose_distribution"][purpose] = patterns["purpose_distribution"].get(purpose, 0) + 1
            
            section = context.get("section", "unknown")
            patterns["section_distribution"][section] = patterns["section_distribution"].get(section, 0) + 1
        
        # Calculate percentages
        total_contexts = len(all_citation_contexts)
        if total_contexts > 0:
            for purpose in patterns["purpose_distribution"]:
                count = patterns["purpose_distribution"][purpose]
                patterns["purpose_distribution"][purpose] = {
                    "count": count,
                    "percentage": round((count / total_contexts) * 100, 1)
                }
            
            for section in patterns["section_distribution"]:
                count = patterns["section_distribution"][section]
                patterns["section_distribution"][section] = {
                    "count": count,
                    "percentage": round((count / total_contexts) * 100, 1)
                }
        
        return patterns
    
    def _trace_intellectual_lineage(self, all_references: Dict[str, Dict]) -> Dict[str, any]:
        """
        Trace intellectual lineage by finding citation chains between papers.
        
        Args:
            all_references: Dictionary of all paper references
            
        Returns:
            Intellectual lineage analysis
        """
        lineage = {
            "citation_chains": [],
            "foundational_works": [],
            "recent_developments": []
        }
        
        # Find papers that cite earlier papers in the collection
        papers_by_year = {}
        for paper_key, paper_data in all_references.items():
            year = paper_data["paper_info"].get("year", "Unknown")
            if year != "Unknown":
                try:
                    year_int = int(year)
                    if year_int not in papers_by_year:
                        papers_by_year[year_int] = []
                    papers_by_year[year_int].append(paper_data)
                except ValueError:
                    pass
        
        # Identify foundational works (older papers cited by newer ones)
        sorted_years = sorted(papers_by_year.keys())
        if len(sorted_years) > 1:
            early_years = sorted_years[:len(sorted_years)//2]
            late_years = sorted_years[len(sorted_years)//2:]
            
            for early_year in early_years:
                for early_paper in papers_by_year[early_year]:
                    citation_count = 0
                    cited_by = []
                    
                    for late_year in late_years:
                        for late_paper in papers_by_year[late_year]:
                            if self._check_paper_citations(late_paper, early_paper["paper_info"]):
                                citation_count += 1
                                cited_by.append(late_paper["paper_info"]["citekey"])
                    
                    if citation_count > 0:
                        lineage["foundational_works"].append({
                            "paper": early_paper["paper_info"],
                            "cited_by_count": citation_count,
                            "cited_by": cited_by
                        })
        
        return lineage
    
    def _build_cross_paper_network(self, all_references: Dict[str, Dict]) -> Dict[str, any]:
        """
        Build a network representation showing relationships between papers.
        
        Args:
            all_references: Dictionary of all paper references
            
        Returns:
            Cross-paper network data
        """
        network = {
            "nodes": [],
            "edges": [],
            "clusters": {}
        }
        
        # Add nodes for each paper
        for paper_key, paper_data in all_references.items():
            network["nodes"].append({
                "id": paper_key,
                "label": paper_data["paper_info"]["title"][:50] + "...",
                "type": "paper",
                "year": paper_data["paper_info"]["year"],
                "authors": paper_data["paper_info"]["authors"],
                "citation_count": len(paper_data["citation_contexts"]),
                "reference_count": len(paper_data["references"])
            })
        
        # Add edges for cross-references
        paper_keys = list(all_references.keys())
        for i, paper1_key in enumerate(paper_keys):
            paper1 = all_references[paper1_key]
            
            for j, paper2_key in enumerate(paper_keys):
                if i == j:  # Skip self-references
                    continue
                
                paper2 = all_references[paper2_key]
                
                if self._check_paper_citations(paper1, paper2["paper_info"]):
                    network["edges"].append({
                        "id": f"{paper1_key}_cites_{paper2_key}",
                        "source": paper1_key,
                        "target": paper2_key,
                        "type": "citation",
                        "weight": 1
                    })
        
        return network
    
    def _generate_interactive_network(
        self, 
        all_references: Dict[str, Dict], 
        output_path: Path,
        filter_isolated_nodes: bool = None
    ) -> str:
        """
        Generate enhanced network visualization with author groupings and optional isolated node filtering.
        
        Args:
            all_references: Dictionary of all paper references
            output_path: Base path for output files
            filter_isolated_nodes: Whether to filter out isolated nodes. If None, auto-filter when >1000 nodes
            
        Returns:
            Path to generated HTML network file
        """
        # Create NetworkX graph
        G = nx.Graph()  # Use undirected graph for better author clustering
        
        # Add paper nodes only
        paper_data = {}
        
        for paper_key, paper_info in all_references.items():
            metadata = paper_info["paper_info"]
            authors = metadata.get("authors", ["Unknown"])
            year = metadata.get("year", "Unknown")
            
            try:
                year_int = int(year) if year != "Unknown" else 2000
            except (ValueError, TypeError):
                year_int = 2000
                
            # Node attributes for papers (including Zotero metadata)
            node_attrs = {
                'title': metadata.get("title", "Unknown Title"),
                'authors': authors,
                'authors_str': ", ".join(authors),
                'year': year_int,
                'citation_count': len(paper_info.get("citation_contexts", [])),
                'reference_count': len(paper_info.get("references", [])),
                'size': min(max(len(paper_info.get("citation_contexts", [])), 8), 30),
                'color_year': year_int,
                # Zotero metadata
                'zotero_key': metadata.get("zotero_key"),
                'zotero_url': metadata.get("zotero_url"),
                'zotero_tags': metadata.get("zotero_tags", []),
                'zotero_collections': metadata.get("zotero_collections", []),
                'collection_primary': metadata.get("zotero_collections", [""])[0] if metadata.get("zotero_collections") else None
            }
            
            G.add_node(paper_key, **node_attrs)
            paper_data[paper_key] = node_attrs
        
        # Add edges between papers that share authors
        papers_list = list(all_references.keys())
        for i, paper1 in enumerate(papers_list):
            for j, paper2 in enumerate(papers_list[i+1:], i+1):
                authors1 = paper_data[paper1]['authors']
                authors2 = paper_data[paper2]['authors']
                
                # Normalize author names for comparison
                normalized_authors1 = self._normalize_authors(authors1)
                normalized_authors2 = self._normalize_authors(authors2)
                
                shared_authors = normalized_authors1.intersection(normalized_authors2)
                
                if shared_authors:
                    # Weight based on number of shared authors
                    weight = len(shared_authors)
                    G.add_edge(paper1, paper2, weight=weight, edge_type='shared_author')
                    logger.debug(f"Added shared author edge between {paper1} and {paper2}: {shared_authors}")
        
        # Add citation edges between papers  
        for i, (paper1_key, paper1_data) in enumerate(all_references.items()):
            for j, (paper2_key, paper2_data) in enumerate(all_references.items()):
                if i != j and self._check_paper_citations(paper1_data, paper2_data["paper_info"]):
                    # If there's already a shared author edge, increase its weight
                    if G.has_edge(paper1_key, paper2_key):
                        G[paper1_key][paper2_key]['weight'] += 2
                        G[paper1_key][paper2_key]['edge_type'] = 'both_citation_and_shared_author'
                    else:
                        G.add_edge(paper1_key, paper2_key, weight=2, edge_type='citation')
        
        # Determine whether to filter isolated nodes
        isolated_nodes = list(nx.isolates(G))
        total_nodes = len(G.nodes())
        
        # Auto-filter if not specified and over 1000 nodes
        if filter_isolated_nodes is None:
            filter_isolated_nodes = total_nodes > 1000
            
        if filter_isolated_nodes and isolated_nodes:
            G.remove_nodes_from(isolated_nodes)
            logger.info(f"Network created: {len(G.nodes())} nodes, {len(G.edges())} edges. Filtered out {len(isolated_nodes)} isolated nodes.")
            isolated_nodes = []  # Clear the list since they're removed
        else:
            connected_nodes = total_nodes - len(isolated_nodes)
            logger.info(f"Network created: {total_nodes} nodes, {len(G.edges())} edges. {connected_nodes} connected nodes, {len(isolated_nodes)} isolated nodes.")
        
        # Generate layout with special handling for isolated nodes
        if len(G.edges()) > 0:
            # Use spring layout for connected components
            try:
                pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
            except:
                # Fallback to random layout if spring layout fails
                pos = nx.random_layout(G, seed=42)
        else:
            # If no edges, arrange all nodes in a circle
            pos = nx.circular_layout(G)
            
        # Adjust isolated nodes to be arranged in a grid pattern at the bottom
        if isolated_nodes:
            import math
            grid_cols = math.ceil(math.sqrt(len(isolated_nodes)))
            for i, node in enumerate(isolated_nodes):
                row = i // grid_cols
                col = i % grid_cols
                # Position isolated nodes in a grid below the main network
                pos[node] = (col * 0.3 - (grid_cols * 0.15), -2.0 - row * 0.4)
        
        # Create edge traces with different styles for different edge types
        edge_traces = []
        
        # Group edges by type
        edge_groups = {'citation': [], 'shared_author': [], 'both_citation_and_shared_author': []}
        
        for edge in G.edges(data=True):
            edge_type = edge[2].get('edge_type', 'shared_author')
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_groups[edge_type].append((x0, x1, y0, y1))
        
        # Citation edges (red)
        if edge_groups['citation']:
            edge_x, edge_y = [], []
            for x0, x1, y0, y1 in edge_groups['citation']:
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_traces.append(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=3, color='red'),
                hoverinfo='none',
                mode='lines',
                name='Citations'
            ))
        
        # Shared author edges (blue)
        if edge_groups['shared_author']:
            edge_x, edge_y = [], []
            for x0, x1, y0, y1 in edge_groups['shared_author']:
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_traces.append(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='blue'),
                hoverinfo='none',
                mode='lines',
                name='Shared Authors'
            ))
        
        # Both citation and shared author edges (purple, thicker)
        if edge_groups['both_citation_and_shared_author']:
            edge_x, edge_y = [], []
            for x0, x1, y0, y1 in edge_groups['both_citation_and_shared_author']:
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_traces.append(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=4, color='purple'),
                hoverinfo='none',
                mode='lines',
                name='Citations + Shared Authors'
            ))
        
        # Create connected and isolated paper node traces separately
        connected_nodes = [node for node in G.nodes() if node not in isolated_nodes]
        
        # Connected paper nodes
        connected_x, connected_y, connected_colors, connected_sizes, connected_text, connected_hover = [], [], [], [], [], []
        
        for node in connected_nodes:
            x, y = pos[node]
            node_data = paper_data[node]
            
            connected_x.append(x)
            connected_y.append(y)
            connected_colors.append(node_data['color_year'])
            connected_sizes.append(node_data['size'])
            connected_text.append(node)  # Show citekey

            # Build hover text with Zotero metadata
            hover_text = (
                f"<b>{node_data['title']}</b><br>"
                f"Authors: {node_data['authors_str']}<br>"
                f"Year: {node_data['year']}<br>"
                f"Citations in text: {node_data['citation_count']}<br>"
                f"References: {node_data['reference_count']}<br>"
            )

            # Add Zotero metadata to tooltip if available
            if node_data.get('zotero_key'):
                hover_text += f"<br><b>Zotero:</b><br>"
                if node_data.get('zotero_collections'):
                    hover_text += f"Collections: {', '.join(node_data['zotero_collections'])}<br>"
                if node_data.get('zotero_tags'):
                    hover_text += f"Tags: {', '.join(node_data['zotero_tags'][:5])}<br>"
                hover_text += f'<a href="{node_data["zotero_url"]}" target="_blank">Open in Zotero</a><br>'

            hover_text += f"Node ID: {node}"
            connected_hover.append(hover_text)
        
        # Isolated paper nodes (if not filtered out)
        isolated_x, isolated_y, isolated_colors, isolated_sizes, isolated_text, isolated_hover = [], [], [], [], [], []
        
        for node in isolated_nodes:
            if node in pos:  # Only include if position was calculated
                x, y = pos[node]
                node_data = paper_data[node]
                
                isolated_x.append(x)
                isolated_y.append(y)
                isolated_colors.append(node_data['color_year'])
                isolated_sizes.append(node_data['size'])
                isolated_text.append(node)  # Show citekey

                # Build hover text with Zotero metadata for isolated nodes
                hover_text = (
                    f"<b>{node_data['title']}</b><br>"
                    f"Authors: {node_data['authors_str']}<br>"
                    f"Year: {node_data['year']}<br>"
                    f"Citations in text: {node_data['citation_count']}<br>"
                    f"References: {node_data['reference_count']}<br>"
                )

                # Add Zotero metadata to tooltip if available
                if node_data.get('zotero_key'):
                    hover_text += f"<br><b>Zotero:</b><br>"
                    if node_data.get('zotero_collections'):
                        hover_text += f"Collections: {', '.join(node_data['zotero_collections'])}<br>"
                    if node_data.get('zotero_tags'):
                        hover_text += f"Tags: {', '.join(node_data['zotero_tags'][:5])}<br>"
                    hover_text += f'<a href="{node_data["zotero_url"]}" target="_blank">Open in Zotero</a><br>'

                hover_text += f"Node ID: {node} (Isolated)"
                isolated_hover.append(hover_text)
        
        # Create node traces
        node_traces = []
        
        # Connected papers trace
        if connected_x:
            connected_trace = go.Scatter(
                x=connected_x, y=connected_y,
                mode='markers+text',
                hoverinfo='text',
                text=connected_text,
                hovertext=connected_hover,
                textposition="middle center",
                name="Connected Papers",
                marker=dict(
                    showscale=True,
                    colorscale='Viridis',
                    reversescale=True,
                    color=connected_colors,
                    size=connected_sizes,
                    colorbar=dict(
                        thickness=15,
                        len=0.5,
                        x=1.02,
                        title="Publication Year",
                        titleside="right"
                    ),
                    line=dict(width=2, color='white'),
                    symbol='circle'
                )
            )
            node_traces.append(connected_trace)
        
        # Isolated papers trace (toggleable)
        if isolated_x:
            isolated_trace = go.Scatter(
                x=isolated_x, y=isolated_y,
                mode='markers+text',
                hoverinfo='text',
                text=isolated_text,
                hovertext=isolated_hover,
                textposition="middle center",
                name="Isolated Papers",
                visible=True,  # Initially visible
                marker=dict(
                    showscale=False,  # Don't duplicate the colorbar
                    colorscale='Viridis',
                    reversescale=True,
                    color=isolated_colors,
                    size=isolated_sizes,
                    line=dict(width=1, color='lightgray'),
                    symbol='circle',
                    opacity=0.5
                )
            )
            node_traces.append(isolated_trace)
        
        # Create the figure with all traces
        all_traces = edge_traces + node_traces
        
        fig = go.Figure(
            data=all_traces,
            layout=go.Layout(
                title=dict(
                    text="Citation Network Analysis<br><sub>Large nodes = citing papers, small nodes = cited references</sub>",
                    x=0.5,
                    font=dict(size=16)
                ),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=80),
                annotations=[dict(
                    text="🔵 Large nodes = citing papers (your PDFs) | Small nodes = cited references<br>"
                         "Edges show citation relationships | Node size indicates citation frequency",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=10)
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                height=700
            )
        )
        
        # Generate HTML file
        network_filename = output_path.stem + "_network.html"
        network_path = output_path.parent / network_filename
        
        # Create HTML with network
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Citation Network - {output_path.stem}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .network-container {{ width: 100%; height: 700px; }}
        .info {{ margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }}
        .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat {{ background: white; padding: 10px; border-radius: 3px; min-width: 120px; }}
        .controls {{ margin: 15px 0; padding: 10px; background-color: #e9ecef; border-radius: 5px; }}
        .toggle-btn {{ 
            background-color: #007bff; 
            color: white; 
            border: none; 
            padding: 8px 15px; 
            border-radius: 3px; 
            cursor: pointer; 
            margin-right: 10px; 
        }}
        .toggle-btn:hover {{ background-color: #0056b3; }}
        .toggle-btn.inactive {{ background-color: #6c757d; }}
        .toggle-btn.inactive:hover {{ background-color: #545b62; }}
    </style>
</head>
<body>
    <div class="info">
        <h2>Citation Network Analysis</h2>
        <div class="stats">
            <div class="stat"><strong>Connected Nodes:</strong> {len(connected_nodes)}</div>
            <div class="stat"><strong>Isolated Nodes:</strong> {len(isolated_nodes)}</div>
            <div class="stat"><strong>Citation Edges:</strong> {len(G.edges())}</div>
            <div class="stat"><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        <p><strong>Instructions:</strong> Hover over nodes for paper details. Drag to pan, scroll to zoom. 
        Node size indicates citation frequency, color indicates publication year.</p>
    </div>
    <div class="controls">
        <strong>Display Options:</strong>
        <button id="toggleIsolated" class="toggle-btn" onclick="toggleIsolatedReferences()">
            Hide Isolated References
        </button>
        <span id="isolatedCount">({len(isolated_nodes)} isolated nodes)</span>
    </div>
    <div id="network" class="network-container"></div>
    <script>
        var figure = {fig.to_json()};
        var showIsolated = true;
        
        Plotly.newPlot('network', figure.data, figure.layout, {{responsive: true}});
        
        function toggleIsolatedReferences() {{
            showIsolated = !showIsolated;
            var btn = document.getElementById('toggleIsolated');
            
            // Find the isolated references trace
            var traces = figure.data;
            var isolatedTraceIndex = -1;
            
            for (let i = traces.length - 1; i >= 0; i--) {{
                if (traces[i].name === 'Isolated References') {{
                    isolatedTraceIndex = i;
                    break;
                }}
            }}
            
            if (isolatedTraceIndex >= 0) {{
                var update = {{'visible': showIsolated}};
                Plotly.restyle('network', update, isolatedTraceIndex);
                
                if (showIsolated) {{
                    btn.textContent = 'Hide Isolated References';
                    btn.classList.remove('inactive');
                }} else {{
                    btn.textContent = 'Show Isolated References';
                    btn.classList.add('inactive');
                }}
            }}
        }}
    </script>
</body>
</html>"""
        
        # Write HTML file
        network_path.write_text(html_content, encoding='utf-8')
        
        logger.info(f"Interactive network visualization generated: {network_path}")
        return str(network_path)

    def _identify_top_cited_papers(self, all_references: Dict[str, Dict]) -> List[Dict[str, any]]:
        """
        Identify the top 5 papers that are most frequently cited across the collection.
        
        Args:
            all_references: Dictionary of all paper references and metadata
            
        Returns:
            List of top cited papers with citation counts
        """
        # Count how many times each paper in our collection is cited by other papers
        paper_citation_counts = {}
        
        for paper_key, paper_info in all_references.items():
            paper_citation_counts[paper_key] = {
                "paper_info": paper_info["paper_info"],
                "citation_count": 0,
                "cited_by": []
            }
        
        # Check cross-citations between papers in collection
        for citing_paper_key, citing_paper_info in all_references.items():
            for cited_paper_key, cited_paper_info in all_references.items():
                if citing_paper_key != cited_paper_key:
                    # Check if citing_paper cites cited_paper
                    if self._check_paper_citations(citing_paper_info, cited_paper_info["paper_info"]):
                        paper_citation_counts[cited_paper_key]["citation_count"] += 1
                        paper_citation_counts[cited_paper_key]["cited_by"].append(citing_paper_key)
        
        # Sort by citation count and return top 5
        top_papers = sorted(
            paper_citation_counts.values(),
            key=lambda x: x["citation_count"],
            reverse=True
        )
        
        # Only return papers that are actually cited (count > 0)
        result = []
        for paper in top_papers:
            if paper["citation_count"] > 0:
                result.append({
                    "title": paper["paper_info"].get("title", "Unknown Title"),
                    "authors": paper["paper_info"].get("authors", ["Unknown Author"]),
                    "year": paper["paper_info"].get("year", "Unknown Year"),
                    "citekey": paper["paper_info"].get("citekey", "unknown"),
                    "citation_count": paper["citation_count"],
                    "cited_by": paper["cited_by"]
                })
        
        return result
    def extract_zotero_relations(self, zotero_items: List[Dict]) -> List[Tuple[str, str, str]]:
        """
        Extract citation relationships from Zotero item relations
        
        Args:
            zotero_items: List of Zotero item dictionaries
            
        Returns:
            List of (source_key, target_key, relation_type) tuples
        """
        relations = []
        
        for item in zotero_items:
            source_key = item.get('key')
            item_relations = item.get('data', {}).get('relations', {})
            
            if not source_key or not item_relations:
                continue
            
            # Extract related items
            related = item_relations.get('dc:relation', [])
            if isinstance(related, str):
                related = [related]
            
            for relation_url in related:
                # Parse Zotero URL to get target key
                # Format: https://www.zotero.org/users/USERID/items/ITEMKEY
                match = re.search(r'/items/([A-Z0-9]{8})$', relation_url)
                if match:
                    target_key = match.group(1)
                    relations.append((source_key, target_key, 'cites'))
        
        return relations
    
    def build_zotero_citation_network(
        self,
        zotero_items: List[Dict],
        include_metadata: bool = True
    ) -> ReferenceNetwork:
        """
        Build citation network from Zotero items with relationships
        
        Args:
            zotero_items: List of Zotero item dictionaries
            include_metadata: Include full metadata in nodes
            
        Returns:
            ReferenceNetwork with nodes and edges
        """
        nodes = []
        edges = []
        
        # Create node for each item
        key_to_metadata = {}
        for item in zotero_items:
            key = item.get('key')
            data = item.get('data', {})
            
            if not key:
                continue
            
            # Extract basic metadata
            creators = data.get('creators', [])
            first_author = creators[0].get('lastName', 'Unknown') if creators else 'Unknown'
            year = data.get('date', '')[:4] if data.get('date') else 'Unknown'
            title = data.get('title', 'Untitled')
            
            node = {
                'id': key,
                'label': f"{first_author} ({year})",
                'title': title,
                'year': year,
                'first_author': first_author
            }
            
            if include_metadata:
                node['zotero_key'] = key
                node['zotero_url'] = f"zotero://select/library/items/{key}"
                node['item_type'] = data.get('itemType', 'unknown')
                node['tags'] = [tag['tag'] for tag in data.get('tags', [])]
                node['collections'] = data.get('collections', [])
            
            nodes.append(node)
            key_to_metadata[key] = node
        
        # Extract relationships
        relations = self.extract_zotero_relations(zotero_items)
        
        for source_key, target_key, relation_type in relations:
            if source_key in key_to_metadata and target_key in key_to_metadata:
                edges.append({
                    'source': source_key,
                    'target': target_key,
                    'relation': relation_type,
                    'source_label': key_to_metadata[source_key]['label'],
                    'target_label': key_to_metadata[target_key]['label']
                })
        
        return ReferenceNetwork(nodes=nodes, edges=edges)
    
    def enhance_network_with_zotero(
        self,
        existing_network: ReferenceNetwork,
        zotero_items: List[Dict]
    ) -> ReferenceNetwork:
        """
        Enhance existing citation network with Zotero relationship data
        
        Args:
            existing_network: Network built from PDF citation extraction
            zotero_items: Zotero items to add relationship data from
            
        Returns:
            Enhanced ReferenceNetwork combining both sources
        """
        # Build Zotero network
        zotero_network = self.build_zotero_citation_network(zotero_items)
        
        # Merge nodes (prefer Zotero metadata)
        merged_nodes = {node['id']: node for node in existing_network.nodes}
        for zotero_node in zotero_network.nodes:
            if zotero_node['id'] in merged_nodes:
                # Update existing node with Zotero metadata
                merged_nodes[zotero_node['id']].update(zotero_node)
            else:
                # Add new node from Zotero
                merged_nodes[zotero_node['id']] = zotero_node
        
        # Merge edges (combine both sources, deduplicate)
        edge_set = set()
        merged_edges = []
        
        for edge in existing_network.edges + zotero_network.edges:
            edge_tuple = (edge['source'], edge['target'], edge['relation'])
            if edge_tuple not in edge_set:
                edge_set.add(edge_tuple)
                merged_edges.append(edge)
        
        return ReferenceNetwork(
            nodes=list(merged_nodes.values()),
            edges=merged_edges
        )

    def _map_collections_to_colors(self, paper_data: Dict) -> Dict[str, int]:
        """
        Map Zotero collections to color indices for visualization.
        
        Args:
            paper_data: Dictionary of paper metadata
            
        Returns:
            Dictionary mapping node keys to collection color indices
        """
        # Extract all unique collections
        all_collections = set()
        for node_key, attrs in paper_data.items():
            if attrs.get('collection_primary'):
                all_collections.add(attrs['collection_primary'])
        
        # Create color mapping (collection name -> index)
        collection_to_index = {coll: idx for idx, coll in enumerate(sorted(all_collections))}
        
        # Map each node to its collection color index
        node_to_color = {}
        for node_key, attrs in paper_data.items():
            primary_coll = attrs.get('collection_primary')
            if primary_coll and primary_coll in collection_to_index:
                node_to_color[node_key] = collection_to_index[primary_coll]
            else:
                # Assign default color index for papers without collection
                node_to_color[node_key] = -1
        
        return node_to_color
