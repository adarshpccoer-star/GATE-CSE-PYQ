import pdfplumber
import io
import pandas as pd

def extract_tables_from_pdf(pdf_bytes):
    formatted_tables = []
    
    # Use pdfplumber to open the PDF from memory
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            # Find tables on the page
            tables = page.extract_tables()
            
            for table in tables:
                # Convert the raw list-of-lists into a DataFrame
                # We use the first row as the header
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    
                    # Clean up: remove empty rows or columns
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    
                    if not df.empty:
                        formatted_tables.append(df.to_markdown())
                        
    return formatted_tables