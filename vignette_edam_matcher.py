#!/usr/bin/env python3
"""
Vignette-based EDAM Ontology Matcher

This script leverages the existing parse_biocviews.py infrastructure to download
and process Bioconductor package vignettes, then uses the enhanced DSPy system
to match them against EDAM ontology terms.

Usage:
    python vignette_edam_matcher.py --packages package1,package2,package3

Example:
    python vignette_edam_matcher.py --packages miloR,xcms,limma,DESeq2
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any, Optional
import tempfile
import shutil

# Import the existing infrastructure
from parse_biocviews import download_if_accessible, convert_html_to_markdown, process_with_pymu4llm

# Import the enhanced EDAM matcher
try:
    from enhanced_edam_matcher import EnhancedEDAMMatchingSystem
except ImportError:
    print("Error: enhanced_edam_matcher.py not found. Please ensure it exists in the same directory.")
    sys.exit(1)


MAX_CONTENT_LENGTH=10000  # Limit content size to avoid context issues

class VignetteEDAMMatcher:
    """Matches Bioconductor package vignettes to EDAM ontology using DSPy."""
    
    def __init__(self, edam_csv_path: str = "EDAM.csv", 
                 openai_api_key: Optional[str] = None):
        """Initialize the vignette EDAM matcher."""
        self.edam_csv_path = edam_csv_path
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Initialize the enhanced EDAM matcher
        self.matcher = EnhancedEDAMMatchingSystem(
            edam_csv_path=edam_csv_path,
            openai_api_key=self.openai_api_key
        )
        
        print(f"Initialized VignetteEDAMMatcher with {len(self.matcher.validator.valid_ids)} EDAM terms")
    
    def create_package_vignette_url(self, package_name: str) -> List[str]:
        """Create vignette URLs for a given package."""
        # Base URL patterns for Bioconductor vignettes
        base_urls = [
            f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/",
            f"https://bioconductor.org/packages/devel/bioc/vignettes/{package_name}/inst/doc/"
        ]
        
        # Common vignette file patterns
        file_patterns = [
            f"{package_name}.html",
            f"{package_name}.pdf",
            f"{package_name}_vignette.html",
            f"{package_name}_vignette.pdf",
            "vignette.html",
            "vignette.pdf",
            "intro.html",
            "intro.pdf"
        ]
        
        urls = []
        for base_url in base_urls:
            for pattern in file_patterns:
                urls.append(f"{base_url}{pattern}")
        
        return urls
    
    def download_package_vignettes(self, package_name: str, download_dir: str) -> List[str]:
        """Download vignettes for a specific package."""
        print(f"\n[PROGRESS] Downloading vignettes for package: {package_name}")
        # Create package-specific directory
        package_dir = os.path.join(download_dir, package_name)
        os.makedirs(package_dir, exist_ok=True)
        # Get potential vignette URLs
        vignette_urls = self.create_package_vignette_url(package_name)
        downloaded_files = []
        for url in vignette_urls:
            print(f"[PROGRESS] Attempting to download: {url}")
            downloaded_file = download_if_accessible(url, package_dir)
            if downloaded_file:
                downloaded_files.append(downloaded_file)
                print(f"[PROGRESS] ✅ Downloaded: {downloaded_file}")
                break  # Stop after first successful download
            else:
                print(f"[PROGRESS] ❌ Failed to download: {url}")
        if not downloaded_files:
            print(f"[PROGRESS] ⚠️  No vignettes found for {package_name}")
        return downloaded_files
    
    def process_vignette_files(self, file_paths: List[str]) -> List[str]:
        """Process downloaded vignette files into extractable text."""
        processed_files = []
        for file_path in file_paths:
            print(f"[PROGRESS] Processing file: {file_path}")
            try:
                if file_path.endswith('.html'):
                    print(f"[PROGRESS] Converting HTML to markdown: {file_path}")
                    markdown_file = convert_html_to_markdown(file_path)
                    if markdown_file:
                        print(f"[PROGRESS] Processing markdown with PyMu4LLM: {markdown_file}")
                        processed_file = process_with_pymu4llm(markdown_file)
                        if processed_file:
                            processed_files.append(processed_file)
                            print(f"[PROGRESS] ✅ Processed HTML->MD->TXT: {processed_file}")
                elif file_path.endswith('.pdf'):
                    print(f"[PROGRESS] Processing PDF with PyMu4LLM: {file_path}")
                    processed_file = process_with_pymu4llm(file_path)
                    if processed_file:
                        processed_files.append(processed_file)
                        print(f"[PROGRESS] ✅ Processed PDF->TXT: {processed_file}")
                else:
                    print(f"[PROGRESS] ⚠️  Unsupported file type: {file_path}")
            except Exception as e:
                print(f"[PROGRESS] ❌ Error processing {file_path}: {e}")
        return processed_files
    
    def extract_text_content(self, processed_files: List[str]) -> str:
        """Extract and combine text content from processed files, removing images and base64 blobs."""
        import re
        combined_content = []
        for file_path in processed_files:
            print(f"[PROGRESS] Extracting text from: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove Markdown images: ![alt](url)
                    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
                    # Remove HTML <img ...> tags
                    content = re.sub(r'<img[^>]*>', '', content, flags=re.IGNORECASE)
                    # Remove base64 blobs (data:image/...)
                    content = re.sub(r'data:image/[^\s\)]+', '', content)
                    # Remove long base64-like lines (over 500 chars, likely images)
                    content = re.sub(r'^[A-Za-z0-9+/=]{500,}$', '', content, flags=re.MULTILINE)
                    combined_content.append(content)
                    print(f"[PROGRESS] ✅ Extracted {len(content)} characters from {file_path} (images removed)")
            except Exception as e:
                print(f"[PROGRESS] ❌ Error reading {file_path}: {e}")
        # Combine all content with separators
        full_content = "\n\n---\n\n".join(combined_content)
        # Limit content size to avoid context issues (approximately 50,000 characters)
        if len(full_content) > MAX_CONTENT_LENGTH:
            print(f"[PROGRESS] ⚠️  Content too long ({len(full_content)} chars), truncating to 50,000")
            full_content = full_content[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"
        return full_content
    
    def process_packages(self, package_names: List[str], output_file: Optional[str] = None) -> Dict[str, Any]:
        """Process a list of packages and match their vignettes to EDAM terms."""
        print(f"[PROGRESS] Starting vignette processing for {len(package_names)} package(s)")
        # Create temporary download directory
        with tempfile.TemporaryDirectory() as temp_dir:
            download_dir = os.path.join(temp_dir, "vignette_downloads")
            os.makedirs(download_dir, exist_ok=True)
            print(f"[PROGRESS] Using temporary directory: {download_dir}")
            # Prepare packages for EDAM matching
            packages_for_matching = []
            for package_name in package_names:
                print(f"\n{'='*60}")
                print(f"[PROGRESS] Processing package: {package_name}")
                print(f"{'='*60}")
                # Download vignettes
                downloaded_files = self.download_package_vignettes(package_name, download_dir)
                if not downloaded_files:
                    print(f"[PROGRESS] ⚠️  No vignettes downloaded for {package_name}, skipping...")
                    continue
                # Process files
                processed_files = self.process_vignette_files(downloaded_files)
                if not processed_files:
                    print(f"[PROGRESS] ⚠️  No files processed for {package_name}, skipping...")
                    continue
                # Extract text content
                text_content = self.extract_text_content(processed_files)
                if not text_content:
                    print(f"[PROGRESS] ⚠️  No text content extracted for {package_name}, skipping...")
                    continue
                # Add to packages for matching
                packages_for_matching.append({
                    "name": package_name,  # Use "name" field as expected by enhanced matcher
                    "description": text_content,  # Using vignette content as "description"
                    "source": "vignette"
                })
                print(f"[PROGRESS] ✅ Ready for EDAM matching: {package_name} ({len(text_content)} chars)")
        # Run EDAM matching using enhanced system
        if packages_for_matching:
            print(f"\n{'='*60}")
            print(f"[PROGRESS] Running Enhanced EDAM Matching")
            print(f"{'='*60}")
            batch_results = self.matcher.process_packages_in_batches(
                packages_for_matching,
                confidence_threshold=0.5
            )
            # Create summary statistics
            total_packages = len(batch_results)
            total_matches = len([r for r in batch_results if 'edam_match' in r])
            confidences = [r.get('confidence', 0) for r in batch_results if 'confidence' in r]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            high_confidence = len([c for c in confidences if c > 0.7])
            low_confidence = len([c for c in confidences if c < 0.5])
            new_designations = len([r for r in batch_results if 'new_designation' in r])
            results = {
                "packages": batch_results,
                "summary": {
                    "total_packages": total_packages,
                    "total_matches": total_matches,
                    "average_confidence": avg_confidence,
                    "high_confidence_count": high_confidence,
                    "low_confidence_count": low_confidence,
                    "new_designations_count": new_designations
                }
            }
            # Save results if output file specified
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"[PROGRESS] ✅ Results saved to: {output_file}")
            return results
        else:
            print("[PROGRESS] ❌ No packages could be processed for EDAM matching")
            return {"packages": [], "summary": {"total_packages": 0}}


def main():
    """Main entry point for the vignette EDAM matcher."""
    
    parser = argparse.ArgumentParser(description="Match Bioconductor package vignettes to EDAM ontology")
    parser.add_argument(
        "--packages", 
        type=str, 
        required=True,
        help="Comma-separated list of Bioconductor package names"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="vignette_edam_results.json",
        help="Output file for results (default: vignette_edam_results.json)"
    )
    parser.add_argument(
        "--edam-csv", 
        type=str, 
        default="EDAM.csv",
        help="Path to EDAM CSV file (default: EDAM.csv)"
    )
    
    args = parser.parse_args()
    
    # Parse package names
    package_names = [pkg.strip() for pkg in args.packages.split(",")]
    
    print(f"Vignette-based EDAM Ontology Matcher")
    print(f"{'='*60}")
    print(f"Packages to process: {package_names}")
    print(f"Output file: {args.output}")
    print(f"EDAM CSV: {args.edam_csv}")
    
    try:
        # Initialize matcher
        matcher = VignetteEDAMMatcher(edam_csv_path=args.edam_csv)
        
        # Process packages
        results = matcher.process_packages(package_names, output_file=args.output)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"Total packages processed: {results['summary']['total_packages']}")
        print(f"Total matches found: {results['summary']['total_matches']}")
        print(f"Average confidence: {results['summary']['average_confidence']:.3f}")
        print(f"High confidence matches (>0.7): {results['summary']['high_confidence_count']}")
        print(f"Low confidence matches (<0.5): {results['summary']['low_confidence_count']}")
        print(f"New designations suggested: {results['summary']['new_designations_count']}")
        
        # Show individual results
        for pkg_result in results["packages"]:
            print(f"\n📦 {pkg_result['name']}:")
            print(f"   Match: {pkg_result['edam_match']['label']}")
            print(f"   ID: {pkg_result['edam_match']['id']}")
            print(f"   Confidence: {pkg_result['confidence']:.3f}")
            
            if "new_designation" in pkg_result:
                print(f"   💡 Suggestion: {pkg_result['new_designation']}")
        
        print(f"\n✅ Complete! Results saved to {args.output}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
