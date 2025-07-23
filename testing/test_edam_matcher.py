#!/usr/bin/env python3
"""
Test script for the EDAM ontology matcher.
This will test with a simple example before running on the full dataset.
"""

import os
import sys

def test_edam_matcher():
    """Test the EDAM ontology matching system with a simple example."""
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running the full system:")
        print("export OPENAI_API_KEY='your-key-here'")
        print("")
        print("For testing purposes, we'll show you how the system would work...")
        return False
    
    try:
        # Import our matcher
        from edam_ontology_matcher import EDAMMatchingSystem
        
        print("🧪 Testing EDAM Ontology Matching System")
        print("=" * 50)
        
        # Initialize the system
        system = EDAMMatchingSystem('EDAM.csv')
        
        # Test with a simple example
        test_package = {
            'name': 'a4',
            'description': 'Automated Affymetrix Array Analysis Umbrella Package for comprehensive gene expression analysis including preprocessing, differential expression, and visualization tools.'
        }
        
        print(f"Test package: {test_package['name']}")
        print(f"Description: {test_package['description']}")
        print()
        
        # Get the match
        match = system.match_package_to_ontology(
            test_package['name'], 
            test_package['description']
        )
        
        print("🎯 Match Result:")
        print(f"   EDAM ID: {match.edam_id}")
        print(f"   EDAM Label: {match.edam_label}")
        print(f"   Confidence Score: {match.confidence_score:.2f}")
        print(f"   Reasoning: {match.reasoning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_edam_matcher()
    if success:
        print("\n✅ Test completed successfully!")
        print("You can now run the full system with: python edam_ontology_matcher.py")
    else:
        print("\n❌ Test failed. Please check the setup and try again.")
