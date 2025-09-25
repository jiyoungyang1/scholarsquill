#!/usr/bin/env python3
"""
Test script for citekey generation and filename creation
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent / "src")
sys.path.insert(0, src_path)

# Change to src directory to handle relative imports
os.chdir(src_path)

try:
    from models import PaperMetadata
    from file_writer import FileWriter
    from utils import generate_citekey
except ImportError as e:
    print(f"Import error: {e}")
    print("Testing citekey generation directly...")
    
    import re
    
    def generate_citekey(first_author: str, year, title: str) -> str:
        """Generate citation key in format: authorYEARkeyword"""
        # Extract last name from first author
        # Handle "LastName, FirstName" format
        if ',' in first_author:
            last_name = first_author.split(',')[0].strip()
        else:
            # Handle "FirstName LastName" format
            author_parts = first_author.split()
            last_name = author_parts[-1] if author_parts else "unknown"
        
        # Clean author name
        author_clean = re.sub(r'[^a-zA-Z]', '', last_name).lower()
        
        # Get year string
        year_str = str(year) if year else "unknown"
        
        # Extract first meaningful word from title
        title_words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
        keyword = title_words[0] if title_words else "paper"
        
        return f"{author_clean}{year_str}{keyword}"


def test_citekey_generation():
    """Test citekey generation with sample metadata"""
    
    # Test cases based on the sample PDFs
    test_cases = [
        {
            "authors": ["Bonollo, M.", "Smith, J.", "Doe, A."],
            "year": 2025,
            "title": "Advancing Molecular Simulations Merging Physical Models, Experiments, and AI to Tackle Multiscale Challenges",
            "expected_citekey": "bonollo2025advancing"
        },
        {
            "authors": ["Cloutier, T.", "Sudrik, C.", "Mody, N."],
            "year": 2020,
            "title": "Molecular computations of preferential interactions of proline, arginine.HCl, and NaCl with IgG1 antibodies",
            "expected_citekey": "cloutier2020molecular"
        },
        {
            "authors": ["Ganguly, P.", "Mukherji, D.", "Junghans, C.", "van der Vegt, N.F.A."],
            "year": 2012,
            "title": "Kirkwood–Buff Coarse-Grained Force Fields for Aqueous Solutions",
            "expected_citekey": "ganguly2012kirkwood"
        },
        {
            "authors": ["Kmiecik, S.", "Gront, D.", "Kolinski, M."],
            "year": 2016,
            "title": "Coarse-Grained Protein Models and Their Applications",
            "expected_citekey": "kmiecik2016coarse"
        },
        {
            "authors": ["Zidar, M.", "Kuzman, D.", "Ravnik, M."],
            "year": 2020,
            "title": "Control of viscosity in biopharmaceutical protein formulations",
            "expected_citekey": "zidar2020control"
        }
    ]
    
    print("Testing citekey generation:")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        # Test direct citekey generation
        first_author = case["authors"][0]
        generated_citekey = generate_citekey(first_author, case["year"], case["title"])
        
        print(f"\nTest Case {i}:")
        print(f"  Authors: {case['authors']}")
        print(f"  Year: {case['year']}")
        print(f"  Title: {case['title'][:60]}...")
        print(f"  Expected: {case['expected_citekey']}")
        print(f"  Generated: {generated_citekey}")
        print(f"  Match: {'✓' if generated_citekey == case['expected_citekey'] else '✗'}")
        
        # Test filename generation
        expected_filename = f"{case['expected_citekey']}.md"
        generated_filename = f"{generated_citekey}.md"
        
        print(f"  Filename: {generated_filename}")
        print(f"  Expected filename: {expected_filename}")
        print(f"  Filename match: {'✓' if generated_filename == expected_filename else '✗'}")


def test_edge_cases():
    """Test edge cases for citekey generation"""
    
    print("\n\nTesting edge cases:")
    print("=" * 50)
    
    edge_cases = [
        {
            "name": "No year",
            "authors": ["Smith, J."],
            "year": None,
            "title": "Test Paper Title"
        },
        {
            "name": "No authors",
            "authors": [],
            "year": 2023,
            "title": "Anonymous Paper"
        },
        {
            "name": "Short title words",
            "authors": ["Doe, A."],
            "year": 2023,
            "title": "A New AI ML Approach"
        },
        {
            "name": "Special characters in author",
            "authors": ["O'Connor, P.", "van der Berg, M."],
            "year": 2023,
            "title": "Complex Author Names"
        }
    ]
    
    for case in edge_cases:
        print(f"\n{case['name']}:")
        
        if case["authors"]:
            first_author = case["authors"][0]
            citekey = generate_citekey(first_author, case["year"], case["title"])
            print(f"  Generated citekey: {citekey}")
        else:
            print("  No authors - would use fallback")
        
        # Test filename generation for edge cases
        if case["authors"]:
            first_author = case["authors"][0]
            citekey = generate_citekey(first_author, case["year"], case["title"])
            filename = f"{citekey}.md"
            print(f"  Generated filename: {filename}")
        else:
            print("  Would use fallback filename generation")


if __name__ == "__main__":
    test_citekey_generation()
    test_edge_cases()