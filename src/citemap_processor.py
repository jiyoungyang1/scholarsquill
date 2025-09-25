"""
Citation Context Mapping Processor for ScholarSquill Kiro

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
            output_filename = f"Citemap_{safe_citekey}.md"
            output_path = Path(options.output_dir) / output_filename
            
            # Write output file
            output_path.write_text(rendered_content, encoding="utf-8")
            
            logger.info(f"Citemap analysis completed: {output_path}")
            
            return {
                "success": True,
                "output_path": str(output_path),
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
                        references.append({
                            "number": str(ref_number),
                            "text": current_ref.strip(),
                            "parsed_authors": self._parse_authors_from_reference(current_ref),
                            "parsed_year": self._parse_year_from_reference(current_ref),
                            "parsed_title": self._parse_title_from_reference(current_ref)
                        })
                        current_ref = ""
                        ref_number += 1
                    continue
                
                # Check if this line starts a new reference
                if re.match(r'^\[?\d+\]?\.?\s+', line) or re.match(r'^[A-Za-z]', line):
                    if current_ref:
                        references.append({
                            "number": str(ref_number),
                            "text": current_ref.strip(),
                            "parsed_authors": self._parse_authors_from_reference(current_ref),
                            "parsed_year": self._parse_year_from_reference(current_ref),
                            "parsed_title": self._parse_title_from_reference(current_ref)
                        })
                        ref_number += 1
                    current_ref = line
                else:
                    # Continuation of current reference
                    current_ref += " " + line
            
            # Don't forget the last reference
            if current_ref:
                references.append({
                    "number": str(ref_number),
                    "text": current_ref.strip(),
                    "parsed_authors": self._parse_authors_from_reference(current_ref),
                    "parsed_year": self._parse_year_from_reference(current_ref),
                    "parsed_title": self._parse_title_from_reference(current_ref)
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
            List of reference dictionaries
        """
        references = []
        
        # Find references section with simple pattern
        ref_match = re.search(r'(?i)references?\s*\n(.*?)(?:\n\n|\Z)', content, re.DOTALL)
        if not ref_match:
            return references
        
        ref_text = ref_match.group(1)
        
        # Simple reference splitting by line
        ref_lines = [line.strip() for line in ref_text.split('\n') if line.strip()]
        
        ref_number = 1
        for line in ref_lines[:30]:  # Process first 30 references only
            if re.match(r'^\[?\d+\]?\.?\s+', line) or len(line) > 50:  # Simple heuristic
                references.append({
                    "number": str(ref_number),
                    "text": line,
                    "parsed_authors": self._parse_authors_from_reference(line),
                    "parsed_year": self._parse_year_from_reference(line),
                    "parsed_title": self._parse_title_from_reference(line)
                })
                ref_number += 1
        
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
        Match a citation string to reference numbers.
        
        Args:
            citation: Citation text (e.g., "Smith 2020", "[1,2]")
            references: List of reference dictionaries
            
        Returns:
            List of matching reference numbers
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
        
        # Handle author-year citations
        else:
            # Try to match author names and years
            for ref in references:
                ref_authors = ref.get("parsed_authors", "").lower()
                ref_year = ref.get("parsed_year", "")
                citation_lower = citation.lower()
                
                # Simple matching - can be improved
                if ref_authors and ref_year:
                    author_parts = ref_authors.split()
                    if author_parts and author_parts[0] in citation_lower and ref_year in citation:
                        matched_refs.append(ref["number"])
        
        return matched_refs
    
    def _parse_authors_from_reference(self, ref_text: str) -> str:
        """Extract author names from reference text."""
        # Simple author extraction - first part before year or journal
        parts = ref_text.split('.')
        if parts:
            first_part = parts[0].strip()
            # Remove reference number if present
            first_part = re.sub(r'^\[?\d+\]?\.?\s*', '', first_part)
            return first_part
        return ""
    
    def _parse_year_from_reference(self, ref_text: str) -> str:
        """Extract publication year from reference text."""
        year_match = re.search(r'\b(19|20)\d{2}\b', ref_text)
        return year_match.group(0) if year_match else ""
    
    def _parse_title_from_reference(self, ref_text: str) -> str:
        """Extract title from reference text."""
        # This is a simple extraction - can be improved
        # Usually title is between author/year and journal
        parts = ref_text.split('.')
        if len(parts) > 2:
            return parts[1].strip()
        return ""
    
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
                output_filename = f"Citemap_{safe_keyword}_{processed_count}.md"
            else:
                folder_name = input_path.name if hasattr(input_path, 'name') else str(input_path).split('/')[-1]
                safe_folder_name = "".join(c for c in folder_name if c.isalnum() or c in ('_', '-'))
                output_filename = f"Citemap_{safe_folder_name}_{processed_count}.md"
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
                
            # Node attributes for papers
            node_attrs = {
                'title': metadata.get("title", "Unknown Title"),
                'authors': authors,
                'authors_str': ", ".join(authors),
                'year': year_int,
                'citation_count': len(paper_info.get("citation_contexts", [])),
                'reference_count': len(paper_info.get("references", [])),
                'size': min(max(len(paper_info.get("citation_contexts", [])), 8), 30),
                'color_year': year_int
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
            connected_hover.append(
                f"<b>{node_data['title']}</b><br>"
                f"Authors: {node_data['authors_str']}<br>"
                f"Year: {node_data['year']}<br>"
                f"Citations in text: {node_data['citation_count']}<br>"
                f"References: {node_data['reference_count']}<br>"
                f"Node ID: {node}"
            )
        
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
                isolated_hover.append(
                    f"<b>{node_data['title']}</b><br>"
                    f"Authors: {node_data['authors_str']}<br>"
                    f"Year: {node_data['year']}<br>"
                    f"Citations in text: {node_data['citation_count']}<br>"
                    f"References: {node_data['reference_count']}<br>"
                    f"Node ID: {node} (Isolated)"
                )
        
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
                    color=isolated_ref_colors,
                    size=isolated_ref_sizes,
                    line=dict(width=1, color='lightgray'),
                    symbol='circle',
                    opacity=0.5
                )
            )
            node_traces.append(isolated_ref_trace)
        
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
            <div class="stat"><strong>Citing Papers:</strong> {len(citing_papers)}</div>
            <div class="stat"><strong>Cited References:</strong> {len(cited_references)}</div>
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
        <span id="isolatedCount">({len(isolated_references)} isolated references)</span>
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