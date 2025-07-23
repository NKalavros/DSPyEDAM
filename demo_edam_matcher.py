#!/usr/bin/env python3
"""
Demo script for the EDAM ontology matcher.
Shows system capabilities and example outputs without requiring API key.
"""

import json
import pandas as pd


def load_edam_data():
    """Load and preview EDAM ontology data."""
    try:
        df = pd.read_csv('EDAM.csv')
        active_terms = df[df['Obsolete'] == False]
        
        print(f"📊 EDAM Ontology Statistics:")
        print(f"   Total terms: {len(df):,}")
        print(f"   Active terms: {len(active_terms):,}")
        print(f"   Obsolete terms: {len(df) - len(active_terms):,}")
        
        # Show distribution by category
        categories = {}
        for _, row in active_terms.iterrows():
            class_id = row['Class ID']
            if 'topic_' in class_id:
                categories['Topics'] = categories.get('Topics', 0) + 1
            elif 'operation_' in class_id:
                categories['Operations'] = categories.get('Operations', 0) + 1
            elif 'data_' in class_id:
                categories['Data Types'] = categories.get('Data Types', 0) + 1
            elif 'format_' in class_id:
                categories['Formats'] = categories.get('Formats', 0) + 1
            else:
                categories['Other'] = categories.get('Other', 0) + 1
        
        print(f"\n📈 Category Distribution:")
        for category, count in categories.items():
            print(f"   {category}: {count:,}")
        
        return active_terms
        
    except FileNotFoundError:
        print("❌ EDAM.csv file not found!")
        return None


def show_example_terms():
    """Show example EDAM terms from different categories."""
    try:
        df = pd.read_csv('EDAM.csv')
        active_terms = df[df['Obsolete'] == False]
        
        print(f"\n🎯 Example EDAM Terms:")
        
        # Show examples from each category
        categories = [
            ('Topics', 'topic_'),
            ('Operations', 'operation_'), 
            ('Data Types', 'data_'),
            ('Formats', 'format_')
        ]
        
        for category_name, prefix in categories:
            category_terms = active_terms[
                active_terms['Class ID'].str.contains(prefix, na=False)
            ].head(3)
            
            print(f"\n   {category_name}:")
            for _, row in category_terms.iterrows():
                class_id = row['Class ID'].split('/')[-1]  # Get just the ID part
                label = row['Preferred Label']
                definition = row['Definitions'] if pd.notna(row['Definitions']) else "No definition"
                definition = definition[:100] + "..." if len(definition) > 100 else definition
                print(f"     • {class_id}: {label}")
                print(f"       {definition}")
        
    except Exception as e:
        print(f"Error loading examples: {e}")


def load_bioconductor_data():
    """Load and preview Bioconductor package data."""
    try:
        with open('bioc_packages_summary.json', 'r') as f:
            packages = json.load(f)
        
        print(f"\n📦 Bioconductor Package Data:")
        print(f"   Total packages: {len(packages)}")
        
        # Show examples
        print(f"\n📋 Example Packages:")
        for i, pkg in enumerate(packages[:3]):
            print(f"   {i+1}. {pkg.get('name', 'Unknown')}")
            desc = pkg.get('description', 'No description')
            desc = desc[:1000] + "..." if len(desc) > 1000 else desc
            print(f"      Description: {desc}")
            
            if 'downloaded_vignettes' in pkg:
                print(f"      Vignettes: {len(pkg['downloaded_vignettes'])} downloaded")
            print()
        
        return packages
        
    except FileNotFoundError:
        print("❌ bioc_packages_summary.json file not found!")
        print("   Please run parse_biocviews.py first to generate package data.")
        return None


def demonstrate_matching_logic():
    """Demonstrate the matching logic without calling the API."""
    
    print(f"\n🔍 Matching Algorithm Demo:")
    print(f"=" * 50)
    
    # Example package
    example = {
        'name': 'a4',
        'description': 'Automated Affymetrix Array Analysis Umbrella Package for comprehensive gene expression analysis including preprocessing, differential expression, and visualization tools.'
    }
    
    print(f"📦 Example Package: {example['name']}")
    print(f"📝 Description: {example['description']}")
    
    # Load EDAM terms and find relevant ones
    try:
        df = pd.read_csv('EDAM.csv')
        active_terms = df[df['Obsolete'] == False]
        
        print(f"\n🎯 Step 1: Keyword-based Candidate Selection")
        
        # Simple keyword matching simulation
        description_words = set(example['description'].lower().split())
        candidates = []
        
        for _, row in active_terms.head(100).iterrows():  # Sample first 100 for demo
            label = str(row['Preferred Label']).lower()
            definition = str(row['Definitions']).lower() if pd.notna(row['Definitions']) else ""
            synonyms = str(row['Synonyms']).lower() if pd.notna(row['Synonyms']) else ""
            
            term_words = set((label + " " + definition + " " + synonyms).split())
            overlap = len(description_words & term_words)
            
            if overlap >= 2:  # At least 2 word overlap
                candidates.append({
                    'id': row['Class ID'],
                    'label': row['Preferred Label'],
                    'definition': row['Definitions'] if pd.notna(row['Definitions']) else "",
                    'overlap': overlap
                })
        
        # Sort by overlap
        candidates.sort(key=lambda x: x['overlap'], reverse=True)
        
        print(f"   Found {len(candidates)} potential candidates")
        print(f"   Top 5 candidates by keyword overlap:")
        
        for i, candidate in enumerate(candidates[:5]):
            print(f"     {i+1}. {candidate['label']} (overlap: {candidate['overlap']})")
            print(f"        ID: {candidate['id']}")
            if candidate['definition']:
                def_preview = candidate['definition'][:80] + "..." if len(candidate['definition']) > 80 else candidate['definition']
                print(f"        Definition: {def_preview}")
            print()
        
        print(f"🤖 Step 2: LLM-based Selection (simulated)")
        print(f"   The system would use GPT-4o to:")
        print(f"   • Analyze semantic similarity between package and candidates")
        print(f"   • Consider context and domain knowledge") 
        print(f"   • Assign confidence scores based on match quality")
        print(f"   • Provide reasoning for the selection")
        
        # Simulate a realistic output
        if candidates:
            best_candidate = candidates[0]
            print(f"\n🎯 Simulated Output:")
            print(f"   EDAM ID: {best_candidate['id']}")
            print(f"   EDAM Label: {best_candidate['label']}")
            print(f"   Confidence Score: 0.85 (simulated)")
            print(f"   Reasoning: Package focuses on gene expression analysis and microarray")
            print(f"             data processing, which aligns well with the selected EDAM term.")
        
    except Exception as e:
        print(f"   Error in demo: {e}")


def show_expected_outputs():
    """Show examples of expected system outputs."""
    
    print(f"\n📋 Expected Output Format:")
    print(f"=" * 50)
    
    example_output = {
        "name": "a4",
        "description": "Automated Affymetrix Array Analysis Umbrella Package...",
        "url": "https://bioconductor.org/packages/a4",
        "vignettes": ["vignettes/a4/a4vignette.pdf"],
        "downloaded_vignettes": ["downloads/a4/a4vignette.pdf"],
        "processed_files": ["downloads/a4/a4vignette_extracted.txt"],
        "edam_match": {
            "edam_id": "http://edamontology.org/topic_0203",
            "edam_label": "Gene expression",
            "confidence_score": 0.85,
            "reasoning": "Package specializes in gene expression analysis using microarray data, which directly matches the gene expression topic in EDAM ontology."
        }
    }
    
    print(json.dumps(example_output, indent=2))
    
    print(f"\n📊 Confidence Score Ranges:")
    examples = [
        ("High confidence (≥0.8)", "Direct semantic match, clear domain alignment"),
        ("Medium confidence (0.5-0.8)", "Good match but broader categorization"),
        ("Low confidence (<0.5)", "Weak match, may need manual review")
    ]
    
    for range_desc, meaning in examples:
        print(f"   • {range_desc}: {meaning}")


def main():
    """Main demo function."""
    
    print("🧬 EDAM Ontology Matching System - Demo")
    print("=" * 60)
    print()
    
    # Load and show EDAM data
    edam_data = load_edam_data()
    if edam_data is not None:
        show_example_terms()
    
    # Load and show Bioconductor data  
    bioc_data = load_bioconductor_data()
    
    # Demonstrate matching process
    if edam_data is not None:
        demonstrate_matching_logic()
    
    # Show expected outputs
    show_expected_outputs()
    
    print(f"\n🚀 Next Steps:")
    print(f"   1. Set up OpenAI API key: export OPENAI_API_KEY='your-key'")
    print(f"   2. Run test: python test_edam_matcher.py")
    print(f"   3. Run full system: python edam_ontology_matcher.py")
    print(f"   4. Check results in: edam_matched_packages.json")


if __name__ == "__main__":
    main()
