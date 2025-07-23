# EDAM Ontology Matching System

A DSPy-based system that automatically matches Bioconductor package descriptions to EDAM (EMBL-EBI's Ontology of Bioinformatics operations, data types, formats, identifiers and topics) ontology terms with confidence scores.

## Features

- 🎯 **Intelligent Matching**: Uses DSPy and GPT-4o to intelligently match package descriptions to relevant EDAM terms
- 📊 **Confidence Scoring**: Provides confidence scores (0.0-1.0) for each match
- 🔍 **Structured Output**: Returns standardized JSON output with EDAM IDs, labels, scores, and reasoning
- 🏗️ **Modular Design**: Built with DSPy for easy optimization and improvement
- 📈 **Scalable**: Can process multiple packages efficiently

## System Architecture

The system uses the DSPy framework to create a structured approach to ontology matching:

1. **Data Loading**: Loads EDAM ontology from CSV and filters to active terms
2. **Candidate Selection**: Uses keyword-based relevance scoring to find potential matches
3. **LLM Matching**: Uses GPT-4o with structured prompts to select the best match
4. **Confidence Assessment**: Provides confidence scores and reasoning for each match

## Setup

### Prerequisites

- Python 3.10+
- OpenAI API key
- EDAM.csv file (included)
- Bioconductor package data (from parse_biocviews.py)

### Installation

```bash
# Install required packages
pip install dspy pandas pydantic

# Set your OpenAI API key
export OPENAI_API_KEY='your-openai-api-key-here'
```

### Files Required

- `EDAM.csv` - EDAM ontology data ✅ (already present)
- `bioc_packages_summary.json` - Package data from parse_biocviews.py ✅ (already present)

## Usage

### Quick Test

```bash
# Test the system with a simple example
python test_edam_matcher.py
```

### Full Processing

```bash
# Process all Bioconductor packages
python edam_ontology_matcher.py
```

### Programmatic Usage

```python
from edam_ontology_matcher import EDAMMatchingSystem

# Initialize the system
system = EDAMMatchingSystem('EDAM.csv')

# Match a single package
match = system.match_package_to_ontology(
    package_name="a4",
    package_description="Automated Affymetrix Array Analysis Umbrella Package"
)

print(f"Best match: {match.edam_label}")
print(f"Confidence: {match.confidence_score}")
print(f"Reasoning: {match.reasoning}")

# Process multiple packages
results = system.process_bioconductor_packages('bioc_packages_summary.json')
```

## Testing

### Four Package Test Case

To verify the system is working correctly, run the test with four specific Bioconductor packages:

```bash
# Test with 4 specific packages using real DSPy calls
python test_four_packages_real_dspy.py
```

This test processes these packages:

| Package | Description | Purpose |
|---------|-------------|---------|
| **DESeq2** | Variance-mean dependence in count data from high-throughput sequencing assays | Differential expression analysis |
| **miloR** | Single-cell differential abundance testing with neighborhood modeling | Single-cell analysis |
| **Rsubread** | Alignment, quantification and analysis of sequencing data | Read processing pipeline |
| **GEOquery** | Tools to query and retrieve data from NCBI Gene Expression Omnibus | Data retrieval |

### Expected Test Results

```bash
🧪 Testing EDAM Ontology Matching with Real DSPy
=======================================================
🚀 Initializing DSPy-based EDAM matching system...
Loaded 2359 active EDAM terms

🔬 Processing 4 packages with real DSPy calls...
-------------------------------------------------------

[1/4] Processing: DESeq2
✅ EDAM Match (via DSPy + OpenAI GPT-4o):
   ID: http://edamontology.org/operation_3800
   Label: RNA-Seq quantification
   Confidence: 0.900

[2/4] Processing: miloR
✅ EDAM Match (via DSPy + OpenAI GPT-4o):
   ID: http://edamontology.org/data_3498
   Label: Sequence variations
   Confidence: 0.300

[3/4] Processing: Rsubread
✅ EDAM Match (via DSPy + OpenAI GPT-4o):
   ID: http://edamontology.org/operation_3921
   Label: Sequence read processing
   Confidence: 0.900

[4/4] Processing: GEOquery
✅ EDAM Match (via DSPy + OpenAI GPT-4o):
   ID: http://edamontology.org/operation_2422
   Label: Data retrieval
   Confidence: 0.900

📊 Summary:
   Total packages: 4
   Successful matches: 4
   Average confidence: 0.750
   High confidence (>0.8): 3
   Low confidence (<0.5): 1
```

### Enhanced Features Testing

For testing the enhanced system with validation, batch processing, and low confidence suggestions:

```bash
# Test all enhanced features
python test_enhanced_features.py
```

This includes:
- **Validator Testing**: Verifies EDAM ID/Label existence in CSV
- **Batch Processing**: Tests processing multiple packages in batches
- **Low Confidence Suggestions**: Tests new designation suggestions
- **Complete System**: End-to-end testing with all features

### Manual Testing

```python
# Test a single package manually
from edam_ontology_matcher import EDAMMatchingSystem

system = EDAMMatchingSystem('EDAM.csv')
match = system.match_package_to_ontology(
    "DESeq2",
    "Estimate variance-mean dependence in count data from high-throughput sequencing assays"
)

print(f"Match: {match.edam_label}")
print(f"Confidence: {match.confidence_score}")
print(f"ID: {match.edam_id}")
```

## Output Format

The system generates structured output in JSON format:

```json
{
  "name": "a4",
  "description": "Automated Affymetrix Array Analysis...",
  "edam_match": {
    "edam_id": "http://edamontology.org/topic_0080",
    "edam_label": "Sequence analysis",
    "confidence_score": 0.85,
    "reasoning": "Package focuses on microarray analysis which is closely related to sequence analysis workflows"
  }
}
```

## Confidence Score Interpretation

- **High (≥0.8)**: Strong semantic match, high confidence in the assignment
- **Medium (0.5-0.8)**: Good match with some uncertainty or broader categorization  
- **Low (<0.5)**: Weak match, may need manual review or represents a fallback assignment

## DSPy Framework

This system leverages DSPy's declarative approach to LLM programming:

- **Signatures**: Define input/output behavior for the matching task
- **Modules**: Use ChainOfThought for reasoning about matches
- **Structured Output**: Pydantic models ensure consistent response format
- **Optimization**: Can be improved with DSPy optimizers for better performance

## EDAM Ontology Coverage

The system covers all main EDAM categories:

- **Topics** (`topic_*`): Broad domains like "Sequence analysis", "Proteomics"
- **Operations** (`operation_*`): Computational operations like "Alignment", "Clustering"  
- **Data Types** (`data_*`): Types of data like "Sequence", "Structure"
- **Formats** (`format_*`): Data formats like "FASTA", "XML"

## Example Matches

Here are some example matches the system can make:

| Package | Description | Matched EDAM Term | Confidence |
|---------|-------------|-------------------|------------|
| a4 | Affymetrix array analysis | Gene expression analysis | 0.9 |
| BiocParallel | Parallel computing | Parallel computing | 0.95 |
| GenomicRanges | Genomic intervals | Genome annotation | 0.85 |

## Troubleshooting

### API Key Issues
```bash
# Make sure your API key is set
echo $OPENAI_API_KEY

# Set it if missing
export OPENAI_API_KEY='your-key-here'
```

### File Not Found
- Ensure `EDAM.csv` is in the current directory
- Run `parse_biocviews.py` first to generate `bioc_packages_summary.json`

### Import Errors
```bash
# Install missing dependencies
pip install dspy pandas pydantic
```

## Future Improvements

- **Optimization**: Use DSPy optimizers to improve matching accuracy
- **Caching**: Cache results for faster re-processing
- **Batch Processing**: Process packages in parallel for better performance
- **Validation**: Add validation against manually curated examples
- **Multi-label**: Support for multiple EDAM term assignments per package

## Contributing

The system is designed to be extensible:

1. **New Ontologies**: Easy to adapt for other ontologies (GO, SO, etc.)
2. **Better Matching**: Improve candidate selection algorithms
3. **Validation**: Add evaluation metrics and test cases
4. **UI**: Add web interface for interactive matching

## API Usage

For integration into other systems, the core components can be used independently:

```python
# Just load EDAM data
system = EDAMMatchingSystem('EDAM.csv')
candidates = system.search_relevant_terms("gene expression analysis")

# Custom matching logic
match = system.match_package_to_ontology(name, description)
```

## License

This project builds on:
- DSPy framework (MIT License)
- EDAM ontology (CC BY-SA 4.0)
- OpenAI API (commercial usage terms apply)
