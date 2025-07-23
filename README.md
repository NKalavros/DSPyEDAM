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

### Test with Five Specific Packages

```bash
# Test the system with 4 real Bioconductor packages
python vignette_edam_matcher.py --packages DESeq2,limma,AnnotationDbi,GEOquery,miloR --output normal.json --edam-csv EDAM.csv --simple_mode --iterative_mode --threshold 0.8 
```

#### Parameters explanation

```
--packages Comma separated list of packages, you can also get it from parse_biocviewspy
```

```
--output testing.json Output file
```

```
edam-csv - The CSV file of the KB
```

```
--simple_mode - If present, will use only "Preferred Label"
```

```
--iterative_mode - If present, runs a second round by expanding with the definition of the term on a certain number of terms.
```

```
--iterative_top_n - that's how many terms are kept. If the estimated tokens are above the expected rate limit (30k), halves until not
```

```
--threshold - Return all designations above specific threshold
```

It will also always try to suggest a new matching. You can filter later if you don't want that.