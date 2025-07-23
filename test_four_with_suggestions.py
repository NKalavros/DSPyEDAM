#!/usr/bin/env python3

"""
Test the four packages with the ENHANCED system to show where suggestions go.
This uses the enhanced_edam_matcher.py which includes the suggestion feature.
"""

import os
import sys
import json

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_edam_matcher import EnhancedEDAMMatchingSystem

def main():
    """Test four packages with enhanced system to show suggestion placement."""
    
    print("🧪 Testing Four Packages with Enhanced System (Including Suggestions)")
    print("=" * 70)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        return
    
    # Initialize enhanced system with small batch size
    system = EnhancedEDAMMatchingSystem('EDAM.csv', batch_size=2)
    
    # Test packages
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
    
    print("🔍 Processing with confidence threshold = 0.5")
    print("💡 Low confidence matches will trigger new designation suggestions")
    print("-" * 70)
    
    results = system.process_packages_in_batches(test_packages, confidence_threshold=0.5)
    
    # Save results showing suggestions
    output_file = 'four_packages_with_suggestions.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to: {output_file}")
    
    # Show where suggestions appear
    print(f"\n💡 Where Suggestions Appear:")
    for result in results:
        match = result.get('edam_match', {})
        reasoning = match.get('reasoning', '')
        
        if 'NEW DESIGNATION SUGGESTED' in reasoning:
            print(f"\n🔍 {result['name']} (confidence: {match['confidence_score']:.3f})")
            print(f"   ✅ Suggestion found in reasoning field:")
            
            # Extract just the suggestion part
            parts = reasoning.split('| NEW DESIGNATION SUGGESTED: ')
            if len(parts) > 1:
                suggestion = parts[1]
                print(f"   💡 NEW DESIGNATION SUGGESTED: {suggestion}")
        else:
            print(f"\n✓ {result['name']} (confidence: {match['confidence_score']:.3f}) - No suggestion needed")

if __name__ == "__main__":
    main()
