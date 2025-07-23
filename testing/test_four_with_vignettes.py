#!/usr/bin/env python3

"""
Enhanced test script that downloads package vignettes from Bioconductor 
and uses them for EDAM ontology matching instead of just descriptions.

This script:
1. Fetches package vignettes from Bioconductor
2. Processes vignettes (HTML/PDF) to extract text content  
3. Uses vignette content for EDAM matching with suggestions
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import subprocess

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_edam_matcher import EnhancedEDAMMatchingSystem

class BioconductorVignetteProcessor:
    """Downloads and processes Bioconductor package vignettes."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the vignette processor."""
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp())
        self.temp_dir.mkdir(exist_ok=True)
        
        print(f"📁 Using temporary directory: {self.temp_dir}")
    
    def get_package_vignettes(self, package_name: str) -> List[Dict[str, str]]:
        """
        Get list of available vignettes for a Bioconductor package.
        
        Args:
            package_name: Name of the Bioconductor package
            
        Returns:
            List of vignette dictionaries with title, url, and format
        """
        # Bioconductor package URL pattern
        base_url = f"https://bioconductor.org/packages/release/bioc/html/{package_name}.html"
        
        print(f"  📡 Fetching vignette list for {package_name}...")
        
        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
            
            # Simple parsing to find vignettes (this is a basic implementation)
            # In practice, you'd want more robust HTML parsing
            content = response.text
            vignettes = []
            
            # Look for common vignette patterns
            if ".html" in content or ".pdf" in content:
                # For this demo, we'll construct likely vignette URLs
                vignette_urls = [
                    f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/{package_name}.html",
                    f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/{package_name}.pdf",
                    f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/vignette.html",
                    f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/vignette.pdf"
                ]
                
                for url in vignette_urls:
                    try:
                        head_response = requests.head(url, timeout=5)
                        if head_response.status_code == 200:
                            file_type = "html" if url.endswith(".html") else "pdf"
                            vignettes.append({
                                "title": f"{package_name} vignette",
                                "url": url,
                                "format": file_type
                            })
                            print(f"    ✅ Found {file_type.upper()} vignette: {url}")
                    except:
                        continue
            
            if not vignettes:
                print(f"    ⚠️  No vignettes found for {package_name}")
            
            return vignettes
            
        except Exception as e:
            print(f"    ❌ Error fetching vignettes for {package_name}: {e}")
            return []
    
    def download_vignette(self, vignette: Dict[str, str]) -> Optional[Path]:
        """
        Download a vignette file.
        
        Args:
            vignette: Vignette dictionary with url and format
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            response = requests.get(vignette["url"], timeout=30)
            response.raise_for_status()
            
            # Create filename
            filename = f"vignette_{hash(vignette['url'])}_{vignette['format']}"
            file_path = self.temp_dir / filename
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"    📥 Downloaded: {file_path.name}")
            return file_path
            
        except Exception as e:
            print(f"    ❌ Error downloading vignette: {e}")
            return None
    
    def process_html_vignette(self, file_path: Path) -> str:
        """
        Process HTML vignette to extract text content.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            Extracted text content
        """
        try:
            # Try using pandoc if available
            result = subprocess.run([
                'pandoc', str(file_path), '-t', 'plain'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"    ✅ Processed HTML with pandoc")
                return result.stdout
            else:
                # Fallback to simple HTML reading
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic HTML tag removal
                import re
                text = re.sub(r'<[^>]+>', ' ', content)
                text = re.sub(r'\s+', ' ', text).strip()
                
                print(f"    ✅ Processed HTML with basic parsing")
                return text
                
        except Exception as e:
            print(f"    ❌ Error processing HTML: {e}")
            return ""
    
    def process_pdf_vignette(self, file_path: Path) -> str:
        """
        Process PDF vignette to extract text content.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            # Try using pymupdf4llm if available
            try:
                import pymupdf4llm
                md_text = pymupdf4llm.to_markdown(str(file_path))
                print(f"    ✅ Processed PDF with pymupdf4llm")
                return md_text
            except ImportError:
                print(f"    ⚠️  pymupdf4llm not available, trying pdfplumber...")
                
                # Fallback to pdfplumber if available
                try:
                    try:
                        import pdfplumber
                    except ImportError:
                        print(f"    ❌ pdfplumber not available")
                        return ""
                        
                    text = ""
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    
                    print(f"    ✅ Processed PDF with pdfplumber")
                    return text
                except Exception as e2:
                    print(f"    ❌ pdfplumber failed: {e2}")
                    return ""
                    
        except Exception as e:
            print(f"    ❌ Error processing PDF: {e}")
            return ""
    
    def get_package_vignette_content(self, package_name: str, max_length: int = 10000) -> str:
        """
        Get processed vignette content for a package.
        
        Args:
            package_name: Name of the Bioconductor package
            max_length: Maximum length of content to return
            
        Returns:
            Processed vignette content as text
        """
        print(f"📖 Processing vignettes for {package_name}...")
        
        # Get available vignettes
        vignettes = self.get_package_vignettes(package_name)
        
        if not vignettes:
            print(f"  ⚠️  No vignettes found, using package name only")
            return f"Bioconductor package: {package_name}"
        
        all_content = []
        
        for i, vignette in enumerate(vignettes[:2]):  # Limit to first 2 vignettes
            print(f"  📄 Processing vignette {i+1}/{min(len(vignettes), 2)}: {vignette['format'].upper()}")
            
            # Download vignette
            file_path = self.download_vignette(vignette)
            if not file_path:
                continue
            
            # Process based on format
            if vignette['format'] == 'html':
                content = self.process_html_vignette(file_path)
            elif vignette['format'] == 'pdf':
                content = self.process_pdf_vignette(file_path)
            else:
                content = ""
            
            if content:
                all_content.append(content)
            
            # Clean up downloaded file
            try:
                file_path.unlink()
            except:
                pass
        
        # Combine all content
        combined_content = "\n\n".join(all_content)
        
        # Truncate if too long
        if len(combined_content) > max_length:
            combined_content = combined_content[:max_length] + "..."
            print(f"  ✂️  Content truncated to {max_length} characters")
        
        if combined_content:
            print(f"  ✅ Extracted {len(combined_content)} characters from vignettes")
        else:
            print(f"  ⚠️  No content extracted, using package name")
            combined_content = f"Bioconductor package: {package_name}"
        
        return combined_content


def main():
    """Test four packages using vignette content instead of descriptions."""
    
    print("🧪 Testing Four Packages with Vignette Content + Enhanced EDAM System")
    print("=" * 75)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        return
    
    # Initialize systems
    print("🚀 Initializing systems...")
    vignette_processor = BioconductorVignetteProcessor()
    edam_system = EnhancedEDAMMatchingSystem('EDAM.csv', batch_size=2)
    
    # Test packages
    test_packages = ["DESeq2", "miloR", "Rsubread", "GEOquery"]
    
    print(f"\n📦 Processing {len(test_packages)} packages with vignette content...")
    print("🔍 Confidence threshold = 0.5 (low confidence triggers suggestions)")
    print("-" * 75)
    
    results = []
    
    for i, package_name in enumerate(test_packages, 1):
        print(f"\n[{i}/{len(test_packages)}] Processing: {package_name}")
        
        # Get vignette content
        vignette_content = vignette_processor.get_package_vignette_content(package_name)
        
        # Match to EDAM using vignette content
        print(f"  🔬 Running EDAM matching with vignette content...")
        
        try:
            match = edam_system.match_package_to_ontology(
                package_name=package_name,
                package_description=vignette_content,  # Using vignette content instead of description
                confidence_threshold=0.5
            )
            
            print(f"  ✅ EDAM Match:")
            print(f"     ID: {match.edam_id}")
            print(f"     Label: {match.edam_label}")
            print(f"     Confidence: {match.confidence_score:.3f}")
            print(f"     Validated: {match.validated}")
            
            if 'NEW DESIGNATION SUGGESTED' in match.reasoning:
                suggestion_part = match.reasoning.split('| NEW DESIGNATION SUGGESTED: ')[1]
                print(f"     💡 Suggestion: {suggestion_part}")
            
            # Store result
            result = {
                "package_name": package_name,
                "vignette_content_length": len(vignette_content),
                "vignette_content_preview": vignette_content[:200] + "..." if len(vignette_content) > 200 else vignette_content,
                "edam_match": {
                    "edam_id": match.edam_id,
                    "edam_label": match.edam_label,
                    "confidence_score": match.confidence_score,
                    "reasoning": match.reasoning,
                    "validated": match.validated
                },
                "method": "DSPy_with_Vignette_Content"
            }
            results.append(result)
            
        except Exception as e:
            print(f"  ❌ Error processing {package_name}: {e}")
            result = {
                "package_name": package_name,
                "error": str(e),
                "method": "DSPy_with_Vignette_Content"
            }
            results.append(result)
    
    # Save results
    output_file = 'four_packages_vignette_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 Results saved to: {output_file}")
    
    # Summary
    successful_results = [r for r in results if 'edam_match' in r]
    
    if successful_results:
        confidences = [r['edam_match']['confidence_score'] for r in successful_results]
        avg_confidence = sum(confidences) / len(confidences)
        suggestions = [r for r in successful_results if 'NEW DESIGNATION SUGGESTED' in r['edam_match']['reasoning']]
        
        print(f"\n📊 Vignette-Based Results Summary:")
        print(f"   Total packages: {len(results)}")
        print(f"   Successful matches: {len(successful_results)}")
        print(f"   Average confidence: {avg_confidence:.3f}")
        print(f"   High confidence (>0.8): {sum(1 for c in confidences if c > 0.8)}")
        print(f"   Medium confidence (0.5-0.8): {sum(1 for c in confidences if 0.5 <= c <= 0.8)}")
        print(f"   Low confidence (<0.5): {sum(1 for c in confidences if c < 0.5)}")
        print(f"   New designations suggested: {len(suggestions)}")
        
        print(f"\n✅ Vignette-based EDAM matching completed successfully!")
    else:
        print(f"\n❌ No successful matches")


if __name__ == "__main__":
    main()
