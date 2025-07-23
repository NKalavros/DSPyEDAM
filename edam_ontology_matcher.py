#!/usr/bin/env python3
"""
DSPy-based EDAM Ontology Matching System

This script uses DSPy (Declarative Self-improving Python) to match Bioconductor 
package descriptions to EDAM ontology terms with structured output including 
confidence scores.

Requirements:
- dspy (pip install dspy)
- pandas (pip install pandas) 
- openai API key set as environment variable OPENAI_API_KEY
"""

import os
import json
import pandas as pd
import dspy
from typing import List, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


class OntologyMatch(BaseModel):
    """Structured output for ontology matching."""
    edam_id: str = Field(description="EDAM ontology ID (e.g., 'http://edamontology.org/topic_0080')")
    edam_label: str = Field(description="EDAM preferred label (e.g., 'Sequence analysis')")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0, where 1.0 is perfect match")
    reasoning: str = Field(description="Brief explanation of why this ontology term was selected")


class EDAMOntologyMatcher(dspy.Signature):
    """
    Match a Bioconductor package description to the most relevant EDAM ontology term.
    
    Given a package description and a set of potential EDAM terms, identify the best match
    and provide a confidence score with reasoning.
    """
    
    package_name: str = dspy.InputField(desc="Name of the Bioconductor package")
    package_description: str = dspy.InputField(desc="Description of the Bioconductor package functionality") 
    candidate_terms: str = dspy.InputField(desc="Relevant EDAM ontology terms with descriptions")
    
    edam_id: str = dspy.OutputField(desc="The EDAM ontology ID (e.g., 'http://edamontology.org/topic_0080')")
    edam_label: str = dspy.OutputField(desc="The EDAM preferred label (e.g., 'Sequence analysis')")
    confidence_score: float = dspy.OutputField(desc="Confidence score between 0.0 and 1.0, where 1.0 is perfect match")
    reasoning: str = dspy.OutputField(desc="Brief explanation of why this ontology term was selected")


class EDAMMatchingSystem:
    """Main system for matching packages to EDAM ontology terms."""
    
    def __init__(self, edam_csv_path: str, openai_api_key: str | None = None):
        """
        Initialize the EDAM matching system.
        
        Args:
            edam_csv_path: Path to the EDAM.csv file
            openai_api_key: OpenAI API key (or will use OPENAI_API_KEY env var)
        """
        # Set up DSPy with OpenAI
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
        
        # Configure DSPy with GPT-4o
        lm = dspy.LM("openai/gpt-4o", api_key=os.getenv('OPENAI_API_KEY'))
        dspy.configure(lm=lm)
        
        # Load EDAM ontology data
        self.edam_df = pd.read_csv(edam_csv_path)
        
        # Filter to non-obsolete terms only
        self.edam_df = self.edam_df[self.edam_df['Obsolete'] == False].copy()
        
        # Initialize the DSPy module
        self.matcher = dspy.ChainOfThought(EDAMOntologyMatcher)
        
        print(f"Loaded {len(self.edam_df)} active EDAM terms")
    
    def preprocess_edam_terms(self, top_k: int = 20) -> Dict[str, str]:
        """
        Preprocess EDAM terms for efficient matching.
        
        Args:
            top_k: Number of top candidate terms to consider
            
        Returns:
            Dictionary mapping EDAM IDs to formatted descriptions
        """
        candidates = {}
        
        # Get a diverse selection of terms across categories
        for category in ['topic_', 'operation_', 'data_']:
            category_terms = self.edam_df[
                self.edam_df['Class ID'].str.contains(category, na=False)
            ].head(top_k // 3)
            
            for _, row in category_terms.iterrows():
                edam_id = row['Class ID']
                label = row['Preferred Label']
                definition = row['Definitions'] if pd.notna(row['Definitions']) else ""
                synonyms = row['Synonyms'] if pd.notna(row['Synonyms']) else ""
                
                # Format the term description
                description = f"{label}"
                if definition:
                    description += f": {definition}"
                if synonyms:
                    description += f" (Synonyms: {synonyms})"
                
                candidates[edam_id] = description
                
        return candidates
    
    def search_relevant_terms(self, package_description: str, top_k: int = 10) -> Dict[str, str]:
        """
        Search for EDAM terms relevant to the package description using text similarity.
        
        Args:
            package_description: Description of the package
            top_k: Number of top terms to return
            
        Returns:
            Dictionary of relevant EDAM terms
        """
        # Simple keyword-based relevance scoring
        description_lower = package_description.lower()
        
        relevant_terms = {}
        
        for _, row in self.edam_df.iterrows():
            edam_id = row['Class ID']
            label = row['Preferred Label']
            definition = row['Definitions'] if pd.notna(row['Definitions']) else ""
            synonyms = row['Synonyms'] if pd.notna(row['Synonyms']) else ""
            
            # Calculate relevance score based on keyword overlap
            score = 0
            text_to_search = f"{label} {definition} {synonyms}".lower()
            
            # Simple scoring based on word overlap
            description_words = set(description_lower.split())
            term_words = set(text_to_search.split())
            
            overlap = len(description_words & term_words)
            if overlap > 0:
                score = overlap / len(description_words | term_words)
                
                # Format the term description
                formatted_desc = f"{label}"
                if definition:
                    formatted_desc += f": {definition}"
                if synonyms:
                    formatted_desc += f" (Synonyms: {synonyms})"
                
                relevant_terms[edam_id] = {
                    'description': formatted_desc,
                    'score': score
                }
        
        # Sort by relevance score and take top_k
        sorted_terms = sorted(relevant_terms.items(), key=lambda x: x[1]['score'], reverse=True)[:top_k]
        
        return {edam_id: data['description'] for edam_id, data in sorted_terms}
    
    def match_package_to_ontology(self, package_name: str, package_description: str) -> OntologyMatch:
        """
        Match a single package to the best EDAM ontology term.
        
        Args:
            package_name: Name of the package
            package_description: Description of the package
            
        Returns:
            OntologyMatch with the best matching term
        """
        # Find relevant candidate terms
        candidates = self.search_relevant_terms(package_description, top_k=10)
        
        if not candidates:
            # Fallback to general terms if no specific matches found
            candidates = self.preprocess_edam_terms(top_k=10)
        
        # Format candidates for the LLM
        candidate_text = ""
        for edam_id, description in candidates.items():
            candidate_text += f"- {edam_id}: {description}\n"
        
        # Use DSPy to find the best match
        try:
            result = self.matcher(
                package_name=package_name,
                package_description=package_description,
                candidate_terms=candidate_text
            )
            
            # Parse the DSPy output into our structured format
            return OntologyMatch(
                edam_id=result.edam_id,
                edam_label=result.edam_label,
                confidence_score=float(result.confidence_score),
                reasoning=result.reasoning
            )
            
        except Exception as e:
            print(f"Error matching {package_name}: {e}")
            # Fallback to first candidate
            if candidates:
                first_id = list(candidates.keys())[0]
                first_desc = candidates[first_id]
                label = first_desc.split(':')[0] if ':' in first_desc else first_desc
                return OntologyMatch(
                    edam_id=first_id,
                    edam_label=label,
                    confidence_score=0.5,
                    reasoning=f"DSPy failed, using top candidate: {str(e)}"
                )
            else:
                return OntologyMatch(
                    edam_id="http://edamontology.org/topic_3365",
                    edam_label="Data architecture, analysis and design", 
                    confidence_score=0.3,
                    reasoning=f"DSPy failed and no candidates found: {str(e)}"
                )
    
    def process_bioconductor_packages(self, packages_json_path: str) -> List[Dict[str, Any]]:
        """
        Process multiple Bioconductor packages and match them to EDAM terms.
        
        Args:
            packages_json_path: Path to the bioc_packages_summary.json file
            
        Returns:
            List of packages with their EDAM matches
        """
        # Load the package data
        with open(packages_json_path, 'r') as f:
            packages = json.load(f)
        
        results = []
        
        for i, package in enumerate(packages):
            if 'name' not in package or 'description' not in package:
                continue
                
            print(f"Processing package {i+1}/{len(packages)}: {package['name']}")
            
            # Match to EDAM ontology
            match = self.match_package_to_ontology(
                package['name'], 
                package['description']
            )
            
            # Add the match to the package data
            package_result = package.copy()
            package_result['edam_match'] = {
                'edam_id': match.edam_id,
                'edam_label': match.edam_label,
                'confidence_score': match.confidence_score,
                'reasoning': match.reasoning
            }
            
            results.append(package_result)
            
            print(f"  -> Matched to: {match.edam_label} (confidence: {match.confidence_score:.2f})")
            print(f"     Reasoning: {match.reasoning}")
            print()
        
        return results


def main():
    """Main function to run the EDAM matching system."""
    
    # Check for required files
    if not os.path.exists('EDAM.csv'):
        print("Error: EDAM.csv file not found!")
        return
    
    if not os.path.exists('bioc_packages_summary.json'):
        print("Error: bioc_packages_summary.json file not found!")
        print("Please run the parse_biocviews.py script first.")
        return
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("🚀 Starting EDAM Ontology Matching System")
    print("=" * 50)
    
    # Initialize the system
    system = EDAMMatchingSystem('EDAM.csv')
    
    # Process the packages
    print("Processing Bioconductor packages...")
    results = system.process_bioconductor_packages('bioc_packages_summary.json')
    
    # Save results
    output_file = 'edam_matched_packages.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Processing complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"📊 Processed {len(results)} packages")
    
    # Print summary statistics
    high_confidence = sum(1 for r in results if r.get('edam_match', {}).get('confidence_score', 0) >= 0.8)
    medium_confidence = sum(1 for r in results if 0.5 <= r.get('edam_match', {}).get('confidence_score', 0) < 0.8)
    low_confidence = sum(1 for r in results if r.get('edam_match', {}).get('confidence_score', 0) < 0.5)
    
    print(f"\n📈 Confidence Score Distribution:")
    print(f"   High confidence (≥0.8): {high_confidence}")
    print(f"   Medium confidence (0.5-0.8): {medium_confidence}")
    print(f"   Low confidence (<0.5): {low_confidence}")
    
    # Show some example matches
    print(f"\n🎯 Example Matches:")
    for i, result in enumerate(results[:3]):
        if 'edam_match' in result:
            match = result['edam_match']
            print(f"   {i+1}. {result['name']}")
            print(f"      -> {match['edam_label']} (confidence: {match['confidence_score']:.2f})")
            print(f"         {match['reasoning']}")
            print()


if __name__ == "__main__":
    main()
