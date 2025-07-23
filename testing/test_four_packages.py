#!/usr/bin/env python3
"""
Focused test script for EDAM ontology matching with 4 specific packages:
DESeq2, miloR, Rsubread, and GEOquery
"""

import json
import pandas as pd
import os


def create_test_packages():
    """Create test data for the 4 target packages."""
    
    test_packages = [
        {
            "name": "DESeq2",
            "description": "Differential gene expression analysis based on the negative binomial distribution. DESeq2 provides methods for testing differential expression by use of negative binomial generalized linear models; the estimates of dispersion and logarithmic fold changes incorporate data-driven prior distributions.",
            "url": "https://bioconductor.org/packages/DESeq2"
        },
        {
            "name": "miloR", 
            "description": "Milo performs single-cell differential abundance testing. Cell states are modelled as overlapping neighbourhoods on a KNN graph. Hypothesis testing is performed using a negative binomial generalized linear model.",
            "url": "https://bioconductor.org/packages/miloR"
        },
        {
            "name": "Rsubread",
            "description": "Tools for processing next-gen sequencing read data including read mapping (align reads to reference), read summarization (counting reads mapped to genomic features) and detection of mutations including SNPs and indels.",
            "url": "https://bioconductor.org/packages/Rsubread"
        },
        {
            "name": "GEOquery",
            "description": "The Gene Expression Omnibus (GEO) is a public repository of microarray data. Given the rich and varied nature of this resource, it is only natural to want to apply BioConductor tools to these data. GEOquery is the bridge between GEO and BioConductor.",
            "url": "https://bioconductor.org/packages/GEOquery"
        }
    ]
    
    return test_packages


def find_relevant_edam_terms(package_description, edam_df, top_k=10):
    """Find EDAM terms relevant to a package description."""
    
    description_words = set(package_description.lower().split())
    candidates = []
    
    for _, row in edam_df.iterrows():
        if row['Obsolete'] == True:
            continue
            
        label = str(row['Preferred Label']).lower()
        definition = str(row['Definitions']).lower() if pd.notna(row['Definitions']) else ""
        synonyms = str(row['Synonyms']).lower() if pd.notna(row['Synonyms']) else ""
        
        # Combine all text for searching
        term_text = label + " " + definition + " " + synonyms
        term_words = set(term_text.split())
        
        # Calculate relevance score
        overlap = len(description_words & term_words)
        if overlap >= 1:  # At least 1 word overlap
            # Bonus for specific keywords
            bonus = 0
            high_value_words = ['expression', 'differential', 'sequencing', 'analysis', 'gene', 'rna', 'mapping', 'alignment']
            for word in high_value_words:
                if word in description_words and word in term_words:
                    bonus += 2
            
            score = overlap + bonus
            
            candidates.append({
                'id': row['Class ID'],
                'label': row['Preferred Label'],
                'definition': row['Definitions'] if pd.notna(row['Definitions']) else "",
                'synonyms': row['Synonyms'] if pd.notna(row['Synonyms']) else "",
                'score': score,
                'category': get_edam_category(row['Class ID'])
            })
    
    # Sort by score and return top candidates
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:top_k]


def get_edam_category(class_id):
    """Determine EDAM category from class ID."""
    if 'topic_' in class_id:
        return 'Topic'
    elif 'operation_' in class_id:
        return 'Operation'
    elif 'data_' in class_id:
        return 'Data'
    elif 'format_' in class_id:
        return 'Format'
    else:
        return 'Other'


def simulate_expert_matching(package, candidates):
    """Simulate expert-level matching with reasoning."""
    
    # Define some expert rules for these specific packages
    expert_rules = {
        'DESeq2': {
            'keywords': ['differential', 'expression', 'gene', 'rna'],
            'preferred_categories': ['Topic', 'Operation'],
            'ideal_terms': ['gene expression', 'differential gene expression', 'rna-seq']
        },
        'miloR': {
            'keywords': ['single-cell', 'differential', 'abundance', 'cell'],
            'preferred_categories': ['Topic', 'Operation'],
            'ideal_terms': ['single cell', 'differential expression', 'cell biology']
        },
        'Rsubread': {
            'keywords': ['mapping', 'alignment', 'sequencing', 'reads'],
            'preferred_categories': ['Operation'],
            'ideal_terms': ['sequence alignment', 'read mapping', 'sequence analysis']
        },
        'GEOquery': {
            'keywords': ['microarray', 'database', 'repository', 'query'],
            'preferred_categories': ['Operation', 'Data'],
            'ideal_terms': ['database', 'query', 'microarray', 'gene expression']
        }
    }
    
    package_name = package['name']
    rules = expert_rules.get(package_name, {})
    
    # Score candidates based on expert knowledge
    for candidate in candidates:
        expert_score = candidate['score']
        
        # Bonus for preferred categories
        if candidate['category'] in rules.get('preferred_categories', []):
            expert_score += 5
        
        # Bonus for ideal terms
        label_lower = candidate['label'].lower()
        for ideal_term in rules.get('ideal_terms', []):
            if ideal_term in label_lower:
                expert_score += 10
        
        candidate['expert_score'] = expert_score
    
    # Sort by expert score
    candidates.sort(key=lambda x: x['expert_score'], reverse=True)
    
    # Select best match and generate confidence
    if candidates:
        best_match = candidates[0]
        
        # Calculate confidence based on score and match quality
        max_possible_score = 20  # Rough estimate
        confidence = min(0.95, best_match['expert_score'] / max_possible_score)
        confidence = max(0.3, confidence)  # Minimum confidence
        
        # Generate reasoning
        reasoning_parts = []
        if package_name in expert_rules:
            if best_match['category'] in expert_rules[package_name].get('preferred_categories', []):
                reasoning_parts.append(f"Matches expected {best_match['category'].lower()} category")
        
        label_lower = best_match['label'].lower()
        matched_concepts = []
        for keyword in rules.get('keywords', []):
            if keyword in label_lower or keyword in best_match['definition'].lower():
                matched_concepts.append(keyword)
        
        if matched_concepts:
            reasoning_parts.append(f"Contains relevant concepts: {', '.join(matched_concepts[:3])}")
        
        if not reasoning_parts:
            reasoning_parts.append("General semantic similarity with package functionality")
        
        reasoning = ". ".join(reasoning_parts) + "."
        
        return {
            'edam_id': best_match['id'],
            'edam_label': best_match['label'],
            'confidence_score': round(confidence, 2),
            'reasoning': reasoning,
            'category': best_match['category']
        }
    
    return None


def test_four_packages():
    """Test the matching system with the 4 target packages."""
    
    print("🧬 EDAM Ontology Matching - Focused Test")
    print("=" * 50)
    print("Testing packages: DESeq2, miloR, Rsubread, GEOquery")
    print()
    
    # Load EDAM data
    try:
        edam_df = pd.read_csv('EDAM.csv')
        print(f"📊 Loaded {len(edam_df)} EDAM terms ({len(edam_df[edam_df['Obsolete'] == False])} active)")
    except FileNotFoundError:
        print("❌ EDAM.csv file not found!")
        return
    
    # Get test packages
    test_packages = create_test_packages()
    
    results = []
    
    for i, package in enumerate(test_packages):
        print(f"\n📦 Package {i+1}: {package['name']}")
        print(f"Description: {package['description'][:100]}...")
        
        # Find relevant EDAM terms
        candidates = find_relevant_edam_terms(package['description'], edam_df, top_k=10)
        
        print(f"\n🔍 Top candidate EDAM terms:")
        for j, candidate in enumerate(candidates[:5]):
            print(f"   {j+1}. {candidate['label']} ({candidate['category']})")
            print(f"      Score: {candidate['score']}, ID: {candidate['id'].split('/')[-1]}")
            if candidate['definition']:
                def_preview = candidate['definition'][:60] + "..." if len(candidate['definition']) > 60 else candidate['definition']
                print(f"      Definition: {def_preview}")
        
        # Simulate expert matching
        match = simulate_expert_matching(package, candidates)
        
        if match:
            print(f"\n🎯 Best Match:")
            print(f"   EDAM ID: {match['edam_id']}")
            print(f"   EDAM Label: {match['edam_label']}")
            print(f"   Category: {match['category']}")
            print(f"   Confidence: {match['confidence_score']}")
            print(f"   Reasoning: {match['reasoning']}")
            
            # Add to results
            result = package.copy()
            result['edam_match'] = match
            results.append(result)
        else:
            print("   ❌ No suitable match found")
        
        print("-" * 50)
    
    # Save results
    output_file = 'test_edam_matches.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Test Complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Successfully matched {len(results)}/{len(test_packages)} packages")
    
    # Summary statistics
    if results:
        confidences = [r['edam_match']['confidence_score'] for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        high_confidence = sum(1 for c in confidences if c >= 0.8)
        
        print(f"\n📈 Summary Statistics:")
        print(f"   Average confidence: {avg_confidence:.2f}")
        print(f"   High confidence matches (≥0.8): {high_confidence}/{len(results)}")
        
        print(f"\n🎯 Quick Results:")
        for result in results:
            match = result['edam_match']
            print(f"   {result['name']} -> {match['edam_label']} ({match['confidence_score']})")


def show_dspy_integration():
    """Show how this would integrate with the DSPy system."""
    
    print(f"\n🤖 DSPy Integration Preview:")
    print("=" * 50)
    
    print("The actual DSPy system would:")
    print("1. 🔄 Use structured prompts with GPT-4o for semantic analysis")
    print("2. 📋 Apply consistent output formatting with Pydantic models")
    print("3. 🎯 Leverage chain-of-thought reasoning for better explanations")
    print("4. 🔧 Allow optimization with DSPy optimizers for improved accuracy")
    print("5. 📊 Provide consistent confidence scoring across all packages")
    
    print(f"\nTo run with DSPy + OpenAI API:")
    print("1. Set API key: export OPENAI_API_KEY='your-key'")
    print("2. Run: python edam_ontology_matcher.py")
    print("3. The system will process all packages with LLM-powered matching")


if __name__ == "__main__":
    test_four_packages()
    show_dspy_integration()
