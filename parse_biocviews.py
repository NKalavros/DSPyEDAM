import re
import requests
import os
from urllib.parse import urljoin
import time
import subprocess
import json

def parse_biocviews(file_path, max_vignettes=4):
    with open(file_path, 'r') as f:
        content = f.read()

    # Split entries by double newlines (each package is separated by blank lines)
    entries = re.split(r'\n\s*\n', content)
    results = []
    total_downloaded = 0

    for entry in entries:
        if total_downloaded >= max_vignettes:
            break
            
        pkg = {}
        # Extract package name
        m = re.search(r'^Package:\s*(\S+)', entry, re.MULTILINE)
        if m:
            pkg['name'] = m.group(1)
            pkg['url'] = f"https://bioconductor.org/packages/{pkg['name']}"
        # Extract description
        m = re.search(r'^Description:\s*(.+?)(?=\n\S|$)', entry, re.DOTALL | re.MULTILINE)
        if m:
            pkg['description'] = ' '.join(m.group(1).split())
        # Extract vignette PDF(s)
        m = re.search(r'^vignettes:\s*(.+)$', entry, re.MULTILINE)
        if m:
            vignettes = [v.strip() for v in m.group(1).split(',')]
            # Only keep PDFs and HTML files
            docs = [v for v in vignettes if v.lower().endswith(('.pdf', '.html'))]
            pkg['vignettes'] = docs
            
            # Download accessible vignettes (but respect the limit)
            downloaded_files = []
            for doc in docs:
                if total_downloaded >= max_vignettes:
                    break
                # Construct full URL - vignettes are relative to the package URL
                doc_url = f"https://bioconductor.org/packages/release/bioc/{doc}"
                downloaded_file = download_if_accessible(doc_url, pkg['name'])
                if downloaded_file:
                    downloaded_files.append(downloaded_file)
                    total_downloaded += 1
            pkg['downloaded_vignettes'] = downloaded_files
        if pkg:
            results.append(pkg)
    return results

def download_if_accessible(url, package_name, max_retries=3):
    """Check if URL is accessible and download if it exists."""
    try:
        # Check if URL is accessible with HEAD request first
        response = requests.head(url, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # Create downloads directory
            download_dir = f"downloads/{package_name}"
            os.makedirs(download_dir, exist_ok=True)
            
            # Get filename from URL
            filename = os.path.basename(url)
            if not filename:
                filename = "vignette.pdf"
            
            file_path = os.path.join(download_dir, filename)
            
            # Download the file
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=30, stream=True)
                    if response.status_code == 200:
                        with open(file_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"Downloaded: {file_path}")
                        return file_path
                    else:
                        print(f"Failed to download {url}: HTTP {response.status_code}")
                        return None
                except requests.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"Retry {attempt + 1} for {url}: {e}")
                        time.sleep(2)
                    else:
                        print(f"Failed to download {url} after {max_retries} attempts: {e}")
                        return None
        else:
            print(f"URL not accessible: {url} (HTTP {response.status_code})")
            return None
            
    except requests.RequestException as e:
        print(f"Error checking {url}: {e}")
        return None

def convert_html_to_markdown(html_file_path):
    """Convert HTML file to markdown using pandoc."""
    try:
        markdown_file = html_file_path.replace('.html', '.md')
        result = subprocess.run([
            'pandoc', html_file_path, '-o', markdown_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"Converted to markdown: {markdown_file}")
            return markdown_file
        else:
            print(f"Failed to convert {html_file_path}: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"Timeout converting {html_file_path}")
        return None
    except FileNotFoundError:
        print("pandoc not found. Installing...")
        try:
            subprocess.run(['brew', 'install', 'pandoc'], check=True)
            return convert_html_to_markdown(html_file_path)  # Retry after installation
        except subprocess.CalledProcessError:
            print("Failed to install pandoc. Please install manually.")
            return None

def process_with_pymu4llm(file_path):
    """Process PDF or markdown file with PyMu4LLM."""
    try:
        output_file = file_path.replace(os.path.splitext(file_path)[1], '_extracted.txt')
        
        if file_path.endswith('.pdf'):
            # Process PDF using pymupdf4llm directly
            import pymupdf4llm
            md_text = pymupdf4llm.to_markdown(file_path)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Extracted content from {os.path.basename(file_path)}\n\n")
                f.write(md_text)
            print(f"PyMu4LLM processed PDF: {output_file}")
            return output_file
        else:
            # For markdown files, just copy content with some processing
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Extracted content from {os.path.basename(file_path)}\n\n")
                f.write(content)
            print(f"Processed markdown: {output_file}")
            return output_file
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    # Create downloads directory
    os.makedirs("downloads", exist_ok=True)
    
    print("Parsing Bioconductor packages...")
    bioc_pkgs = parse_biocviews('biocviews.txt', max_vignettes=4)
    
    print(f"Found {len(bioc_pkgs)} packages")
    
    # Count total downloaded files
    downloaded_count = 0
    for pkg in bioc_pkgs:
        if 'downloaded_vignettes' in pkg and pkg['downloaded_vignettes']:
            downloaded_count += len(pkg['downloaded_vignettes'])
    
    for i, pkg in enumerate(bioc_pkgs):
        print(f"\nPackage {i+1}: {pkg.get('name', 'Unknown')}")
        print(f"Description: {pkg.get('description', 'N/A')[:100]}...")
        
        if 'downloaded_vignettes' in pkg and pkg['downloaded_vignettes']:
            print(f"Downloaded {len(pkg['downloaded_vignettes'])} vignette(s)")
        else:
            print("No vignettes found or accessible")
    
    print(f"\n=== Summary ===")
    print(f"Processed: {len(bioc_pkgs)} packages")
    print(f"Total files downloaded: {downloaded_count}")
    print(f"Download directory: downloads/")
    
    # Process downloaded files
    print(f"\n=== Converting and Processing Files ===")
    all_processed_files = []
    
    for pkg in bioc_pkgs:
        if 'downloaded_vignettes' in pkg and pkg['downloaded_vignettes']:
            print(f"\nProcessing files for package: {pkg['name']}")
            processed_files = []
            
            for file_path in pkg['downloaded_vignettes']:
                if file_path.endswith('.html'):
                    # Convert HTML to markdown
                    markdown_file = convert_html_to_markdown(file_path)
                    if markdown_file:
                        # Process markdown with PyMu4LLM
                        processed_file = process_with_pymu4llm(markdown_file)
                        if processed_file:
                            processed_files.append(processed_file)
                elif file_path.endswith('.pdf'):
                    # Process PDF directly with PyMu4LLM
                    processed_file = process_with_pymu4llm(file_path)
                    if processed_file:
                        processed_files.append(processed_file)
            
            pkg['processed_files'] = processed_files
            all_processed_files.extend(processed_files)
    
    print(f"\n=== Processing Complete ===")
    print(f"Total processed files: {len(all_processed_files)}")
    for f in all_processed_files:
        print(f"  - {f}")
    
    # Save summary to JSON for further processing
    import json
    with open('bioc_packages_summary.json', 'w') as f:
        json.dump(bioc_pkgs, f, indent=2)
    print(f"Package summary saved to: bioc_packages_summary.json")