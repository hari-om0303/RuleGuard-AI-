import os
import re
import csv
from typing import List, Dict, Any

class DocumentLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_all_documents(self) -> List[Dict[str, Any]]:
        raw_documents = []
        
        # 1. Load Markdown files
        md_dir = os.path.join(self.data_dir, "markdown")
        if os.path.exists(md_dir):
            for fname in os.listdir(md_dir):
                if fname.endswith(".md"):
                    fpath = os.path.join(md_dir, fname)
                    raw_documents.extend(self.load_markdown_file(fpath, fname))

        # 2. Load Table (CSV) files
        tables_dir = os.path.join(self.data_dir, "tables")
        if os.path.exists(tables_dir):
            for fname in os.listdir(tables_dir):
                if fname.endswith(".csv"):
                    fpath = os.path.join(tables_dir, fname)
                    raw_documents.extend(self.load_csv_file(fpath, fname))

        # 3. Load PDF files
        pdf_dir = os.path.join(self.data_dir, "pdf")
        if os.path.exists(pdf_dir):
            for fname in os.listdir(pdf_dir):
                if fname.endswith(".pdf"):
                    fpath = os.path.join(pdf_dir, fname)
                    raw_documents.extend(self.load_pdf_file(fpath, fname))

        return raw_documents

    def load_markdown_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split content into sections based on ## or ### headers containing "Section X.Y"
        section_pattern = re.compile(r'(^|\n)(#{2,3}\s+(Section\s+\d+\.\d+.*?))(?=\n#{2,3}\s+Section|\Z)', re.DOTALL)
        matches = section_pattern.findall(content)
        
        sections = []
        if matches:
            for match in matches:
                full_block = match[1].strip()
                header_line = full_block.split('\n')[0].strip()
                body = '\n'.join(full_block.split('\n')[1:]).strip()
                
                # Extract section number and title
                sec_match = re.search(r'Section\s+(\d+\.\d+)\s*:?\s*(.*)', header_line, re.IGNORECASE)
                if sec_match:
                    sec_num = f"Section {sec_match.group(1)}"
                    sec_title = sec_match.group(2).strip("# ").strip()
                else:
                    sec_num = "Section General"
                    sec_title = header_line.strip("# ").strip()
                
                sections.append({
                    "document": filename,
                    "section": sec_num,
                    "title": sec_title,
                    "text": full_block,
                    "page": None,
                    "source_type": "markdown"
                })
        else:
            # Fallback if regex split didn't find standard headers
            sections.append({
                "document": filename,
                "section": "Section General",
                "title": filename,
                "text": content,
                "page": None,
                "source_type": "markdown"
            })
        return sections

    def load_csv_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        sections = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sec_num = row.get("Section Number", "Section Table").strip()
                category = row.get("Category / Fee Component", "Fee Schedule").strip()
                deadline = row.get("Official Deadline Date / Window", "").strip()
                penalty = row.get("Late Penalty / Fee Amount", "").strip()
                rules = row.get("Grace Period Rules & Conditions", "").strip()
                
                text_content = (
                    f"{sec_num}: {category}\n"
                    f"Official Deadline: {deadline}\n"
                    f"Late Penalty: {penalty}\n"
                    f"Grace Period & Rules: {rules}"
                )
                
                sections.append({
                    "document": filename,
                    "section": sec_num,
                    "title": category,
                    "text": text_content,
                    "page": None,
                    "source_type": "table"
                })
        return sections

    def load_pdf_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        sections = []
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text()
                # Find sections in page text
                sec_matches = re.finditer(r'(Section\s+\d+\.\d+)\s+([^\n]+)', text)
                last_pos = 0
                match_list = list(sec_matches)
                if match_list:
                    for i, m in enumerate(match_list):
                        sec_num = m.group(1).strip()
                        sec_title = m.group(2).strip()
                        start_pos = m.start()
                        end_pos = match_list[i+1].start() if i+1 < len(match_list) else len(text)
                        chunk_text = text[start_pos:end_pos].strip()
                        sections.append({
                            "document": filename,
                            "section": sec_num,
                            "title": sec_title,
                            "text": chunk_text,
                            "page": page_idx + 1,
                            "source_type": "pdf"
                        })
                else:
                    sections.append({
                        "document": filename,
                        "section": "Section PDF",
                        "title": f"PDF Page {page_idx + 1}",
                        "text": text.strip(),
                        "page": page_idx + 1,
                        "source_type": "pdf"
                    })
        except Exception as e:
            print(f"Warning: Failed to parse PDF {filename} using pypdf: {e}")
        return sections
