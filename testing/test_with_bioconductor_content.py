#!/usr/bin/env python3

"""
Simplified vignette-based test script for EDAM ontology matching.
Downloads vignette content from Bioconductor packages and uses it for matching.

This version focuses on getting the content rather than complex processing.
"""

import os
import sys
import json
import requests
from typing import Dict, Any, List, Optional
import re
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_edam_matcher import EnhancedEDAMMatchingSystem

def fetch_package_info_from_biocviews(package_name: str) -> Dict[str, Any]:
    """
    Fetch package information from Bioconductor, including potential vignette content.
    
    Args:
        package_name: Name of the Bioconductor package
        
    Returns:
        Dictionary with package information and content
    """
    print(f"  📡 Fetching info for {package_name}...")
    
    # Try to get the package page
    package_url = f"https://bioconductor.org/packages/release/bioc/html/{package_name}.html"
    
    try:
        response = requests.get(package_url, timeout=10)
        response.raise_for_status()
        
        content = response.text
        
        # Extract basic information from the page
        info = {
            "package_name": package_name,
            "source_url": package_url,
            "content_type": "bioconductor_page",
            "raw_content": content[:5000],  # First 5000 chars
            "processed_content": ""
        }
        
        # Simple text extraction from HTML
        # Remove HTML tags
        text_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        text_content = re.sub(r'<style[^>]*>.*?</style>', '', text_content, flags=re.DOTALL | re.IGNORECASE)
        text_content = re.sub(r'<[^>]+>', ' ', text_content)
        
        # Clean up whitespace
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Extract key sections
        description_patterns = [
            r'Description[:\s]*([^<\n]+)',
            r'Package[:\s]*([^<\n]+)',
            r'Title[:\s]*([^<\n]+)'
        ]
        
        extracted_text = f"Bioconductor package: {package_name}\n\n"
        
        for pattern in description_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                extracted_text += f"{matches[0]}\n"
        
        # Add some context from the full page
        if len(text_content) > 1000:
            # Take a meaningful chunk from the middle where descriptions usually are
            start_idx = max(0, text_content.find('Description') - 200)
            end_idx = min(len(text_content), start_idx + 2000)
            context_chunk = text_content[start_idx:end_idx]
            extracted_text += f"\nPage content: {context_chunk}"
        else:
            extracted_text += f"\nPage content: {text_content}"
        
        info["processed_content"] = extracted_text
        
        print(f"    ✅ Extracted {len(extracted_text)} characters from package page")
        return info
        
    except Exception as e:
        print(f"    ❌ Error fetching {package_name}: {e}")
        return {
            "package_name": package_name,
            "error": str(e),
            "processed_content": f"Bioconductor package: {package_name} (error fetching details)"
        }

def try_fetch_vignette_directly(package_name: str) -> Optional[str]:
    """
    Try to fetch a vignette directly using common URL patterns.
    
    Args:
        package_name: Name of the package
        
    Returns:
        Vignette content if found, None otherwise
    """
    # Common vignette URL patterns
    vignette_urls = [
        f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/{package_name}.html",
        f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/vignette.html",
        f"https://bioconductor.org/packages/release/bioc/vignettes/{package_name}/inst/doc/{package_name.lower()}.html",
    ]
    
    for url in vignette_urls:
        try:
            print(f"    🔍 Trying vignette URL: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Basic HTML processing
                content = response.text
                
                # Remove scripts and styles
                content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
                content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
                
                # Remove HTML tags
                text_content = re.sub(r'<[^>]+>', ' ', content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                if len(text_content) > 500:  # Minimum meaningful content
                    print(f"    ✅ Found vignette content: {len(text_content)} characters")
                    return text_content[:8000]  # Limit size
                    
        except Exception as e:
            print(f"    ⚠️  Failed to fetch {url}: {e}")
            continue
    
    return None

def get_enhanced_package_content(package_name: str) -> str:
    """
    Get enhanced content for a package including vignettes if available.
    
    Args:
        package_name: Name of the package
        
    Returns:
        Enhanced content string
    """
    print(f"📖 Getting enhanced content for {package_name}...")
    
    # First try to get vignette content
    vignette_content = try_fetch_vignette_directly(package_name)
    
    if vignette_content:
        print(f"  ✅ Using vignette content ({len(vignette_content)} chars)")
        return f"Bioconductor package: {package_name}\n\nVignette content:\n{vignette_content}"
    
    # Fallback to package page info
    print(f"  ⚠️  No vignette found, using package page content")
    package_info = fetch_package_info_from_biocviews(package_name)
    
    return package_info.get("processed_content", f"Bioconductor package: {package_name}")

def main():
    """Test four packages using enhanced content (vignettes + package pages)."""
    
    print("🧪 Testing Four Packages with Enhanced Bioconductor Content")
    print("=" * 65)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        return
    
    # Initialize EDAM system
    print("🚀 Initializing Enhanced EDAM matching system...")
    edam_system = EnhancedEDAMMatchingSystem('EDAM.csv', batch_size=2)
    
    # Test packages
    test_packages = ["DESeq2", "miloR", "Rsubread", "GEOquery"]
    
    print(f"\n📦 Processing {len(test_packages)} packages with Bioconductor content...")
    print("🔍 Will try vignettes first, fallback to package pages")
    print("🎯 Confidence threshold = 0.5 (triggers suggestions)")
    print("-" * 65)
    
    results = []
    
    for i, package_name in enumerate(test_packages, 1):
        print(f"\n[{i}/{len(test_packages)}] Processing: {package_name}")
        
        # Get enhanced content (vignettes or package page)
        enhanced_content = get_enhanced_package_content(package_name)
        
        # Show content preview
        preview = enhanced_content[:200] + "..." if len(enhanced_content) > 200 else enhanced_content
        print(f"  📄 Content preview: {preview}")
        
        # Match to EDAM using enhanced content
        print(f"  🔬 Running EDAM matching...")
        
        try:
            match = edam_system.match_package_to_ontology(
                package_name=package_name,
                package_description=enhanced_content,
                confidence_threshold=0.5
            )
            
            print(f"  ✅ EDAM Match:")
            print(f"     ID: {match.edam_id}")
            print(f"     Label: {match.edam_label}")
            print(f"     Confidence: {match.confidence_score:.3f}")
            print(f"     Validated: {match.validated}")
            
            # Check for suggestions
            if 'NEW DESIGNATION SUGGESTED' in match.reasoning:
                suggestion_part = match.reasoning.split('| NEW DESIGNATION SUGGESTED: ')[1]
                print(f"     💡 NEW DESIGNATION: {suggestion_part}")
            
            # Store result
            result = {
                "package_name": package_name,
                "content_source": "vignette" if "Vignette content:" in enhanced_content else "package_page",
                "content_length": len(enhanced_content),
                "content_preview": enhanced_content[:300] + "..." if len(enhanced_content) > 300 else enhanced_content,
                "edam_match": {
                    "edam_id": match.edam_id,
                    "edam_label": match.edam_label,
                    "confidence_score": match.confidence_score,
                    "reasoning": match.reasoning,
                    "validated": match.validated
                },
                "method": "DSPy_with_Bioconductor_Content"
            }
            results.append(result)
            
        except Exception as e:
            print(f"  ❌ Error matching {package_name}: {e}")
            result = {
                "package_name": package_name,
                "error": str(e),
                "method": "DSPy_with_Bioconductor_Content"
            }
            results.append(result)
    
    # Save results
    output_file = 'four_packages_bioconductor_content.json'
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
        vignette_sources = [r for r in successful_results if r.get('content_source') == 'vignette']
        
        print(f"\n📊 Bioconductor Content Results:")
        print(f"   Total packages: {len(results)}")
        print(f"   Successful matches: {len(successful_results)}")
        print(f"   Used vignettes: {len(vignette_sources)}")
        print(f"   Used package pages: {len(successful_results) - len(vignette_sources)}")
        print(f"   Average confidence: {avg_confidence:.3f}")
        print(f"   High confidence (>0.8): {sum(1 for c in confidences if c > 0.8)}")
        print(f"   Low confidence (<0.5): {sum(1 for c in confidences if c < 0.5)}")
        print(f"   New designations suggested: {len(suggestions)}")
        
        print(f"\n✅ Enhanced Bioconductor content matching completed!")
    else:
        print(f"\n❌ No successful matches")

if __name__ == "__main__":
    main()
