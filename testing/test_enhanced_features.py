#!/usr/bin/env python3

"""
Test script for the Enhanced EDAM Ontology Matching System.
Tests the three new features:
1. Pure Python validator for EDAM ID/Label existence
2. Batch processing with small batches for testing
3. DSPy module for suggesting new designations when confidence < 0.5
"""

import os
import sys
import json
from typing import Dict, Any, List

# Add current directory to path to import our module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_edam_matcher import EnhancedEDAMMatchingSystem, EDAMValidator, OntologyMatch, NewDesignationSuggestion

def test_validator():
    """Test the pure Python EDAM validator."""
    print("🧪 Testing EDAM Validator")
    print("-" * 40)
    
    # Initialize validator
    validator = EDAMValidator('EDAM.csv')
    
    # Test valid ID and label
    valid_id = "http://edamontology.org/topic_0080"
    valid_label = "Sequence analysis"
    
    print(f"Testing valid ID: {valid_id}")
    print(f"ID exists: {validator.validate_id(valid_id)}")
    
    print(f"Testing valid label: {valid_label}")
    print(f"Label exists: {validator.validate_label(valid_label)}")
    
    # Test validation of matching pair
    is_valid, msg = validator.validate_match(valid_id, valid_label)
    print(f"ID-Label pair validation: {is_valid} - {msg}")
    
    # Test invalid cases
    invalid_id = "http://edamontology.org/topic_9999"
    print(f"\nTesting invalid ID: {invalid_id}")
    print(f"ID exists: {validator.validate_id(invalid_id)}")
    
    # Test mismatched pair
    mismatched_label = "Some Random Label"
    is_valid, msg = validator.validate_match(valid_id, mismatched_label)
    print(f"Mismatched pair validation: {is_valid} - {msg}")
    
    # Test fix functionality
    print(f"\nTesting fix functionality:")
    corrected_id, corrected_label = validator.fix_match(valid_id, mismatched_label)
    print(f"Fixed: {corrected_id} -> {corrected_label}")
    
    print("✅ Validator test complete\n")

def test_batch_processing():
    """Test batch processing functionality."""
    print("🧪 Testing Batch Processing")
    print("-" * 40)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping batch processing test - no OpenAI API key")
        return
    
    # Create test data with 12 packages to test batching
    test_packages = [
        {
            "name": f"TestPackage{i}",
            "description": f"This is a test package {i} that does sequence analysis and data processing. It provides tools for genomic data analysis and bioinformatics workflows."
        }
        for i in range(1, 13)  # 12 packages
    ]
    
    # Add our 4 real test packages
    real_packages = [
        {
            "name": "DESeq2",
            "description": "Estimate variance-mean dependence in count data from high-throughput sequencing assays and test for differential expression based on a model using the negative binomial distribution."
        },
        {
            "name": "miloR", 
            "description": "Milo performs single-cell differential abundance testing. Cell states are modelled as representative neighbourhoods on a nearest neighbour graph."
        }
    ]
    
    all_test_packages = test_packages + real_packages
    
    print(f"Created {len(all_test_packages)} test packages")
    
    # Initialize system with small batch size for testing
    system = EnhancedEDAMMatchingSystem('EDAM.csv', batch_size=5)
    
    print(f"Processing with batch size: {system.batch_size}")
    
    # Process in batches
    results = system.process_packages_in_batches(all_test_packages, confidence_threshold=0.5)
    
    print(f"✅ Processed {len(results)} packages in batches")
    
    # Save test results
    with open('batch_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("📁 Batch test results saved to batch_test_results.json")
    print("✅ Batch processing test complete\n")

def test_low_confidence_suggestions():
    """Test low confidence suggestion functionality."""
    print("🧪 Testing Low Confidence Suggestions")
    print("-" * 40)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping low confidence test - no OpenAI API key")
        return
    
    # Initialize system
    system = EnhancedEDAMMatchingSystem('EDAM.csv')
    
    # Create a package that should have low confidence
    unusual_package = {
        "name": "QuantumBioAnalyzer",
        "description": "A revolutionary quantum computing approach to analyze interdimensional protein folding patterns using advanced alien algorithms from the future. This package implements time-travel based sequence alignment."
    }
    
    print(f"Testing unusual package: {unusual_package['name']}")
    print(f"Description: {unusual_package['description']}")
    
    # Process this package
    match = system.match_package_to_ontology(
        unusual_package['name'],
        unusual_package['description'],
        confidence_threshold=0.5
    )
    
    print(f"\n📊 Match result:")
    print(f"   EDAM ID: {match.edam_id}")
    print(f"   EDAM Label: {match.edam_label}")
    print(f"   Confidence: {match.confidence_score:.3f}")
    print(f"   Validated: {match.validated}")
    print(f"   Reasoning: {match.reasoning}")
    
    # Check if new designation was suggested (should be in reasoning)
    if "NEW DESIGNATION SUGGESTED" in match.reasoning:
        print("✅ New designation suggestion triggered!")
    else:
        print("⚠️  New designation suggestion may not have triggered")
    
    print("✅ Low confidence suggestion test complete\n")

def test_comprehensive_system():
    """Test the complete enhanced system with real packages."""
    print("🧪 Testing Complete Enhanced System")
    print("-" * 40)
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping comprehensive test - no OpenAI API key")
        return
    
    # Initialize system
    system = EnhancedEDAMMatchingSystem('EDAM.csv', batch_size=2)  # Small batches for testing
    
    # Test the 4 specific packages
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
    
    print(f"Testing {len(test_packages)} packages with all enhanced features:")
    
    results = system.process_packages_in_batches(test_packages, confidence_threshold=0.5)
    
    # Analyze results
    validated_count = 0
    high_conf_count = 0
    low_conf_count = 0
    
    for result in results:
        match = result.get('edam_match', {})
        if match.get('validated', False):
            validated_count += 1
        if match.get('confidence_score', 0) >= 0.8:
            high_conf_count += 1
        elif match.get('confidence_score', 0) < 0.5:
            low_conf_count += 1
    
    print(f"\n📊 Enhanced System Results:")
    print(f"   Total packages: {len(results)}")
    print(f"   Validated matches: {validated_count}/{len(results)}")
    print(f"   High confidence (≥0.8): {high_conf_count}")
    print(f"   Low confidence (<0.5): {low_conf_count}")
    
    # Save results
    with open('comprehensive_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("📁 Results saved to comprehensive_test_results.json")
    print("✅ Comprehensive system test complete\n")

def main():
    """Run all tests for the enhanced EDAM matching system."""
    
    print("🚀 Testing Enhanced EDAM Ontology Matching System")
    print("=" * 60)
    print("🔧 Features: Validation + Batch Processing + Low Confidence Handling")
    print("=" * 60)
    
    # Check for required files
    if not os.path.exists('EDAM.csv'):
        print("❌ Error: EDAM.csv file not found!")
        return
    
    # Test 1: Validator (no API key needed)
    test_validator()
    
    # Test 2: Batch processing (needs API key)
    test_batch_processing()
    
    # Test 3: Low confidence suggestions (needs API key)
    test_low_confidence_suggestions()
    
    # Test 4: Complete system (needs API key)
    test_comprehensive_system()
    
    print("🎉 All enhanced feature tests completed!")
    print("\n📈 Summary of New Features:")
    print("   ✅ Pure Python EDAM Validator")
    print("   ✅ Batch Processing (5000 entries per batch)")
    print("   ✅ Low Confidence Suggestion System")
    print("   ✅ Enhanced validation and error handling")

if __name__ == "__main__":
    main()
