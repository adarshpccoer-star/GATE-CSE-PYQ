import fitz  # PyMuPDF
import re

def extract_clean_pages(pdf_path: str, debug=False):
    """
    Extract text from PDF and remove corporate footer noise.
    Handles various footer patterns and formatting issues.
    """
    doc = fitz.open(pdf_path)
    pages_data = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        original_text = text  # Keep original for debugging
        
        # Strategy 1: Remove by bounding box (footer is usually at bottom)
        # Get footer area (bottom 20% of page)
        rect = page.rect
        footer_height = rect.height * 0.2
        footer_rect = fitz.Rect(rect.x0, rect.y1 - footer_height, rect.x1, rect.y1)
        
        # Extract footer text for debugging
        footer_text = page.get_text("text", clip=footer_rect)
        
        if debug:
            print(f"\n=== PAGE {i+1} DEBUG ===")
            print(f"Footer area text: {repr(footer_text[:200])}")
        
        # Strategy 2: Multiple regex patterns (try all)
        clean_text = text
        
        # Pattern 1: Corporate Office to Kolkata (flexible spacing)
        clean_text = re.sub(
            r"Corporate\s+Office:.*?Kolkata",
            "",
            clean_text,
            flags=re.IGNORECASE | re.DOTALL
        )
        
        # Pattern 2: Common footer markers - match from any phone/email pattern to end
        clean_text = re.sub(
            r"\+91.*?(?=\n\n|\Z)",
            "",
            clean_text,
            flags=re.DOTALL
        )
        
        # Pattern 3: Remove lines that match typical footer elements
        lines = clean_text.split('\n')
        filtered_lines = []
        
        footer_keywords = [
            'corporate office',
            'kolkata',
            'bangalore',
            'mumbai',
            'delhi',
            'office:',
            'phone:',
            'email:',
            'www.',
            '.com',
            '+91',
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            # Skip lines that are ONLY footer-like content
            if line_lower and not any(keyword in line_lower for keyword in footer_keywords):
                filtered_lines.append(line)
            elif line_lower == '':  # Keep blank lines
                filtered_lines.append(line)
        
        clean_text = '\n'.join(filtered_lines)
        
        # Remove multiple consecutive blank lines
        clean_text = re.sub(r"\n\n\n+", "\n\n", clean_text)
        clean_text = clean_text.strip()
        
        if debug and footer_text.strip():
            print(f"Original text length: {len(original_text)}")
            print(f"Cleaned text length: {len(clean_text)}")
            print(f"Footer removed: {len(original_text) - len(clean_text)} chars")
        
        pages_data.append({
            "page": i + 1,
            "text": clean_text
        })

    doc.close()
    return pages_data


def inspect_pdf_footers(pdf_path: str, sample_pages=3):
    """
    Inspect a PDF to understand footer structure.
    Run this first to see what you're dealing with.
    """
    doc = fitz.open(pdf_path)
    print(f"Total pages: {len(doc)}\n")
    
    pages_to_check = min(sample_pages, len(doc))
    
    for i in range(pages_to_check):
        page = doc[i]
        print(f"\n{'='*60}")
        print(f"PAGE {i+1}")
        print(f"{'='*60}")
        
        text = page.get_text("text")
        
        # Show last 800 chars (where footer usually is)
        print("\n--- LAST 800 CHARACTERS (FOOTER AREA) ---")
        footer_sample = text[-800:]
        print(repr(footer_sample))
        print("\nFormatted view:")
        print(footer_sample)
        
        # Try to detect footer lines
        lines = text.split('\n')
        print(f"\n--- LAST 15 LINES ---")
        for line in lines[-15:]:
            print(f"[{len(line):3d} chars] {repr(line[:100])}")
    
    doc.close()


# Usage example:
if __name__ == "__main__":
    pdf_path = "your_document.pdf"
    
    # First: Inspect the footer structure
    print("INSPECTING PDF STRUCTURE...")
    inspect_pdf_footers(pdf_path, sample_pages=2)
    
    # Then: Extract clean pages
    print("\n" + "="*60)
    print("EXTRACTING CLEAN PAGES...")
    print("="*60)
    pages = extract_clean_pages(pdf_path, debug=True)
    
    # Show results
    for page_data in pages[:2]:  # Show first 2 pages
        print(f"\n--- Page {page_data['page']} ---")
        print(page_data['text'][:500] + "...")
        print(f"Length: {len(page_data['text'])} chars")