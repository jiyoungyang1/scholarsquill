#!/usr/bin/env python3
"""
Main execution script for ScholarsQuill Kiro MCP Server
Demonstrates complete workflow integration and provides CLI interface
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from .server import ScholarsQuillKiroServer
from .config import ServerConfig
from .models import FocusType, DepthType, FormatType, CodelangFocusType, SectionFilterType
from .utils import setup_logging


class ScholarsQuillKiroCLI:
    """Command-line interface for ScholarsQuill Kiro"""
    
    def __init__(self):
        self.server: Optional[ScholarsQuillKiroServer] = None
    
    async def initialize(self, config: Optional[ServerConfig] = None) -> None:
        """Initialize the server"""
        if not config:
            config = ServerConfig.from_env()
        
        self.server = ScholarsQuillKiroServer(config)
        await self.server.initialize()
    
    async def process_file(
        self,
        file_path: str,
        focus: str = "balanced",
        depth: str = "standard",
        output_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Process a single PDF file"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        if verbose:
            print(f"Processing file: {file_path}")
            print(f"Focus: {focus}, Depth: {depth}")
            if output_dir:
                print(f"Output directory: {output_dir}")
        
        result = await self.server.process_note_command(
            target=file_path,
            focus=focus,
            depth=depth,
            output_dir=output_dir
        )
        
        if verbose:
            if result["success"]:
                print(f"✓ Successfully processed: {result['output_path']}")
                print(f"  Paper type: {result['analysis']['paper_type']} (confidence: {result['analysis']['confidence']:.2f})")
                print(f"  Processing time: {result['timing']['total_time_seconds']:.2f}s")
            else:
                print(f"✗ Failed to process: {result['error']}")
        
        return result
    
    async def process_batch(
        self,
        directory_path: str,
        focus: str = "balanced",
        depth: str = "standard",
        output_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Process multiple PDF files in batch mode"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        if verbose:
            print(f"Processing directory: {directory_path}")
            print(f"Focus: {focus}, Depth: {depth}")
            if output_dir:
                print(f"Output directory: {output_dir}")
        
        result = await self.server.process_note_command(
            target=directory_path,
            focus=focus,
            depth=depth,
            batch=True,
            output_dir=output_dir
        )
        
        if verbose:
            if result["success"]:
                summary = result["summary"]
                print(f"✓ Batch processing completed:")
                print(f"  Total files: {summary['total_files']}")
                print(f"  Successful: {summary['successful_extractions']}")
                print(f"  Failed: {summary['failed_extractions']}")
                print(f"  Success rate: {summary['success_rate']:.1%}")
                print(f"  Total time: {summary['total_processing_time_seconds']:.2f}s")
            else:
                print(f"✗ Batch processing failed: {result['error']}")
        
        return result
    
    async def process_minireview(
        self,
        directory_path: str,
        topic: str,
        focus: str = "review",
        depth: str = "standard",
        output_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Process multiple PDF files to create a comprehensive mini-review"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        if verbose:
            print(f"Creating mini-review for directory: {directory_path}")
            print(f"Topic: {topic}")
            print(f"Focus: {focus}, Depth: {depth}")
            if output_dir:
                print(f"Output directory: {output_dir}")
        
        result = await self.server.process_note_command(
            target=directory_path,
            focus=focus,
            depth=depth,
            minireview=True,
            topic=topic,
            output_dir=output_dir
        )
        
        if verbose:
            if result["success"]:
                review_info = result.get("minireview_result", {})
                print(f"✓ Mini-review creation completed:")
                print(f"  Topic: {review_info.get('topic', 'Unknown')}")
                print(f"  Papers analyzed: {review_info.get('papers_analyzed', 0)}")
                print(f"  Output file: {review_info.get('output_filename', 'Unknown')}")
                print(f"  File size: {review_info.get('file_size', 0)} bytes")
                print(f"  Focus: {review_info.get('focus', 'Unknown')}")
                print(f"  Depth: {review_info.get('depth', 'Unknown')}")
            else:
                print(f"✗ Mini-review creation failed: {result['error']}")
        
        return result
    
    async def process_citemap(
        self,
        target: str,
        batch: bool = False,
        keyword: Optional[str] = None,
        output_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Process PDF files to create citation context maps"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        if verbose:
            print(f"Starting citemap analysis: target={target}, batch={batch}")
            if output_dir:
                print(f"Output directory: {output_dir}")
        
        result = await self.server.server.run_tool(
            "sq_citemap",
            target=target,
            batch=batch,
            keyword=keyword,
            output_dir=output_dir
        )
        
        if verbose:
            if result["success"]:
                if batch:
                    summary = result.get("batch_summary", {})
                    print(f"✓ Batch citemap analysis completed:")
                    print(f"  Total papers: {summary.get('total_papers', 0)}")
                    print(f"  Processed papers: {summary.get('processed_papers', 0)}")
                    print(f"  Total references: {summary.get('total_references', 0)}")
                    print(f"  Total citation contexts: {summary.get('total_citation_contexts', 0)}")
                    print(f"  Common sources found: {summary.get('common_sources_found', 0)}")
                    print(f"  Cross-references identified: {summary.get('cross_references_identified', 0)}")
                    print(f"  Output file: {result.get('output_path', 'Unknown')}")
                else:
                    analysis_summary = result.get("analysis_summary", {})
                    print(f"✓ Single citemap analysis completed:")
                    print(f"  Total citations: {analysis_summary.get('total_citations', 0)}")
                    print(f"  Unique references: {analysis_summary.get('unique_references', 0)}")
                    print(f"  Network nodes: {analysis_summary.get('network_nodes', 0)}")
                    print(f"  Network edges: {analysis_summary.get('network_edges', 0)}")
                    print(f"  Output file: {result.get('output_path', 'Unknown')}")
            else:
                print(f"✗ Citemap analysis failed: {result['error']}")
        
        return result
    
    async def process_codelang(
        self,
        target: str,
        field: str = "auto-detect",
        focus: str = "discourse",
        section_filter: str = "all",
        depth: str = "standard",
        batch: bool = False,
        keyword: Optional[str] = None,
        output_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        if not self.server:
            raise RuntimeError("Server not initialized")

        if verbose:
            print(f"Starting codelang analysis: target={target}, focus={focus}, batch={batch}")
            if output_dir:
                print(f"Output directory: {output_dir}")

        result = await self.server.server.run_tool(
            "sq_codelang",
            target=target,
            field=field,
            focus=focus,
            section_filter=section_filter,
            depth=depth,
            batch=batch,
            keyword=keyword,
            output_dir=output_dir
        )

        if verbose:
            if result["success"]:
                if batch:
                    summary = result["summary"]
                    print(f"✓ Batch codelang analysis completed:")
                    print(f"  Total files: {summary['total_files']}")
                    print(f"  Successful extractions: {summary['successful_extractions']}")
                    print(f"  Failed extractions: {summary['failed_extractions']}")
                    print(f"  Success rate: {summary['success_rate']:.1%}")
                    print(f"  Output directory: {result['output_info']['suggested_directory']}")
                    print(f"  Generated file: {result['output_info']['full_suggested_path']}")
                else:
                    print(f"✓ Single codelang analysis completed. Output: {result['output_info']['full_suggested_path']}")
            else:
                print(f"✗ Codelang analysis failed: {result['error']}")

        return result
    
    async def analyze_paper(
        self,
        file_path: str,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Analyze paper type without generating notes"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        if verbose:
            print(f"Analyzing paper: {file_path}")
        
        result = await self.server.analyze_paper_type(file_path)
        
        if verbose:
            if result["success"]:
                print(f"✓ Analysis completed:")
                print(f"  Paper type: {result['paper_type']}")
                print(f"  Confidence: {result['confidence_score']:.2f}")
                print(f"  Title: {result['metadata']['title'][:60]}...")
                print(f"  Authors: {', '.join(result['metadata']['authors'][:3])}")
                if len(result['metadata']['authors']) > 3:
                    print(f"    ... and {len(result['metadata']['authors']) - 3} more")
            else:
                print(f"✗ Analysis failed: {result['error']}")
        
        return result
    
    async def list_templates(self, verbose: bool = False) -> Dict[str, Any]:
        """List available templates"""
        if not self.server:
            raise RuntimeError("Server not initialized")
        
        result = await self.server.get_available_templates()
        
        if verbose and result["success"]:
            print("Available templates:")
            for template_name, template_info in result["templates"].items():
                print(f"  {template_name}: {template_info['name']}")
                print(f"    {template_info['description']}")
                print(f"    Sections: {', '.join(template_info['sections'][:3])}...")
                print()
        
        return result
    
    async def shutdown(self) -> None:
        """Shutdown the server"""
        if self.server:
            await self.server.shutdown()


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="ScholarsQuill Kiro - PDF to Literature Notes Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  python -m src.main process paper.pdf --focus research --depth deep
  
  # Process all PDFs in a directory
  python -m src.main batch /path/to/papers/ --focus theory --output /path/to/notes/
  
  # Create a comprehensive mini-review
  python -m src.main minireview /path/to/papers/ --topic "protein folding mechanisms" --focus review --depth deep
  
  # Create citation context map for single paper
  python -m src.main citemap paper.pdf
  
  # Create batch citemap with cross-reference analysis
  python -m src.main citemap /path/to/papers/ --batch
  
  # Analyze paper type only
  python -m src.main analyze paper.pdf
  
  # List available templates
  python -m src.main templates
        """
    )
    
    # Global options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")
    parser.add_argument("--output-dir", "-o", help="Output directory for generated notes")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process a single PDF file")
    process_parser.add_argument("file", help="Path to PDF file")
    process_parser.add_argument("--focus", default="balanced", choices=[f.value for f in FocusType], help="Analysis focus")
    process_parser.add_argument("--depth", default="standard", choices=[d.value for d in DepthType], help="Analysis depth")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Process multiple PDF files")
    batch_parser.add_argument("directory", help="Directory containing PDF files")
    batch_parser.add_argument("--focus", default="balanced", choices=[f.value for f in FocusType], help="Analysis focus")
    batch_parser.add_argument("--depth", default="standard", choices=[d.value for d in DepthType], help="Analysis depth")
    
    # Mini-review command
    minireview_parser = subparsers.add_parser("minireview", help="Create comprehensive topic-focused mini-review")
    minireview_parser.add_argument("directory", help="Directory containing PDF files")
    minireview_parser.add_argument("--topic", required=True, help="Topic focus for the mini-review (required)")
    minireview_parser.add_argument("--focus", default="review", choices=[f.value for f in FocusType], help="Analysis focus")
    minireview_parser.add_argument("--depth", default="standard", choices=[d.value for d in DepthType], help="Analysis depth")
    minireview_parser.add_argument("--output-dir", help="Output directory for generated mini-review")
    minireview_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze paper type without generating notes")
    analyze_parser.add_argument("file", help="Path to PDF file")
    
    # Templates command
    templates_parser = subparsers.add_parser("templates", help="List available templates")
    
    # Codelang command
    codelang_parser = subparsers.add_parser("codelang", help="Perform codelang discourse analysis on PDF files")
    codelang_parser.add_argument("target", help="Path to PDF file or directory")
    codelang_parser.add_argument("--field", default="auto-detect", help="Academic field for context")
    codelang_parser.add_argument("--focus", default="discourse", choices=[f.value for f in CodelangFocusType], help="Analysis focus")
    codelang_parser.add_argument("--section-filter", default="all", choices=[s.value for s in SectionFilterType], help="Paper sections to analyze")
    codelang_parser.add_argument("--depth", default="standard", choices=[d.value for d in DepthType], help="Analysis depth")
    codelang_parser.add_argument("--batch", action="store_true", help="Enable batch processing for directories")
    codelang_parser.add_argument("--keyword", help="Keyword for batch filename (Codelang_[keyword]_[focus].md)")
    
    # Citemap command
    citemap_parser = subparsers.add_parser("citemap", help="Create citation context maps and reference networks")
    citemap_parser.add_argument("target", help="Path to PDF file or directory")
    citemap_parser.add_argument("--batch", action="store_true", help="Enable batch processing for directories with cross-reference analysis")
    citemap_parser.add_argument("--keyword", help="Keyword for batch filename (Citemap_[keyword]_[count].md)")
    
    # Server command (for MCP mode)
    server_parser = subparsers.add_parser("server", help="Run as MCP server")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Create CLI instance
    cli = ScholarsQuillKiroCLI()
    
    try:
        # Initialize server
        config = ServerConfig.from_env()
        config.log_level = args.log_level
        await cli.initialize(config)
        
        # Execute command
        if args.command == "process":
            result = await cli.process_file(
                args.file,
                focus=args.focus,
                depth=args.depth,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            
            if not args.verbose:
                print(json.dumps(result, indent=2))
            
            return 0 if result["success"] else 1
        
        elif args.command == "batch":
            result = await cli.process_batch(
                args.directory,
                focus=args.focus,
                depth=args.depth,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            
            if not args.verbose:
                print(json.dumps(result, indent=2))
            
            return 0 if result["success"] else 1
        
        elif args.command == "minireview":
            result = await cli.process_minireview(
                args.directory,
                topic=args.topic,
                focus=args.focus,
                depth=args.depth,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            
            if not args.verbose:
                print(json.dumps(result, indent=2))
            
            return 0 if result["success"] else 1
        
        elif args.command == "analyze":
            result = await cli.analyze_paper(
                args.file,
                verbose=args.verbose
            )
            
            if not args.verbose:
                print(json.dumps(result, indent=2))
            
            return 0 if result["success"] else 1
        
        elif args.command == "templates":
            result = await cli.list_templates(verbose=True)
            
            if not args.verbose:
                print(json.dumps(result, indent=2))
            
            return 0 if result["success"] else 1
        
        elif args.command == "codelang":
            result = await cli.process_codelang(
                args.target,
                field=args.field,
                focus=args.focus,
                section_filter=args.section_filter,
                depth=args.depth,
                batch=args.batch,
                keyword=args.keyword,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            if not args.verbose:
                print(json.dumps(result, indent=2))
            return 0 if result["success"] else 1
        
        elif args.command == "citemap":
            result = await cli.process_citemap(
                args.target,
                batch=args.batch,
                keyword=args.keyword,
                output_dir=args.output_dir,
                verbose=args.verbose
            )
            
            if not args.verbose:
                print(json.dumps(result, indent=2))
            
            return 0 if result["success"] else 1
        
        elif args.command == "server":
            # Run as MCP server
            from mcp.server.stdio import stdio_server
            
            print("Starting ScholarsQuill Kiro MCP Server...", file=sys.stderr)
            
            async with stdio_server() as (read_stream, write_stream):
                await cli.server.get_server().run(
                    read_stream,
                    write_stream,
                    cli.server.get_server().create_initialization_options()
                )
            
            return 0
        
        else:
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    finally:
        await cli.shutdown()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))