# EDAMnotation

Trying to annotate Bioconductor packages using EDAM ontology with DSPy and GPT-4o.

## Quick Start

### 1. Download the EDAM ontology

```bash
wget https://edamontology.org/EDAM.csv
```

### 2. Download the Bioconductor views

```bash
curl https://www.bioconductor.org/packages/release/bioc/VIEWS -o biocviews.txt
```

### 3. Parse the Bioconductor data

```bash
python parse_biocviews.py
```

This creates a file called `bioc_packages_summary.json` with structured data including vignettes.
Vignettes are processed with pandoc if .html and pymupdf4llm if .pdf

### 4. Set up OpenAI API key

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

### 5. Run the EDAM matching system

```bash
python edam_ontology_matcher.py
```

## System Features

This uses DSPy to force GPT-4o to suggest:
- **Specific EDAM designation** with ID and label
- **Confidence score** (0.0-1.0) 
- **Reasoning** for the match

Additional features:
- **Pure Python validator** to check that the label exists in CSV and the URL too
- **Batch processing** with 5000 entries at a time to avoid context limits
- **Low confidence handler** - if confidence < 0.5, suggests a new EDAM designation

## Testing

### Test with Four Specific Packages

```bash
# Test the system with 4 real Bioconductor packages
python test_four_packages_real_dspy.py
```

This tests:
- **DESeq2**: Differential expression analysis
- **miloR**: Single-cell differential abundance testing  
- **Rsubread**: Sequencing read processing pipeline
- **GEOquery**: Data retrieval from NCBI GEO