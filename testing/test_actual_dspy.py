#!/usr/bin/env python3

"""
Test script to verify that DSPy is actually being used for EDAM ontology matching.
This script tests the four specific packages: DESeq2, miloR, Rsubread, and GEOquery.
"""

import os
import sys
from typing import Dict, Any
import json

# Add current directory to path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from edam_ontology_matcher import EDAMMatchingSystem, OntologyMatch

def test_dspy_integration():
    """Test that DSPy is properly integrated and working."""
    
    # Check for required files
    if not os.path.exists('EDAM.csv'):
        print("❌ Error: EDAM.csv file not found!")
        return False
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        return False
    
    print("🧪 Testing DSPy Integration with EDAM Ontology Matching")
    print("=" * 60)
    
    # Initialize the system
    try:
        print("📡 Initializing DSPy system with OpenAI GPT-4o...")
        system = EDAMMatchingSystem('EDAM.csv', openai_api_key=api_key)
        print("✅ DSPy system initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing DSPy system: {e}")
        return False
    
    # Test packages - the 4 specified by the user
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
    
    print(f"\n🔬 Testing {len(test_packages)} packages with actual DSPy calls...")
    print("-" * 60)
    
    for i, package in enumerate(test_packages, 1):
        print(f"\n[{i}/{len(test_packages)}] Processing: {package['name']}")
        print(f"Description: {package['description'][:100]}...")
        
        try:
            # This should make an actual DSPy/OpenAI API call
            match = system.match_package_to_ontology(
                package['name'], 
                package['description']
            )
            
            print(f"✅ DSPy Match Result:")
            print(f"   EDAM ID: {match.edam_id}")
            print(f"   EDAM Label: {match.edam_label}")
            print(f"   Confidence: {match.confidence_score:.3f}")
            print(f"   Reasoning: {match.reasoning}")
            
            # Store result
            result = {
                "package": package,
                "match": {
                    "edam_id": match.edam_id,
                    "edam_label": match.edam_label,
                    "confidence_score": match.confidence_score,
                    "reasoning": match.reasoning
                }
            }
            results.append(result)
            
        except Exception as e:
            print(f"❌ Error processing {package['name']}: {e}")
            print(f"   This indicates a problem with the DSPy integration!")
            return False
    
    # Save results
    output_file = 'dspy_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎉 All tests completed successfully!")
    print(f"📊 Results saved to: {output_file}")
    print(f"✅ DSPy integration is working correctly!")
    
    # Summary statistics
    confidences = [r['match']['confidence_score'] for r in results]
    avg_confidence = sum(confidences) / len(confidences)
    print(f"📈 Average confidence score: {avg_confidence:.3f}")
    
    return True

if __name__ == "__main__":
    success = test_dspy_integration()
    if success:
        print("\n🎯 SUCCESS: DSPy is properly integrated and working!")
    else:
        print("\n💥 FAILURE: DSPy integration has issues!")
        sys.exit(1)
