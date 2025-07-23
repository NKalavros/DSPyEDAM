#!/usr/bin/env python3
"""
Enhanced EDAM Ontology Matching System with Validation, Batch Processing, and Low Confidence Handling

New Features:
1. Pure Python validator for EDAM ID/Label existence
2. Batch processing with 5000 entries at a time
3. DSPy module for suggesting new designations when confidence < 0.5

Requirements:
- dspy (pip install dspy)
- pandas (pip install pandas) 
- openai API key set as environment variable OPENAI_API_KEY
"""

import os
import json
import pandas as pd
import dspy
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from pydantic import BaseModel, Field
import math
from pathlib import Path


class OntologyMatch(BaseModel):
    """Structured output for ontology matching."""
    edam_id: str = Field(description="EDAM ontology ID (e.g., 'http://edamontology.org/topic_0080')")
    edam_label: str = Field(description="EDAM preferred label (e.g., 'Sequence analysis')")
    confidence_score: float = Field(description="Confidence score between 0.0 and 1.0, where 1.0 is perfect match")
    reasoning: str = Field(description="Brief explanation of why this ontology term was selected")
    validated: bool = Field(description="Whether the EDAM ID and label were validated against the CSV", default=False)


class NewDesignationSuggestion(BaseModel):
    """Structured output for new EDAM designation suggestions."""
    suggested_label: str = Field(description="Suggested new EDAM term label")
    suggested_category: str = Field(description="Suggested EDAM category (topic, operation, data, format)")
    justification: str = Field(description="Justification for why this new term is needed")
    similar_terms: List[str] = Field(description="List of existing similar EDAM terms for reference")
    confidence_score: float = Field(description="Confidence in the suggestion (0.0-1.0)")


class EDAMValidator:
    """Pure Python validator for EDAM terms, with optional synonym support."""
    def __init__(self, edam_csv_path: str, use_synonyms: bool = True):
        """Initialize validator with EDAM CSV data, optionally including synonyms."""
        self.edam_df = pd.read_csv(edam_csv_path)

        # Create lookup sets for fast validation
        self.valid_ids: Set[str] = set(self.edam_df['Class ID'].dropna())
        self.valid_labels: Set[str] = set(self.edam_df['Preferred Label'].dropna())

        # Create mapping from ID to label and vice versa
        self.id_to_label: Dict[str, str] = {}
        self.label_to_id: Dict[str, str] = {}

        self.use_synonyms = use_synonyms
        self.synonym_to_label: Dict[str, str] = {}
        self.synonym_to_id: Dict[str, str] = {}

        for _, row in self.edam_df.iterrows():
            if pd.notna(row['Class ID']) and pd.notna(row['Preferred Label']):
                class_id = row['Class ID']
                label = row['Preferred Label']
                self.id_to_label[class_id] = label
                self.label_to_id[label] = class_id
                if self.use_synonyms:
                    # Index synonyms (pipe-separated)
                    if 'Synonyms' in row and pd.notna(row['Synonyms']):
                        for synonym in str(row['Synonyms']).split('|'):
                            synonym = synonym.strip()
                            if synonym:
                                self.synonym_to_label[synonym] = label
                                self.synonym_to_id[synonym] = class_id

        print(f"✅ EDAM Validator initialized with {len(self.valid_ids)} valid IDs and {len(self.valid_labels)} valid labels, {len(self.synonym_to_label) if self.use_synonyms else 0} synonyms indexed (use_synonyms={self.use_synonyms})")
        if not self.use_synonyms:
            print("[DEBUG] Synonym support is OFF. Only preferred labels will be used for matching.")
    def get_label_for_synonym(self, synonym: str) -> str | None:
        if not self.use_synonyms:
            return None
        return self.synonym_to_label.get(synonym)

    def get_id_for_synonym(self, synonym: str) -> str | None:
        if not self.use_synonyms:
            return None
        return self.synonym_to_id.get(synonym)

    def normalize_label_and_id(self, label_or_synonym: str) -> tuple[str | None, str | None]:
        if label_or_synonym in self.label_to_id:
            return label_or_synonym, self.label_to_id[label_or_synonym]
        if self.use_synonyms and label_or_synonym in self.synonym_to_label:
            label = self.synonym_to_label[label_or_synonym]
            class_id = self.synonym_to_id[label_or_synonym]
            return label, class_id
        return None, None
    
    def validate_id(self, edam_id: str) -> bool:
        """Check if EDAM ID exists in CSV."""
        return edam_id in self.valid_ids
    
    def validate_label(self, edam_label: str) -> bool:
        if self.use_synonyms:
            return edam_label in self.valid_labels or edam_label in self.synonym_to_label
        else:
            return edam_label in self.valid_labels
    
    def validate_match(self, edam_id: str, edam_label: str) -> Tuple[bool, str]:
        """
        Validate that ID and label exist and match each other.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if ID exists
        if not self.validate_id(edam_id):
            return False, f"EDAM ID '{edam_id}' not found in CSV"
        
        # Check if label exists
        if not self.validate_label(edam_label):
            return False, f"EDAM label '{edam_label}' not found in CSV"
        
        # Check if ID and label match (allow for synonym normalization)
        expected_label = self.id_to_label.get(edam_id)
        if expected_label == edam_label:
            return True, "Valid match"
        if self.use_synonyms and edam_label in self.synonym_to_label:
            if self.synonym_to_id[edam_label] == edam_id:
                return True, "Valid match (via synonym)"
            else:
                return False, f"Label '{edam_label}' is a synonym for '{self.synonym_to_label[edam_label]}' (ID: {self.synonym_to_id[edam_label]}), not for '{expected_label}'"
        return False, f"ID '{edam_id}' should have label '{expected_label}', not '{edam_label}'"
    
    def get_label_for_id(self, edam_id: str) -> Optional[str]:
        """Get the correct label for a given EDAM ID."""
        return self.id_to_label.get(edam_id)
    
    def get_id_for_label(self, edam_label: str) -> Optional[str]:
        """Get the correct ID for a given EDAM label."""
        return self.label_to_id.get(edam_label)
    
    def fix_match(self, edam_id: str, edam_label: str) -> Tuple[str, str]:
        """
        Try to fix a mismatched ID/label pair.
        
        Returns:
            Tuple of (corrected_id, corrected_label)
        """
        # If ID is valid but label is wrong, use correct label for ID
        if self.validate_id(edam_id):
            correct_label = self.get_label_for_id(edam_id)
            if correct_label:
                return edam_id, correct_label
        
        # If label is valid but ID is wrong, use correct ID for label
        if self.validate_label(edam_label):
            correct_id = self.get_id_for_label(edam_label)
            if correct_id:
                return correct_id, edam_label
        
        # If neither is valid, return as-is (will be handled elsewhere)
        return edam_id, edam_label


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


class NewDesignationSuggester(dspy.Signature):
    """
    Suggest a new EDAM designation for packages that don't match well with existing terms.
    
    When confidence is low (<0.5), suggest what new EDAM term should be created.
    """
    
    package_name: str = dspy.InputField(desc="Name of the Bioconductor package")
    package_description: str = dspy.InputField(desc="Description of the Bioconductor package functionality")
    low_confidence_match: str = dspy.InputField(desc="The best existing match that had low confidence")
    existing_terms_sample: str = dspy.InputField(desc="Sample of existing EDAM terms for context")
    
    suggested_label: str = dspy.OutputField(desc="Suggested label for a new EDAM term")
    suggested_category: str = dspy.OutputField(desc="Suggested EDAM category: topic, operation, data, or format")
    justification: str = dspy.OutputField(desc="Detailed justification for why this new term is needed")
    similar_terms: str = dspy.OutputField(desc="Comma-separated list of existing similar EDAM terms")
    confidence_score: float = dspy.OutputField(desc="Confidence in this suggestion (0.0-1.0)")


class EnhancedEDAMMatchingSystem:
    """Enhanced EDAM matching system with validation, batch processing, and low confidence handling."""
    
    def __init__(self, edam_csv_path: str, openai_api_key: str | None = None, batch_size: int = 5000, use_synonyms: bool = False, simple_mode: bool = True):
        """
        Initialize the enhanced EDAM matching system.
        
        Args:
            edam_csv_path: Path to the EDAM.csv file
            openai_api_key: OpenAI API key (or will use OPENAI_API_KEY env var)
            batch_size: Number of packages to process in each batch
        """
        self.simple_mode = simple_mode
        # Set up DSPy with OpenAI
        if openai_api_key:
            os.environ['OPENAI_API_KEY'] = openai_api_key
        api_key = os.getenv('OPENAI_API_KEY', '')
        org = os.getenv('OPENAI_ORG_ID', '')
        print(f"[DEBUG] Using OpenAI API key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
        if org:
            print(f"[DEBUG] Using OpenAI Org: {org}")
        # Use a model that supports response_format (structured output)
        lm = dspy.LM("gpt-4o", api_key=api_key)
        dspy.configure(lm=lm)
        
        # Initialize validator
        self.validator = EDAMValidator(edam_csv_path, use_synonyms=use_synonyms)
        
        # Load EDAM ontology data
        self.edam_df = pd.read_csv(edam_csv_path)
        
        # Filter to non-obsolete terms only
        self.edam_df = self.edam_df[self.edam_df['Obsolete'] == False].copy()
        
        # Set batch size
        self.batch_size = batch_size
        
        # Initialize the DSPy modules
        self.matcher = dspy.ChainOfThought(EDAMOntologyMatcher)
        self.suggester = dspy.ChainOfThought(NewDesignationSuggester)
        
        print(f"✅ Enhanced EDAM System initialized with {len(self.edam_df)} active terms")
        print(f"📦 Batch size set to {self.batch_size} packages per batch")
        print(f"[DEBUG] use_synonyms={use_synonyms}")
    
    def search_relevant_terms(self, description: str, top_k: int = 10) -> Dict[str, str]:
        """
        Find EDAM terms relevant to a package description using keyword matching, including synonyms.
        Args:
            description: Package description
            top_k: Number of top candidates to return
        Returns:
            Dictionary mapping EDAM IDs to formatted descriptions
        """
        description_lower = description.lower()
        relevant_terms = {}
        description_words = set(description_lower.split())

        for _, row in self.edam_df.iterrows():
            edam_id = row['Class ID']
            label = row['Preferred Label'] if pd.notna(row['Preferred Label']) else ""
            definition = row['Definitions'] if pd.notna(row['Definitions']) else ""
            synonyms = row['Synonyms'] if pd.notna(row['Synonyms']) else ""

            # Build a set of all words from label, definition, and synonyms
            text_to_search = f"{label} {definition} {synonyms}".lower()
            term_words = set(text_to_search.split())

            # Also consider each synonym as a separate candidate for overlap
            all_synonyms = [s.strip() for s in synonyms.split('|') if s.strip()] if synonyms else []
            max_overlap = len(description_words & term_words)

            # Check overlap for each synonym individually
            for syn in all_synonyms:
                syn_words = set(syn.lower().split())
                overlap = len(description_words & syn_words)
                if overlap > max_overlap:
                    max_overlap = overlap

            if max_overlap > 0:
                relevant_terms[edam_id] = f"{label}: {definition}" if definition else label

        # Return top_k by overlap (not sorted here, but could be improved)
        if relevant_terms:
            return dict(list(relevant_terms.items())[:top_k])
        return {}


    def match_package_to_ontology(self, package_name: str, package_description: str, confidence_threshold: float = 0.5, simple_mode: Optional[bool] = None) -> Dict[str, Any]:
        if simple_mode is None:
            simple_mode = self.simple_mode
        """
        Match a package to the most relevant EDAM ontology term with retry logic and validation.
        Returns a dictionary with match details.
        """
        import time
        max_retries = 3
        # Chunk ontology to avoid token/context overflow
        # Token/char limits
        MAX_TOKENS = 30000
        SAFE_TOKENS = 25000  # Stay well below limit
        CHARS_PER_TOKEN = 4  # Approximate
        MAX_ONTOLOGY_CHARS = SAFE_TOKENS * CHARS_PER_TOKEN
        vignette_chars = len(package_description)
        vignette_words = len(package_description.split())
        vignette_tokens = vignette_chars // 4
        # Prepare all ontology entries as strings (label and description only)
        if simple_mode:
            # Use only preferred labels for simple mode
            ontology_entries = [
                f"{row['Preferred Label']}" for _, row in self.edam_df.iterrows()
            ]
        else:
            ontology_entries = [
                f"{row['Preferred Label']}: {row['Definitions'] if pd.notna(row['Definitions']) else ''}"
                for _, row in self.edam_df.iterrows()
            ]
        print(f"[DEBUG] Number of ontology entries (label+desc only): {len(ontology_entries)}")
        # If synonyms are off, allow much larger chunks
        if not self.validator.use_synonyms:
            SAFE_TOKENS = 29000
            MAX_ONTOLOGY_CHARS = SAFE_TOKENS * CHARS_PER_TOKEN
            print(f"[DEBUG] Synonyms off: using larger chunk size (SAFE_TOKENS={SAFE_TOKENS})")
        ontology_text = "\n".join(ontology_entries)
        ontology_chars = len(ontology_text)
        ontology_words = len(ontology_text.split())
        ontology_tokens = ontology_chars // 4
        # Chunk ontology so each chunk + vignette is < MAX_ONTOLOGY_CHARS
        chunk_char_budget = MAX_ONTOLOGY_CHARS - vignette_chars
        chunk_entries = []
        current_chunk = []
        current_len = 0
        chunk_words = []
        chunk_tokens = []
        for entry in ontology_entries:
            entry_len = len(entry) + 1  # +1 for newline
            if current_len + entry_len > chunk_char_budget and current_chunk:
                chunk_entries.append(current_chunk)
                chunk_text = " ".join(current_chunk)
                chunk_words.append(len(chunk_text.split()))
                chunk_tokens.append(len(chunk_text) // 4)
                current_chunk = []
                current_len = 0
            current_chunk.append(entry)
            current_len += entry_len
        if current_chunk:
            chunk_entries.append(current_chunk)
            chunk_text = " ".join(current_chunk)
            chunk_words.append(len(chunk_text.split()))
            chunk_tokens.append(len(chunk_text) // 4)
        num_chunks = len(chunk_entries)
        print(f"[MATCHER REPORT] Vignette: {vignette_chars} chars, {vignette_words} words, ~{vignette_tokens} tokens")
        print(f"[MATCHER REPORT] Ontology: {ontology_chars} chars, {ontology_words} words, ~{ontology_tokens} tokens")
        print(f"[MATCHER REPORT] Ontology chunks: {num_chunks}")
        print(f"[MATCHER REPORT] Ontology per chunk: {[{'chars': sum(len(e)+1 for e in chunk), 'words': w, 'tokens': t} for chunk, w, t in zip(chunk_entries, chunk_words, chunk_tokens)]}")

        best_match = None
        best_confidence = -1
        best_reasoning = ""
        for chunk_idx, chunk in enumerate(chunk_entries):
            candidate_text = "\n".join(chunk)
            for attempt in range(max_retries):
                try:
                    result = self.matcher(
                        package_name=package_name,
                        package_description=package_description,
                        candidate_terms=candidate_text
                    )
                    # Normalize label and ID if a synonym was returned
                    norm_label, norm_id = self.validator.normalize_label_and_id(result.edam_label)
                    if norm_label and norm_id:
                        result.edam_label = norm_label
                        result.edam_id = norm_id
                    # Validate the result
                    is_valid, error_msg = self.validator.validate_match(result.edam_id, result.edam_label)
                    # If validation fails, try to fix the match
                    if not is_valid:
                        print(f"⚠️  Validation failed for {package_name}: {error_msg}")
                        corrected_id, corrected_label = self.validator.fix_match(result.edam_id, result.edam_label)
                        # Check if fix worked
                        is_valid_fixed, _ = self.validator.validate_match(corrected_id, corrected_label)
                        if is_valid_fixed:
                            print(f"✅ Fixed match: {corrected_id} -> {corrected_label}")
                            result.edam_id = corrected_id
                            result.edam_label = corrected_label
                            is_valid = True
                        else:
                            print(f"❌ Could not fix match for {package_name}")
                    # Create the match object
                    match = OntologyMatch(
                        edam_id=result.edam_id,
                        edam_label=result.edam_label,
                        confidence_score=float(result.confidence_score),
                        reasoning=result.reasoning,
                        validated=is_valid
                    )
                    # Track best match across all chunks
                    if match.confidence_score > best_confidence:
                        best_match = match
                        best_confidence = match.confidence_score
                        best_reasoning = match.reasoning
                    break  # Only use first successful attempt per chunk
                except Exception as e:
                    if 'RateLimitError' in str(e) or 'quota' in str(e):
                        print(f"[RETRY] OpenAI RateLimitError or quota error on attempt {attempt+1}/{max_retries}: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(10 * (attempt + 1))
                            continue
                    print(f"❌ Error matching {package_name} in chunk {chunk_idx+1}: {e}")
                    break
        # Only suggest a new term if no valid match found in any chunk
        if best_match:
            return {
                'edam_id': best_match.edam_id,
                'edam_label': best_match.edam_label,
                'confidence_score': best_match.confidence_score,
                'reasoning': best_match.reasoning,
                'validated': best_match.validated
            }
        # Fallback if no match found
        print(f"[MATCHER REPORT] No valid match found in any chunk. Suggesting new term.")
        return {
            'edam_id': "http://edamontology.org/topic_3365",
            'edam_label': "Data architecture, analysis and design",
            'confidence_score': 0.1,
            'reasoning': f"Error during matching: No valid match found in any chunk.",
            'validated': False
        }



    def suggest_new_designation(self, package_name: str, package_description: str, low_confidence_match: OntologyMatch) -> NewDesignationSuggestion:
        """
        Suggest a new EDAM designation for packages with low confidence matches.
        
        Args:
            package_name: Name of the package
            package_description: Description of the package
            low_confidence_match: The best existing match that had low confidence
            
        Returns:
            NewDesignationSuggestion with suggested new term
        """
        # Get sample of existing terms for context
        sample_terms = self.get_existing_terms_sample()
        
        try:
            result = self.suggester(
                package_name=package_name,
                package_description=package_description,
                low_confidence_match=f"{low_confidence_match.edam_label} (confidence: {low_confidence_match.confidence_score:.3f})",
                existing_terms_sample=sample_terms
            )
            
            return NewDesignationSuggestion(
                suggested_label=result.suggested_label,
                suggested_category=result.suggested_category,
                justification=result.justification,
                similar_terms=result.similar_terms.split(', ') if result.similar_terms else [],
                confidence_score=float(result.confidence_score)
            )
            
        except Exception as e:
            print(f"❌ Error suggesting new designation for {package_name}: {e}")
            return NewDesignationSuggestion(
                suggested_label=f"Specialized {package_name} analysis",
                suggested_category="operation",
                justification=f"Could not generate suggestion due to error: {str(e)}",
                similar_terms=[],
                confidence_score=0.1
            )
    
    def get_fallback_terms(self) -> Dict[str, str]:
        """Get fallback terms when no specific matches are found."""
        fallback_ids = [
            "http://edamontology.org/topic_3365",  # Data architecture, analysis and design
            "http://edamontology.org/topic_0003",  # Topic
            "http://edamontology.org/operation_2945"  # Analysis
        ]
        
        fallback_terms = {}
        for term_id in fallback_ids:
            row = self.edam_df[self.edam_df['Class ID'] == term_id]
            if not row.empty:
                label = row.iloc[0]['Preferred Label']
                definition = row.iloc[0]['Definitions'] if pd.notna(row.iloc[0]['Definitions']) else ""
                fallback_terms[term_id] = f"{label}: {definition}" if definition else label
        
        return fallback_terms
    
    def get_existing_terms_sample(self) -> str:
        """Get a sample of existing EDAM terms for context in suggestions."""
        sample_terms = []
        
        # Get samples from each category
        categories = ['topic_', 'operation_', 'data_', 'format_']
        for category in categories:
            category_terms = self.edam_df[
                self.edam_df['Class ID'].str.contains(category, na=False)
            ].head(5)
            
            for _, row in category_terms.iterrows():
                sample_terms.append(f"- {row['Class ID']}: {row['Preferred Label']}")
        
        return "\n".join(sample_terms)
    
    def process_packages_in_batches(self, packages_data: List[Dict[str, Any]], confidence_threshold: float = 0.5, simple_mode: Optional[bool] = None) -> List[Dict[str, Any]]:
        if simple_mode is None:
            simple_mode = self.simple_mode
        """
        Process packages in batches to avoid context limitations.
        
        Args:
            packages_data: List of package dictionaries with 'name' and 'description'
            confidence_threshold: Threshold for suggesting new designations
            
        Returns:
            List of packages with their EDAM matches
        """

        if simple_mode is None:
            simple_mode = self.simple_mode


        total_packages = len(packages_data)
        num_batches = math.ceil(total_packages / self.batch_size)
        
        print(f"📦 Processing {total_packages} packages in {num_batches} batches of {self.batch_size}")
        
        all_results = []
        
        for batch_num in range(num_batches):
            start_idx = batch_num * self.batch_size
            end_idx = min(start_idx + self.batch_size, total_packages)
            batch = packages_data[start_idx:end_idx]
            
            print(f"\n🔄 Processing batch {batch_num + 1}/{num_batches} (packages {start_idx + 1}-{end_idx})")
            
            batch_results = []
            
            for i, package in enumerate(batch):
                if 'name' not in package or 'description' not in package:
                    print(f"⚠️  Skipping package {start_idx + i + 1}: missing name or description")
                    continue
                
                print(f"  [{i + 1}/{len(batch)}] {package['name']}")
                
                # Match to EDAM ontology
                match = self.match_package_to_ontology(
                    package['name'], 
                    package['description'],
                    confidence_threshold,
                    simple_mode=simple_mode
                )
                
                # Add the match to the package data
                package_result = package.copy()
                package_result['edam_match'] = match
                batch_results.append(package_result)
                print(f"    -> {match['edam_label']} (confidence: {match['confidence_score']:.3f}, validated: {match['validated']})")
            
            all_results.extend(batch_results)
            
            # Save intermediate results after each batch
            batch_output_file = f'batch_{batch_num + 1}_results.json'
            with open(batch_output_file, 'w') as f:
                json.dump(batch_results, f, indent=2)
            
            print(f"✅ Batch {batch_num + 1} complete. Results saved to {batch_output_file}")
        
        return all_results
    
    def process_bioconductor_packages_enhanced(self, packages_json_path: str, confidence_threshold: float = 0.5, simple_mode: Optional[bool] = None) -> List[Dict[str, Any]]:
        if simple_mode is None:
            simple_mode = self.simple_mode
        """
        Process Bioconductor packages with enhanced features.
        
        Args:
            packages_json_path: Path to the bioc_packages_summary.json file
            confidence_threshold: Threshold for suggesting new designations
            
        Returns:
            List of packages with their EDAM matches
        """
        # Load the package data
        with open(packages_json_path, 'r') as f:
            packages = json.load(f)
        
        print(f"📊 Loaded {len(packages)} packages from {packages_json_path}")
        
        # Process in batches
        results = self.process_packages_in_batches(packages, confidence_threshold, simple_mode = simple_mode)
        
        return results


def main():
    """Main function to run the enhanced EDAM matching system."""
    
    # Check for required files
    if not os.path.exists('EDAM.csv'):
        print("❌ Error: EDAM.csv file not found!")
        return
    
    if not os.path.exists('bioc_packages_summary.json'):
        print("❌ Error: bioc_packages_summary.json file not found!")
        print("Please run the parse_biocviews.py script first.")
        return
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("🚀 Starting Enhanced EDAM Ontology Matching System")
    print("=" * 60)
    print("🔧 Features: Validation + Batch Processing + Low Confidence Handling")
    print("=" * 60)
    
    # Initialize the enhanced system
    system = EnhancedEDAMMatchingSystem('EDAM.csv', batch_size=5000, simple_mode=True, use_synonyms=False)
    
    # Process the packages
    print("\n📦 Processing Bioconductor packages...")
    results = system.process_bioconductor_packages_enhanced('bioc_packages_summary.json', confidence_threshold=0.5, simple_mode = system.simple_mode)
    
    # Save final results
    output_file = 'enhanced_edam_matched_packages.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 Final results saved to: {output_file}")
    print(f"📊 Processed {len(results)} packages total")
    
    # Print summary statistics
    validated_matches = sum(1 for r in results if r.get('edam_match', {}).get('validated', False))
    high_confidence = sum(1 for r in results if r.get('edam_match', {}).get('confidence_score', 0) >= 0.8)
    medium_confidence = sum(1 for r in results if 0.5 <= r.get('edam_match', {}).get('confidence_score', 0) < 0.8)
    low_confidence = sum(1 for r in results if r.get('edam_match', {}).get('confidence_score', 0) < 0.5)
    
    print(f"\n📈 Enhanced Statistics:")
    print(f"   Validated matches: {validated_matches}/{len(results)} ({validated_matches/len(results)*100:.1f}%)")
    print(f"   High confidence (≥0.8): {high_confidence}")
    print(f"   Medium confidence (0.5-0.8): {medium_confidence}")
    print(f"   Low confidence (<0.5): {low_confidence} (new designations suggested)")


if __name__ == "__main__":
    main()
