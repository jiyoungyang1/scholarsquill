"""
Test cases for citekey generation and filename creation
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import PaperMetadata
from utils import generate_citekey, extract_first_author_lastname
from file_writer import FileWriter


class TestCitekeyGeneration:
    """Test citekey generation functionality"""
    
    def test_generate_citekey_standard_format(self):
        """Test citekey generation with standard author format"""
        # Test case: "LastName, FirstName" format
        citekey = generate_citekey("Bonollo, M.", 2025, "Advancing Molecular Simulations")
        assert citekey == "bonollo2025advancing"
        
        citekey = generate_citekey("Cloutier, T.", 2020, "Molecular computations of preferential interactions")
        assert citekey == "cloutier2020molecular"
    
    def test_generate_citekey_firstname_lastname_format(self):
        """Test citekey generation with FirstName LastName format"""
        citekey = generate_citekey("John Smith", 2023, "Testing Paper Title")
        assert citekey == "smith2023testing"
        
        citekey = generate_citekey("Maria Garcia", 2022, "Advanced Research Methods")
        assert citekey == "garcia2022advanced"
    
    def test_generate_citekey_special_characters(self):
        """Test citekey generation with special characters in names"""
        citekey = generate_citekey("O'Connor, P.", 2023, "Complex Author Names")
        assert citekey == "oconnor2023complex"
        
        citekey = generate_citekey("van der Berg, M.", 2023, "Dutch Name Format")
        assert citekey == "vandenberg2023dutch"
    
    def test_generate_citekey_no_year(self):
        """Test citekey generation without year"""
        citekey = generate_citekey("Smith, J.", None, "Test Paper Title")
        assert citekey == "smithunknowntest"
    
    def test_generate_citekey_short_title_words(self):
        """Test citekey generation with short title words"""
        citekey = generate_citekey("Doe, A.", 2023, "A New AI ML Approach")
        assert citekey == "doe2023new"
    
    def test_generate_citekey_no_meaningful_words(self):
        """Test citekey generation with no meaningful words in title"""
        citekey = generate_citekey("Test, A.", 2023, "A An The")
        assert citekey == "test2023paper"
    
    def test_extract_first_author_lastname(self):
        """Test extraction of first author's last name"""
        # Test "LastName, FirstName" format
        lastname = extract_first_author_lastname(["Bonollo, M.", "Smith, J."])
        assert lastname == "Bonollo"
        
        # Test "FirstName LastName" format
        lastname = extract_first_author_lastname(["John Smith", "Jane Doe"])
        assert lastname == "Smith"
        
        # Test empty list
        lastname = extract_first_author_lastname([])
        assert lastname == "Unknown"
        
        # Test single name
        lastname = extract_first_author_lastname(["Smith"])
        assert lastname == "Smith"


class TestFileWriter:
    """Test FileWriter functionality for citekey-based filenames"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.file_writer = FileWriter()
    
    def test_generate_citekey_filename(self):
        """Test citekey-based filename generation"""
        metadata = PaperMetadata(
            title="Advancing Molecular Simulations",
            authors=["Bonollo, M.", "Smith, J."],
            year=2025,
            journal="Test Journal"
        )
        
        filename = self.file_writer.generate_citekey_filename(metadata)
        assert filename == "bonollo2025advancing.md"
    
    def test_generate_citekey_filename_different_format(self):
        """Test citekey filename generation with different format"""
        metadata = PaperMetadata(
            title="Molecular computations of preferential interactions",
            authors=["Cloutier, T.", "Sudrik, C."],
            year=2020,
            journal="Test Journal"
        )
        
        filename = self.file_writer.generate_citekey_filename(metadata, "markdown")
        assert filename == "cloutier2020molecular.md"
    
    def test_generate_citekey_filename_no_authors(self):
        """Test citekey filename generation with no authors"""
        metadata = PaperMetadata(
            title="Anonymous Paper",
            authors=[],
            year=2023,
            journal="Test Journal"
        )
        
        filename = self.file_writer.generate_citekey_filename(metadata)
        # Should use fallback method
        assert filename.endswith(".md")
        assert len(filename) > 4  # More than just ".md"
    
    def test_generate_citekey_filename_no_title(self):
        """Test citekey filename generation with no title"""
        metadata = PaperMetadata(
            title="",
            authors=["Smith, J."],
            year=2023,
            journal="Test Journal"
        )
        
        filename = self.file_writer.generate_citekey_filename(metadata)
        # Should use fallback method
        assert filename.endswith(".md")
        assert len(filename) > 4  # More than just ".md"


class TestRealPDFSamples:
    """Test with real PDF samples from examples directory"""
    
    @pytest.fixture
    def sample_papers(self):
        """Sample paper metadata based on real PDFs"""
        return [
            {
                "metadata": PaperMetadata(
                    title="Advancing Molecular Simulations Merging Physical Models, Experiments, and AI to Tackle Multiscale Challenges",
                    authors=["Bonollo, M.", "Smith, J.", "Doe, A."],
                    year=2025,
                    journal="Test Journal"
                ),
                "expected_citekey": "bonollo2025advancing",
                "expected_filename": "bonollo2025advancing.md",
                "reference_note": "bonollo2025advancing_review_analysis.md"
            },
            {
                "metadata": PaperMetadata(
                    title="Molecular computations of preferential interactions of proline, arginine.HCl, and NaCl with IgG1 antibodies",
                    authors=["Cloutier, T.", "Sudrik, C.", "Mody, N."],
                    year=2020,
                    journal="Test Journal"
                ),
                "expected_citekey": "cloutier2020molecular",
                "expected_filename": "cloutier2020molecular.md",
                "reference_note": "cloutier2020molecular.md"
            },
            {
                "metadata": PaperMetadata(
                    title="Kirkwood–Buff Coarse-Grained Force Fields for Aqueous Solutions",
                    authors=["Ganguly, P.", "Mukherji, D.", "Junghans, C.", "van der Vegt, N.F.A."],
                    year=2012,
                    journal="Test Journal"
                ),
                "expected_citekey": "ganguly2012kirkwood",
                "expected_filename": "ganguly2012kirkwood.md",
                "reference_note": "simon2022kirkwood.md"  # Note: reference might be different
            },
            {
                "metadata": PaperMetadata(
                    title="Coarse-Grained Protein Models and Their Applications",
                    authors=["Kmiecik, S.", "Gront, D.", "Kolinski, M."],
                    year=2016,
                    journal="Test Journal"
                ),
                "expected_citekey": "kmiecik2016coarse",
                "expected_filename": "kmiecik2016coarse.md",
                "reference_note": "kmiecik2016coarsegrained.md"
            },
            {
                "metadata": PaperMetadata(
                    title="Control of viscosity in biopharmaceutical protein formulations",
                    authors=["Zidar, M.", "Kuzman, D.", "Ravnik, M."],
                    year=2020,
                    journal="Test Journal"
                ),
                "expected_citekey": "zidar2020control",
                "expected_filename": "zidar2020control.md",
                "reference_note": "zidar2020control.md"
            }
        ]
    
    def test_sample_papers_citekey_generation(self, sample_papers):
        """Test citekey generation for sample papers"""
        file_writer = FileWriter()
        
        for paper in sample_papers:
            metadata = paper["metadata"]
            expected_citekey = paper["expected_citekey"]
            expected_filename = paper["expected_filename"]
            
            # Test direct citekey generation
            first_author = metadata.authors[0] if metadata.authors else ""
            generated_citekey = generate_citekey(first_author, metadata.year, metadata.title)
            assert generated_citekey == expected_citekey, f"Citekey mismatch for {metadata.title[:30]}..."
            
            # Test filename generation
            generated_filename = file_writer.generate_citekey_filename(metadata)
            assert generated_filename == expected_filename, f"Filename mismatch for {metadata.title[:30]}..."
    
    def test_reference_notes_exist(self, sample_papers):
        """Test that reference notes exist for comparison"""
        reference_dir = Path("/Users/yyangg00/scholarsquill/examples/papers/output literature notes")
        
        if not reference_dir.exists():
            pytest.skip("Reference notes directory not found")
        
        for paper in sample_papers:
            reference_note = paper["reference_note"]
            reference_path = reference_dir / reference_note
            
            # Note: This is informational - we don't require exact matches
            # as the reference notes might have different naming conventions
            if reference_path.exists():
                print(f"✓ Reference note found: {reference_note}")
            else:
                print(f"ℹ Reference note not found: {reference_note}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])