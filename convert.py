import docx
import os
import sys

def convert_to_markdown(docx_path, md_path):
    try:
        doc = docx.Document(docx_path)
        md_content = []
        
        for para in doc.paragraphs:
            if not para.text.strip():
                continue
                
            style_name = para.style.name.lower() if para.style and para.style.name else "normal"
            text = para.text.strip()
            
            # Simple bold/italic extraction
            para_markdown = ""
            for run in para.runs:
                run_text = run.text
                if not run_text.strip():
                    para_markdown += run_text
                    continue
                
                # Check formatting
                if run.bold:
                    run_text = f"**{run_text}**"
                if run.italic:
                    run_text = f"*{run_text}*"
                    
                para_markdown += run_text
            
            if not para_markdown.strip():
                continue
                
            if 'heading 1' in style_name or style_name == 'title' or 'judul' in style_name:
                md_content.append(f"# {para_markdown}")
            elif 'heading 2' in style_name:
                md_content.append(f"## {para_markdown}")
            elif 'heading 3' in style_name:
                md_content.append(f"### {para_markdown}")
            elif 'heading 4' in style_name:
                md_content.append(f"#### {para_markdown}")
            elif 'heading 5' in style_name:
                md_content.append(f"##### {para_markdown}")
            elif 'heading 6' in style_name:
                md_content.append(f"###### {para_markdown}")
            elif 'list bullet' in style_name or 'list' in style_name and 'number' not in style_name:
                md_content.append(f"* {para_markdown}")
            elif 'list number' in style_name:
                md_content.append(f"1. {para_markdown}")
            else:
                md_content.append(para_markdown)
                
            md_content.append("") # Empty line after paragraph
            
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
            
        print(f"Successfully converted to {md_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert.py input.docx output.md")
    else:
        convert_to_markdown(sys.argv[1], sys.argv[2])
