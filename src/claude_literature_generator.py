"""
Literature Guidance MCP Tool - Simplified
Provides ONLY guidance and structure - Claude does all PDF reading and analysis
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class LiteratureGuidanceTool:
    """
    Simplified MCP tool that provides guidance for literature note generation
    
    Core principle: This tool does NOT read, process, or analyze PDFs
    It only provides structural guidance and naming conventions
    Claude handles all intelligent PDF reading and analysis
    """
    
    def __init__(self):
        self.structure_templates = {
            'empirical': [
                '---',
                'title: "{title}"',
                'authors: "{authors}"',
                'year: {year}',
                'journal: "{journal}"',
                'doi: "{doi}"',
                'citekey: "{citekey}"',
                'focus: "{focus}"',
                'depth: "{depth}"',
                'paper_type: "empirical"',
                'tags: ["{domain}", "{method}", "empirical", "literature-note"]',
                'generated: "{timestamp}"',
                '---',
                '',
                '# Literature Note: {title}',
                '',
                '## Citation Information',
                '**Authors:** {authors}',
                '**Year:** {year}',
                '**Journal:** {journal}',
                '**DOI:** {doi}',
                '**Citekey:** `{citekey}`',
                '',
                '## Executive Summary',
                '[Claude: Read the PDF and provide 2-3 sentence summary of key findings]',
                '',
                '## Research Question and Hypotheses',
                '[Claude: Extract the main research questions and hypotheses from PDF]',
                '',
                '## Methodology',
                '### Study Design',
                '[Claude: Describe the experimental/study design from PDF]',
                '',
                '### Data Collection',
                '[Claude: Explain data collection methods from PDF]',
                '',
                '### Analysis Methods',
                '[Claude: Detail analytical approaches from PDF]',
                '',
                '## Key Findings',
                '[Claude: Summarize main results with quantitative details from PDF]',
                '',
                '## Statistical Results',
                '[Claude: Extract key statistical findings, effect sizes, p-values from PDF]',
                '',
                '## Discussion and Interpretation',
                '[Claude: Analyze authors\' interpretation from PDF]',
                '',
                '## Limitations',
                '[Claude: Identify study limitations mentioned in PDF]',
                '',
                '## Implications',
                '### Theoretical Implications',
                '[Claude: Extract theoretical implications from PDF]',
                '',
                '### Practical Applications',
                '[Claude: Extract practical applications from PDF]',
                '',
                '## Personal Notes and Insights',
                '[Your analysis after Claude completes the above]',
                '',
                '## Tags and Keywords',
                '`empirical` `{domain}` `{method}` `literature-note`',
                '',
                '---',
                '**Note Generated:** {timestamp}',
                '**Analysis Method:** Claude direct PDF analysis',
                '**Structure:** Empirical research template'
            ],
            
            'theoretical': [
                '---',
                'title: "{title}"',
                'authors: "{authors}"',
                'year: {year}',
                'journal: "{journal}"',
                'doi: "{doi}"',
                'citekey: "{citekey}"',
                'focus: "{focus}"',
                'depth: "{depth}"',
                'paper_type: "theoretical"',
                'tags: ["{domain}", "{theory_type}", "theoretical", "literature-note"]',
                'generated: "{timestamp}"',
                '---',
                '',
                '# Literature Note: {title}',
                '',
                '## Citation Information',
                '**Authors:** {authors}',
                '**Year:** {year}',
                '**Journal:** {journal}',
                '**DOI:** {doi}',
                '**Citekey:** `{citekey}`',
                '',
                '## Executive Summary',
                '[Claude: Read PDF and summarize theoretical contribution]',
                '',
                '## Theoretical Framework',
                '[Claude: Describe main theoretical framework from PDF]',
                '',
                '## Key Concepts and Definitions',
                '[Claude: Extract and define key concepts from PDF]',
                '',
                '## Mathematical Formulation',
                '[Claude: Include key equations/models from PDF]',
                '',
                '## Model Assumptions',
                '[Claude: List assumptions from PDF]',
                '',
                '## Theoretical Contributions',
                '[Claude: Extract new theoretical insights from PDF]',
                '',
                '## Validation and Testing',
                '[Claude: How theory is validated in PDF]',
                '',
                '## Applications and Examples',
                '[Claude: Extract applications from PDF]',
                '',
                '## Personal Notes and Insights',
                '[Your theoretical analysis after Claude completes above]',
                '',
                '## Tags and Keywords',
                '`theoretical` `{domain}` `{theory_type}` `literature-note`',
                '',
                '---',
                '**Note Generated:** {timestamp}',
                '**Analysis Method:** Claude direct PDF analysis',
                '**Structure:** Theoretical paper template'
            ],
            
            'review': [
                '---',
                'title: "{title}"',
                'authors: "{authors}"',
                'year: {year}',
                'journal: "{journal}"',
                'doi: "{doi}"',
                'citekey: "{citekey}"',
                'focus: "{focus}"',
                'depth: "{depth}"',
                'paper_type: "review"',
                'tags: ["{domain}", "review", "synthesis", "literature-note"]',
                'generated: "{timestamp}"',
                '---',
                '',
                '# Literature Note: {title}',
                '',
                '## Citation Information',
                '**Authors:** {authors}',
                '**Year:** {year}',
                '**Journal:** {journal}',
                '**DOI:** {doi}',
                '**Citekey:** `{citekey}`',
                '',
                '## Executive Summary',
                '[Claude: Read PDF and summarize scope and conclusions]',
                '',
                '## Scope and Coverage',
                '[Claude: Extract scope and criteria from PDF]',
                '',
                '## Key Topics Reviewed',
                '[Claude: Extract main themes from PDF]',
                '',
                '## Major Findings Synthesis',
                '[Claude: Extract synthesized findings from PDF]',
                '',
                '## Gaps Identified',
                '[Claude: Extract identified gaps from PDF]',
                '',
                '## Future Directions',
                '[Claude: Extract recommended directions from PDF]',
                '',
                '## Critical Assessment',
                '[Claude: Extract authors\' evaluation from PDF]',
                '',
                '## Personal Notes and Insights',
                '[Your synthesis after Claude completes above]',
                '',
                '## Tags and Keywords',
                '`review` `{domain}` `synthesis` `literature-note`',
                '',
                '---',
                '**Note Generated:** {timestamp}',
                '**Analysis Method:** Claude direct PDF analysis',
                '**Structure:** Review paper template'
            ],
            
            'method': [
                '---',
                'title: "{title}"',
                'authors: "{authors}"',
                'year: {year}',
                'journal: "{journal}"',
                'doi: "{doi}"',
                'citekey: "{citekey}"',
                'focus: "{focus}"',
                'depth: "{depth}"',
                'paper_type: "method"',
                'tags: ["{domain}", "{technique}", "method", "literature-note"]',
                'generated: "{timestamp}"',
                '---',
                '',
                '# Literature Note: {title}',
                '',
                '## Citation Information',
                '**Authors:** {authors}',
                '**Year:** {year}',
                '**Journal:** {journal}',
                '**DOI:** {doi}',
                '**Citekey:** `{citekey}`',
                '',
                '## Executive Summary',
                '[Claude: Read PDF and summarize methodological contribution]',
                '',
                '## Method Overview',
                '[Claude: Describe the main method/technique from PDF]',
                '',
                '## Technical Specifications',
                '[Claude: Extract technical details and parameters from PDF]',
                '',
                '## Implementation Details',
                '[Claude: Extract implementation specifics from PDF]',
                '',
                '## Validation and Testing',
                '[Claude: Extract validation methods and results from PDF]',
                '',
                '## Performance Evaluation',
                '[Claude: Extract performance metrics and comparisons from PDF]',
                '',
                '## Advantages and Limitations',
                '[Claude: Extract method strengths and limitations from PDF]',
                '',
                '## Applications and Use Cases',
                '[Claude: Extract practical applications from PDF]',
                '',
                '## Personal Notes and Insights',
                '[Your methodological analysis after Claude completes above]',
                '',
                '## Tags and Keywords',
                '`method` `{domain}` `{technique}` `literature-note`',
                '',
                '---',
                '**Note Generated:** {timestamp}',
                '**Analysis Method:** Claude direct PDF analysis',
                '**Structure:** Methodological paper template'
            ]
        }

    def get_filename_guidance(self, title: str, first_author: str, year: int) -> Dict[str, str]:
        """
        Get filename guidance using author+year+firstword format
        NO PDF processing - just naming guidance
        """
        # Clean author name (last name only)
        author_clean = self._extract_last_name(first_author)
        
        # Extract first meaningful word from title
        first_word = self._extract_first_word(title)
        
        # Generate the yang2024multi format
        filename = f"{author_clean.lower()}{year}{first_word.lower()}"
        
        return {
            'suggested_filename': f"{filename}.md",
            'format': f"{author_clean}+{year}+{first_word}",
            'example': "yang2024multi.md for 'Multi-domain Protein...' by Yang et al (2024)"
        }

    def get_structure_guidance(self, paper_type: str = 'empirical') -> Dict[str, Any]:
        """
        Get structure template based on paper type
        NO content analysis - just structure guidance
        """
        template = self.structure_templates.get(paper_type, self.structure_templates['empirical'])
        
        return {
            'paper_type': paper_type,
            'template_lines': template,
            'claude_workflow': [
                "1. Read the PDF directly using your multimodal capabilities",
                "2. Use this template structure as your outline",
                "3. Fill in all [Claude: ...] sections with your PDF analysis", 
                "4. Replace {placeholders} with extracted information",
                "5. Save with the suggested filename"
            ],
            'no_preprocessing': "This tool provides structure only - Claude reads PDF directly"
        }

    def get_batch_guidance(self, theme: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get guidance for multi-paper batch analysis
        NO processing - just coordination guidance
        """
        # Generate individual file guidance
        individual_notes = []
        for paper in papers:
            filename_guidance = self.get_filename_guidance(
                paper.get('title', 'Unknown'),
                paper.get('first_author', 'Unknown'),
                paper.get('year', 2024)
            )
            individual_notes.append({
                'title': paper.get('title', 'Unknown'),
                'filename': filename_guidance['suggested_filename'],
                'pdf_path': paper.get('pdf_path', '')
            })
        
        # Calculate year range
        years = [p.get('year', 2024) for p in papers]
        year_range = f"{min(years)}-{max(years)}" if len(set(years)) > 1 else str(years[0])
        
        batch_template = [
            '---',
            f'title: "Batch Literature Analysis: {theme}"',
            f'theme: "{theme}"',
            f'paper_count: {len(papers)}',
            f'year_range: "{year_range}"',
            'analysis_type: "batch"',
            'tags: ["batch-analysis", "multi-paper", "literature-review"]',
            f'generated: "{datetime.now().isoformat()}"',
            '---',
            '',
            f'# Batch Literature Analysis: {theme}',
            '',
            '## Analysis Overview',
            f'**Theme:** {theme}',
            f'**Papers Analyzed:** {len(papers)}',
            f'**Year Range:** {year_range}',
            f'**Analysis Date:** {datetime.now().strftime("%Y-%m-%d")}',
            '',
            '## Individual Paper Notes',
            '[Claude: Create individual notes for each paper using structure guidance]'
        ]
        
        # Add links to individual notes
        for i, note in enumerate(individual_notes, 1):
            batch_template.extend([
                f'### Paper {i}: {note["filename"]}',
                f'[Link to: {note["filename"]}]',
                ''
            ])
        
        batch_template.extend([
            '## Cross-Paper Analysis',
            '',
            '### Historical Evolution',
            '[Claude: How has this field evolved chronologically across these papers?]',
            '',
            '### Methodological Progression', 
            '[Claude: How have methods evolved across papers?]',
            '',
            '### Key Findings Synthesis',
            '[Claude: What are combined insights across papers?]',
            '',
            '### Current State and Gaps',
            '[Claude: Current state and remaining gaps?]',
            '',
            '### Future Trajectory',
            '[Claude: Future direction based on these papers?]',
            '',
            '## Personal Synthesis',
            '[Your cross-paper insights after Claude completes analyses]',
            '',
            '## Tags and Keywords',
            f'`batch-analysis` `{theme.replace(" ", "-")}` `multi-paper` `literature-review`',
            '',
            '---',
            f'**Batch Analysis Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'**Individual Notes:** {len(papers)}',
            '**Analysis Method:** Claude direct PDF analysis + Guidance structure'
        ])
        
        return {
            'theme': theme,
            'paper_count': len(papers),
            'year_range': year_range,
            'individual_notes': individual_notes,
            'batch_template': batch_template,
            'claude_workflow': [
                "1. For each paper: read PDF directly and create individual note",
                "2. Use structure guidance for consistent format",
                "3. Save individual notes with suggested filenames",
                "4. Create batch synthesis note using batch template",
                "5. Link all individual notes in batch synthesis"
            ]
        }

    def _extract_last_name(self, author: str) -> str:
        """Extract last name from author string"""
        author = re.sub(r'\b(Dr|Prof|Mr|Ms|Mrs)\.?\s*', '', author, flags=re.IGNORECASE)
        
        if ',' in author:
            last_name = author.split(',')[0].strip()
        else:
            parts = author.strip().split()
            last_name = parts[-1] if parts else 'unknown'
        
        clean_name = re.sub(r'[^a-zA-Z]', '', last_name)
        return clean_name[:15]

    def _extract_first_word(self, title: str) -> str:
        """Extract first meaningful word from title"""
        skip_words = {'a', 'an', 'the', 'on', 'in', 'at', 'to', 'for', 'of', 'with', 'by', 'and', 'or'}
        
        words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
        
        for word in words:
            if word not in skip_words and len(word) > 2:
                return word[:10]
        
        return words[0][:10] if words else 'paper'


# Main MCP Functions (what gets called by external tools)
def get_literature_note_guidance(title: str, first_author: str, year: int, 
                               paper_type: str = 'empirical') -> Dict[str, Any]:
    """
    MCP Function: Get complete guidance for creating a literature note
    
    Returns guidance only - Claude does all PDF reading and analysis
    """
    tool = LiteratureGuidanceTool()
    
    filename_guidance = tool.get_filename_guidance(title, first_author, year)
    structure_guidance = tool.get_structure_guidance(paper_type)
    
    return {
        'filename': filename_guidance,
        'structure': structure_guidance,
        'mcp_role': 'Provides guidance only - no PDF processing',
        'claude_role': 'Reads PDF directly and does all intelligent analysis'
    }


def get_batch_analysis_guidance(theme: str, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    MCP Function: Get guidance for batch analysis of multiple papers
    
    Args:
        theme: Analysis theme (e.g., "evolution of CRISPR techniques")
        papers: [{'title': str, 'first_author': str, 'year': int, 'pdf_path': str}, ...]
    
    Returns guidance only - Claude does all PDF reading and analysis
    """
    tool = LiteratureGuidanceTool()
    
    return tool.get_batch_guidance(theme, papers)


def generate_literature_note(pdf_path: str, focus: str = "balanced", depth: str = "standard") -> Dict[str, Any]:
    """
    TRANSFORMED FUNCTION: Returns guidance + actual PDF metadata when possible
    
    This function provides guidance and tries to extract real metadata from PDF
    to improve filename suggestions and paper type detection.
    
    Args:
        pdf_path: Path to PDF file
        focus: Analysis focus (empirical, theoretical, review, method, balanced)
        depth: Analysis depth (quick, standard, deep)
        
    Returns:
        Guidance for Claude to generate literature note + real metadata
    """
    try:
        # Try to extract real metadata using PDF processor
        from pdf_processor import PDFProcessor
        pdf_processor = PDFProcessor()
        
        if pdf_processor.validate_pdf(pdf_path):
            metadata = pdf_processor.extract_metadata(pdf_path)
            title = metadata.title
            first_author = metadata.first_author
            year = metadata.year or 2024
            
            print(f"✅ Successfully extracted metadata from PDF:")
            print(f"   Title: {title}")
            print(f"   Author: {first_author}")
            print(f"   Year: {year}")
        else:
            raise Exception("PDF validation failed")
            
    except Exception as e:
        print(f"⚠️  Could not extract PDF metadata ({e}), using filename parsing...")
        # Fallback to filename parsing
        pdf_file = Path(pdf_path)
        filename = pdf_file.stem
        title, first_author, year = _parse_filename_for_guidance(filename)
    
    # Determine paper type from focus or title
    if focus in ['empirical', 'theoretical', 'review', 'method']:
        paper_type = focus
    else:
        paper_type = _infer_paper_type_from_title(title)
    
    # Get guidance with real metadata
    guidance = get_literature_note_guidance(title, first_author, year, paper_type)
    
    # Create proper template with real values filled in
    template_filled = []
    for line in guidance['structure']['template_lines']:
        # Replace placeholders with real values
        line_filled = line.format(
            title=title,
            authors=first_author,
            year=year,
            journal="[Extract from PDF]",
            doi="[Extract from PDF]", 
            citekey=_generate_citekey_for_guidance(first_author, year, title),
            focus=focus,
            depth=depth,
            domain=_infer_domain_from_title(title),
            method=_infer_method_from_title(title),
            theory_type=_infer_theory_type_from_title(title),
            technique=_infer_technique_from_title(title),
            timestamp=datetime.now().isoformat()
        )
        template_filled.append(line_filled)
    
    return {
        'success': True,
        'guidance_mode': True,
        'pdf_path': pdf_path,
        'suggested_filename': guidance['filename']['suggested_filename'],
        'structure_template': template_filled,
        'claude_instructions': [
            f"1. Read this PDF directly using Claude Code's capabilities: {pdf_path}",
            f"2. The PDF file exists and contains: {title} by {first_author} ({year})",
            f"3. Use the provided structure template as your outline",
            f"4. Fill in all [Claude: ...] sections by reading and analyzing the PDF content",
            f"5. Replace [Extract from PDF] placeholders with actual information from the PDF",
            f"6. Save the completed note as: {guidance['filename']['suggested_filename']}",
            f"7. Analysis Parameters: Focus={focus}, Depth={depth}, Type={paper_type}",
            *_get_depth_instructions(depth, focus)
        ],
        'pdf_reading_instructions': [
            "IMPORTANT: Use Claude Code's Task tool to read the PDF if the Read tool fails",
            "The Task tool can handle PDF files that the Read tool cannot process",
            "Example: Use Task tool with description 'Read and analyze PDF content for literature note'"
        ],
        'mcp_benefits': 'Provides structure + real metadata extraction when possible',
        'metadata_extracted': {
            'title': title,
            'first_author': first_author, 
            'year': year,
            'paper_type': paper_type
        }
    }


def _parse_filename_for_guidance(filename: str) -> tuple:
    """Parse filename for basic guidance (not content analysis)"""
    # Common patterns: "Author et al. - YEAR - Title.pdf"
    patterns = [
        r'([^-]+)\s*-\s*(\d{4})\s*-\s*(.+)',
        r'([^(]+)\((\d{4})\)\s*(.+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            if len(match.groups()) == 3:
                author_part, year_str, title_part = match.groups()
                return title_part.strip(), author_part.strip(), int(year_str)
    
    # Fallback
    year_match = re.search(r'(\d{4})', filename)
    year = int(year_match.group(1)) if year_match else 2024
    
    return filename, filename.split()[0] if filename.split() else 'Unknown', year


def _infer_paper_type_from_title(title: str) -> str:
    """Infer paper type from title for structure guidance"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['review', 'survey', 'overview']):
        return 'review'
    elif any(word in title_lower for word in ['theory', 'model', 'framework']):
        return 'theoretical'
    elif any(word in title_lower for word in ['method', 'technique', 'algorithm', 'protocol']):
        return 'method'
    else:
        return 'empirical'


def _generate_citekey_for_guidance(first_author: str, year: int, title: str) -> str:
    """Generate citekey for guidance using author+year+firstword format"""
    # Clean author name (last name only)
    if ',' in first_author:
        author_clean = first_author.split(',')[0].strip()
    else:
        parts = first_author.strip().split()
        author_clean = parts[-1] if parts else 'unknown'
    
    # Clean non-alphabetic characters
    author_clean = re.sub(r'[^a-zA-Z]', '', author_clean).lower()[:10]
    
    # Extract first meaningful word from title
    skip_words = {'a', 'an', 'the', 'on', 'in', 'at', 'to', 'for', 'of', 'with', 'by', 'and', 'or'}
    words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
    
    first_word = 'paper'
    for word in words:
        if word not in skip_words and len(word) > 2:
            first_word = word[:8]
            break
    
    return f"{author_clean}{year}{first_word}"


def _infer_domain_from_title(title: str) -> str:
    """Infer research domain from title"""
    title_lower = title.lower()
    
    domain_keywords = {
        'protein': 'protein-science',
        'molecular': 'molecular-biology', 
        'coarse': 'computational-modeling',
        'viscosity': 'rheology',
        'simulation': 'computational-chemistry',
        'force': 'molecular-dynamics',
        'quantum': 'quantum-chemistry',
        'machine': 'machine-learning',
        'ai': 'artificial-intelligence',
        'neural': 'neural-networks',
        'ftir': 'spectroscopy',
        'histology': 'medical-imaging',
        'deep': 'deep-learning'
    }
    
    for keyword, domain in domain_keywords.items():
        if keyword in title_lower:
            return domain
    
    return 'scientific-research'


def _infer_method_from_title(title: str) -> str:
    """Infer methodology from title"""
    title_lower = title.lower()
    
    if 'simulation' in title_lower or 'dynamics' in title_lower:
        return 'computational'
    elif 'experimental' in title_lower or 'measurement' in title_lower:
        return 'experimental'
    elif 'theoretical' in title_lower or 'model' in title_lower:
        return 'theoretical'
    elif 'deep' in title_lower or 'neural' in title_lower:
        return 'machine-learning'
    else:
        return 'analytical'


def _infer_theory_type_from_title(title: str) -> str:
    """Infer theory type from title"""
    title_lower = title.lower()
    
    if 'quantum' in title_lower:
        return 'quantum-theory'
    elif 'statistical' in title_lower:
        return 'statistical-theory'
    elif 'thermodynamic' in title_lower:
        return 'thermodynamic-theory'
    elif 'kirkwood' in title_lower:
        return 'solution-theory'
    else:
        return 'mathematical-theory'


def _infer_technique_from_title(title: str) -> str:
    """Infer technique from title"""
    title_lower = title.lower()
    
    if 'ftir' in title_lower:
        return 'spectroscopy'
    elif 'neural' in title_lower or 'cnn' in title_lower:
        return 'deep-learning'
    elif 'simulation' in title_lower:
        return 'molecular-simulation'
    elif 'scattering' in title_lower:
        return 'scattering-methods'
    else:
        return 'computational-method'


def _get_depth_instructions(depth: str, focus: str) -> list:
    """Get depth-specific instructions for literature note generation"""
    base_instructions = {
        'quick': [
            "8. DEPTH=QUICK: Target 400-600 words total",
            "   - Focus on essential points only",
            "   - 2-3 sentences per major section",
            "   - Emphasize key findings and main conclusion",
            "   - Skip detailed methodology unless critical"
        ],
        'standard': [
            "8. DEPTH=STANDARD: Target 1000-1800 words total",
            "   - Comprehensive coverage of all major aspects",
            "   - 4-6 sentences per section with supporting details",
            "   - Include methodology, results, and implications",
            "   - Balance breadth with sufficient detail for understanding"
        ],
        'deep': [
            "8. DEPTH=DEEP: Target 1800-3000 words total",
            "   - Extensive analysis with critical evaluation",
            "   - 6+ sentences per section with comprehensive detail",
            "   - Include mathematical formulations, detailed methods",
            "   - Add critical assessment and broader implications",
            "   - Consider limitations and future directions thoroughly"
        ]
    }
    
    length_guidance = {
        'empirical': " - Scale length based on experimental complexity",
        'theoretical': " - Include mathematical details proportional to paper length", 
        'review': " - Synthesis depth should match scope of review",
        'method': " - Technical detail should match method complexity"
    }
    
    instructions = base_instructions.get(depth, base_instructions['standard']).copy()
    if focus in length_guidance:
        instructions.append(f"9. FOCUS={focus.upper()}:{length_guidance[focus]}")
    
    return instructions


if __name__ == "__main__":
    # Example usage
    print("=== Literature Guidance MCP Tool ===")
    print("Provides guidance only - Claude does all PDF reading and analysis")
    print()
    
    # Test guidance generation
    guidance = generate_literature_note(
        "tests/examples/papers/Yang et al. - 2024 - Multi-domain Protein Design.pdf",
        focus="balanced",
        depth="standard"
    )
    
    print("GUIDANCE OUTPUT:")
    print(f"Suggested filename: {guidance['suggested_filename']}")
    print(f"Claude instructions: {guidance['claude_instructions'][0]}")
    print()
    print("KEY TRANSFORMATION:")
    print("- No PDF text extraction")
    print("- No content processing") 
    print("- No Claude API calls")
    print("- Only provides structure and naming guidance")
    print("- Claude reads PDF directly and does intelligent analysis")