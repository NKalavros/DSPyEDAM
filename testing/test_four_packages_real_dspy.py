#!/usr/bin/env python3

"""
Updated test script for the EDAM ontology matching system using actual DSPy.
Tests the four specific packages: DESeq2, miloR, Rsubread, and GEOquery.
This version uses real DSPy calls instead of simulation.
"""

import os
import sys
from typing import Dict, Any
import json

# Add current directory to path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from edam_ontology_matcher import EDAMMatchingSystem, OntologyMatch

def main():
    """Test the EDAM matching system with four specific packages using actual DSPy."""
    
    print("🧪 Testing EDAM Ontology Matching with Real DSPy")
    print("=" * 55)
    
    # Check for required files
    if not os.path.exists('EDAM.csv'):
        print("❌ Error: EDAM.csv file not found!")
        return
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize the system with DSPy
    print("🚀 Initializing DSPy-based EDAM matching system...")
    system = EDAMMatchingSystem('EDAM.csv')
    
    # Test packages - exactly as specified by the user
    test_packages = [
        {
            "name": "DESeq2",
            "description": "Estimate variance-mean dependence in count data from high-throughput sequencing assays and test for differential expression based on a model using the negative binomial distribution."
        },
        {
            "name": "miloR", 
            "description": "Milo performs single-cell differential abundance testing. Cell states are modelled as representative neighbourhoods on a nearest neighbour graph."
        },
        {
            "name": "Rsubread",
            "description": "Tools for alignment, quantification and analysis of second and third generation sequencing data. It includes the whole pipeline starting from reads mapping to differential expression analysis."
        },
        {
            "name": "GEOquery",
            "description": "The NCBI Gene Expression Omnibus (GEO) is a public repository of microarray and next-generation sequencing functional genomics data. This package provides tools to query and retrieve data from GEO."
        }
    ]
    
    results = []
    
    print(f"\n🔬 Processing {len(test_packages)} packages with real DSPy calls...")
    print("-" * 55)
    
    for i, package in enumerate(test_packages, 1):
        print(f"\n[{i}/{len(test_packages)}] Processing: {package['name']}")
        print(f"Description: {package['description']}")
        
        # Use actual DSPy matching - this makes real API calls
        try:
            match = system.match_package_to_ontology(
                package['name'], 
                package['description']
            )
            
            print(f"\n✅ EDAM Match (via DSPy + OpenAI GPT-4o):")
            print(f"   ID: {match.edam_id}")
            print(f"   Label: {match.edam_label}")
            print(f"   Confidence: {match.confidence_score:.3f}")
            print(f"   Reasoning: {match.reasoning}")
            
            # Store result
            result = {
                "package_name": package['name'],
                "package_description": package['description'],
                "edam_match": {
                    "edam_id": match.edam_id,
                    "edam_label": match.edam_label,
                    "confidence_score": match.confidence_score,
                    "reasoning": match.reasoning
                },
                "method": "DSPy_with_OpenAI_GPT4o"
            }
            results.append(result)
            
        except Exception as e:
            print(f"❌ Error processing {package['name']}: {e}")
            # Store error result
            result = {
                "package_name": package['name'],
                "package_description": package['description'],
                "error": str(e),
                "method": "DSPy_with_OpenAI_GPT4o"
            }
            results.append(result)
    
    # Save results
    output_file = 'four_packages_real_dspy_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎉 Testing complete!")
    print(f"📁 Results saved to: {output_file}")
    
    # Summary statistics
    successful_results = [r for r in results if 'edam_match' in r]
    
    if successful_results:
        confidences = [r['edam_match']['confidence_score'] for r in successful_results]
        avg_confidence = sum(confidences) / len(confidences)
        
        print(f"\n📊 Summary:")
        print(f"   Total packages: {len(results)}")
        print(f"   Successful matches: {len(successful_results)}")
        print(f"   Average confidence: {avg_confidence:.3f}")
        print(f"   High confidence (>0.8): {sum(1 for c in confidences if c > 0.8)}")
        print(f"   Medium confidence (0.5-0.8): {sum(1 for c in confidences if 0.5 <= c <= 0.8)}")
        print(f"   Low confidence (<0.5): {sum(1 for c in confidences if c < 0.5)}")
        
        print(f"\n✅ DSPy integration verified - real API calls are working!")
    else:
        print(f"\n❌ No successful matches - there may be issues with the DSPy integration")

if __name__ == "__main__":
    main()
