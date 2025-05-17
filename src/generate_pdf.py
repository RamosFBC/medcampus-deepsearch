import textwrap
from datetime import datetime
import os
import re
from fpdf import FPDF
import unicodedata

# Current directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Output directory for PDFs
PDF_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "pdf")

# Define page dimensions and margins
PAGE_WIDTH = 210  # A4 width in mm
PAGE_HEIGHT = 297  # A4 height in mm
MARGIN = 15  # margin in mm - reduced for more space
EFFECTIVE_WIDTH = PAGE_WIDTH - (2 * MARGIN)  # Width available for text

# Define regex patterns for markdown elements
MD_HEADING1 = re.compile(r"^# (.+)$")
MD_HEADING2 = re.compile(r"^## (.+)$")
MD_HEADING3 = re.compile(r"^### (.+)$")
MD_HEADING4 = re.compile(r"^#### (.+)$")
MD_BULLET = re.compile(r"^[\*\-\+] (.+)$")
MD_NUMBERED = re.compile(r"^(\d+)\. (.+)$")
MD_BOLD = re.compile(r"\*\*(.+?)\*\*")
MD_ITALIC = re.compile(r"\*(.+?)\*")
MD_LINK = re.compile(r"\[(.+?)\]\((.+?)\)")
MD_CODE_BLOCK_START = re.compile(r"^```(?:\w+)?$")
MD_CODE_BLOCK_END = re.compile(r"^```$")
MD_INLINE_CODE = re.compile(r"`(.+?)`")
MD_IMAGE = re.compile(r"!\[(.+?)\]\((.+?)\)")
MD_BLOCKQUOTE = re.compile(r"^> (.+)$")


class PDF(FPDF):
    def __init__(self, title="Document"):
        # Initialize with default settings
        super().__init__()
        
        # Set document information
        self.doc_title = title
        self.in_code_block = False
        self.link_blue = (0, 0, 255)  # RGB for links
        
        # Try to set encoding if this version of fpdf supports it
        try:
            self.set_doc_option('core_fonts_encoding', 'latin-1')
        except (AttributeError, TypeError):
            # Older versions of fpdf might not have this method
            pass

    def header(self):
        self.set_font("helvetica", "B", 12)
        # Encode the title to latin-1 to ensure proper display
        self.cell(
            0,
            10,
            self.doc_title,
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        # Encode the footer text to latin-1
        page_text = f"Página {self.page_no()}"
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}"
        
        self.cell(0, 10, page_text, align="C")
        self.ln(5)
        self.cell(0, 5, date_text, align="C")

    def add_heading(self, level, text):
        """Add a heading with appropriate styling based on level"""
        # Add spacing before headings
        if level > 1:
            self.ln(5)

        sizes = {1: 18, 2: 16, 3: 14, 4: 12}
        size = sizes.get(level, 12)

        self.set_font("helvetica", "B", size)
        self.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", size=12)  # Reset font

        # Add spacing after headings
        if level == 1:
            self.ln(5)

    def add_paragraph(self, text):
        """Add a regular paragraph with proper text wrapping"""
        # Process inline formatting (bold, italic, links, inline code)
        text = self.process_inline_formatting(text)

        # Use smaller font for better fit
        self.set_font("helvetica", size=9)  # Reduced to 9 for better fitting

        # Check if text has any formatting markers
        has_formatting = "###" in text

        if has_formatting:
            # For formatted text, use our special rendering function
            self.set_x(10)  # Set consistent left margin

            # Wrap text manually
            wrapped_text = textwrap.wrap(
                text, width=65
            )  # Wider width for formatted text
            for i, wrap in enumerate(wrapped_text):
                if i > 0:
                    self.ln(5)  # Add line spacing between wrapped lines
                self.set_x(10)  # Reset x position for each line
                try:
                    self.render_formatted_text(wrap)
                except Exception as e:
                    # Fall back to simple text if rendering fails
                    self.set_x(10)
                    clean_text = wrap.replace("###BOLD#", "").replace("#BOLD###", "")
                    clean_text = clean_text.replace("###ITALIC#", "").replace(
                        "#ITALIC###", ""
                    )
                    clean_text = clean_text.replace("###LINK#", "").replace(
                        "#LINK###", ""
                    )
                    clean_text = clean_text.replace("###CODE#", "").replace(
                        "#CODE###", ""
                    )
                    # Replace any remaining formatting markers
                    clean_text = re.sub(r"###[A-Z]+#.*?#[A-Z]+###", "", clean_text)
                    self.multi_cell(0, 5, clean_text)

            self.ln(3)  # Add spacing after paragraph
        else:
            # For plain text paragraphs, use the simpler approach
            try:
                # Wrap and write the paragraph
                wrapped_text = textwrap.wrap(text, width=60)  # Increased width
                for wrap in wrapped_text:
                    if wrap:  # Ensure content exists before writing
                        self.set_x(10)  # Set consistent left margin
                        self.multi_cell(0, 5, wrap)

                # Add a small space after paragraphs
                self.ln(3)
            except Exception as e:
                # If multi_cell fails, try using a very simple approach
                self.set_x(10)
                self.write(
                    5, text[:80] + (text[80:] and "...")
                )  # Truncate if necessary
                self.ln(5)

        self.set_font("helvetica", size=12)  # Reset font size

    def add_bullet_point(self, text, level=0):
        """Add a bullet point with proper indentation"""
        # Process inline formatting
        text = self.process_inline_formatting(text)

        # Calculate indentation based on level
        indent = 10 + (level * 5)
        self.set_x(indent)

        self.set_font("helvetica", size=10)
        self.cell(5, 7, "-", new_x="RIGHT")  # Using hyphen instead of bullet point

        # Handle text wrapping for bullet points
        wrapped_text = textwrap.wrap(text, width=60 - (level * 5))
        for i, wrap in enumerate(wrapped_text):
            if i == 0:
                self.cell(0, 7, wrap, new_x="LMARGIN", new_y="NEXT")
            else:
                self.set_x(indent + 5)  # Indent wrapped lines
                self.cell(0, 7, wrap, new_x="LMARGIN", new_y="NEXT")

        self.set_font("helvetica", size=12)  # Reset font

    def add_numbered_item(self, number, text, level=0):
        """Add a numbered list item with proper indentation"""
        # Process inline formatting
        text = self.process_inline_formatting(text)

        # Calculate indentation based on level
        indent = 10 + (level * 5)
        self.set_x(indent)

        self.set_font("helvetica", size=10)
        self.cell(8, 7, f"{number}.", new_x="RIGHT")

        # Handle text wrapping for numbered items
        wrapped_text = textwrap.wrap(text, width=58 - (level * 5))
        for i, wrap in enumerate(wrapped_text):
            if i == 0:
                self.cell(0, 7, wrap, new_x="LMARGIN", new_y="NEXT")
            else:
                self.set_x(indent + 8)  # Indent wrapped lines
                self.cell(0, 7, wrap, new_x="LMARGIN", new_y="NEXT")

        self.set_font("helvetica", size=12)  # Reset font

    def add_code_block(self, text):
        """Format and add a code block"""
        self.set_font("courier", size=8)  # Smaller monospace font for code

        # Save current settings
        old_fill_color = self.fill_color

        # Add a light gray background
        self.set_fill_color(240, 240, 240)  # Light gray

        # Add some padding before the code block
        self.ln(3)

        # Draw a border around the code block
        block_x = 10
        block_width = self.w - 20

        # Determine the height needed - each line is about 4mm high
        lines = text.split("\n")

        # Make sure lines aren't too long
        processed_lines = []
        for line in lines:
            # If line is too long, wrap it
            if len(line) > 80:
                wrapped = textwrap.wrap(line, width=80)
                processed_lines.extend(wrapped)
            else:
                processed_lines.append(line)

        # Set x position for the code block
        self.set_x(block_x)

        # Set text color slightly darker for better readability
        self.set_text_color(50, 50, 50)

        # Draw the code block
        for line in processed_lines:
            try:
                # Replace tabs with spaces for better rendering
                line = line.replace("\t", "    ")

                # Clean any problematic characters
                line = line.replace("\x0c", " ")  # Form feed

                # Ensure the line fits by truncating if necessary
                if len(line) > 80:
                    line = line[:77] + "..."

                # Draw the cell with text
                self.cell(
                    block_width, 5, line, fill=True, new_x="LMARGIN", new_y="NEXT"
                )
            except Exception as e:
                # If a line fails, skip it
                continue

        # Add padding after code block
        self.ln(3)

        # Restore normal text settings
        self.set_fill_color(old_fill_color[0], old_fill_color[1], old_fill_color[2])
        self.set_text_color(0, 0, 0)  # Reset to black
        self.set_font("helvetica", size=12)

    def add_blockquote(self, text):
        """Format and add a blockquote"""
        # Process inline formatting
        text = self.process_inline_formatting(text)

        self.set_font("helvetica", "I", 10)  # Italic for blockquotes

        # Indent blockquotes
        self.set_x(20)

        # Add left border
        self.set_draw_color(200, 200, 200)  # Light gray
        self.set_line_width(0.5)
        line_y = self.get_y()

        # Wrap and write the blockquote text
        wrapped_text = textwrap.wrap(text, width=50)
        for wrap in wrapped_text:
            if wrap:
                self.multi_cell(0, 5, wrap)

        # Draw vertical line
        end_y = self.get_y()
        self.line(18, line_y, 18, end_y)

        # Add spacing
        self.ln(3)

        # Reset settings
        self.set_draw_color(0, 0, 0)  # Black
        self.set_font("helvetica", size=12)

    def process_inline_formatting(self, text):
        """Process inline markdown formatting (bold, italic, links, code)"""
        # Handle formatting in the right order to avoid conflicts

        # First, handle inline code to protect it from other formatting
        inline_code_matches = MD_INLINE_CODE.findall(text)
        for match in inline_code_matches:
            text = text.replace(f"`{match}`", f"###CODE#{match}#CODE###")

        # Handle bold text
        bold_matches = MD_BOLD.findall(text)
        for match in bold_matches:
            # We will convert the markdown to special markers for later processing
            text = text.replace(f"**{match}**", f"###BOLD#{match}#BOLD###")

        # Handle italic text
        italic_matches = MD_ITALIC.findall(text)
        for match in italic_matches:
            # Only replace if it's not already part of a bold tag
            if f"###BOLD#{match}#BOLD###" not in text:
                text = text.replace(f"*{match}*", f"###ITALIC#{match}#ITALIC###")

        # Handle links
        link_matches = MD_LINK.findall(text)
        for link_text, link_url in link_matches:
            text = text.replace(
                f"[{link_text}]({link_url})", f"###LINK#{link_text}|{link_url}#LINK###"
            )

        return text

    def render_formatted_text(self, text):
        """Render text with inline formatting applied"""
        # Process different formatting elements
        formatted_segments = []

        # Start with the whole text
        remaining_text = text

        # Find all markers and their positions
        all_markers = []

        # Find all markers in the text
        marker_types = [
            ("###BOLD#", "#BOLD###", "bold"),
            ("###ITALIC#", "#ITALIC###", "italic"),
            ("###LINK#", "#LINK###", "link"),
            ("###CODE#", "#CODE###", "code"),
        ]

        for start_marker, end_marker, marker_type in marker_types:
            pos = 0
            while pos < len(remaining_text):
                start_pos = remaining_text.find(start_marker, pos)
                if start_pos == -1:
                    break

                end_pos = remaining_text.find(end_marker, start_pos + len(start_marker))
                if end_pos == -1:
                    break

                all_markers.append((start_pos, end_pos + len(end_marker), marker_type))
                pos = end_pos + len(end_marker)

        # Sort markers by their start position
        all_markers.sort(key=lambda x: x[0])

        # Process text based on markers
        last_pos = 0

        for start_pos, end_pos, marker_type in all_markers:
            # Add text before this marker
            if start_pos > last_pos:
                formatted_segments.append(
                    ("normal", remaining_text[last_pos:start_pos])
                )

            # Extract content based on marker type
            if marker_type == "bold":
                content = remaining_text[
                    start_pos + 8 : end_pos - 8
                ]  # Remove '###BOLD#' and '#BOLD###'
                formatted_segments.append(("bold", content))
            elif marker_type == "italic":
                content = remaining_text[
                    start_pos + 10 : end_pos - 10
                ]  # Remove '###ITALIC#' and '#ITALIC###'
                formatted_segments.append(("italic", content))
            elif marker_type == "link":
                content = remaining_text[
                    start_pos + 8 : end_pos - 8
                ]  # Remove '###LINK#' and '#LINK###'
                link_parts = content.split("|")
                if len(link_parts) == 2:
                    formatted_segments.append(("link", link_parts[0], link_parts[1]))
                else:
                    formatted_segments.append(("normal", content))
            elif marker_type == "code":
                content = remaining_text[
                    start_pos + 8 : end_pos - 8
                ]  # Remove '###CODE#' and '#CODE###'
                formatted_segments.append(("code", content))

            last_pos = end_pos

        # Add any remaining text
        if last_pos < len(remaining_text):
            formatted_segments.append(("normal", remaining_text[last_pos:]))

        try:
            # Render each segment with appropriate formatting
            for segment in formatted_segments:
                format_type = segment[0]

                if format_type == "normal":
                    self.write(5, segment[1])
                elif format_type == "bold":
                    current_style = self.font_style
                    self.set_font("helvetica", style="B")
                    self.write(5, segment[1])
                    self.set_font("helvetica", style=current_style)
                elif format_type == "italic":
                    current_style = self.font_style
                    self.set_font("helvetica", style="I")
                    self.write(5, segment[1])
                    self.set_font("helvetica", style=current_style)
                elif format_type == "link":
                    text, url = segment[1], segment[2]
                    current_color = self.text_color
                    self.set_text_color(self.link_blue)
                    # Make URLs shorter if they're too long
                    display_url = url
                    if len(url) > 30:
                        display_url = url[:27] + "..."
                    self.write(5, text + " (" + display_url + ")")
                    self.set_text_color(current_color)
                elif format_type == "code":
                    current_font = self.font_family
                    current_style = self.font_style
                    current_size = self.font_size
                    self.set_font("courier", size=current_size - 1)
                    self.write(5, segment[1])
                    self.set_font(current_font, style=current_style, size=current_size)
        except Exception as e:
            # If any rendering fails, fall back to simple text
            self.write(
                5,
                text.replace("###BOLD#", "")
                .replace("#BOLD###", "")
                .replace("###ITALIC#", "")
                .replace("#ITALIC###", "")
                .replace("###LINK#", "")
                .replace("#LINK###", "")
                .replace("###CODE#", "")
                .replace("#CODE###", ""),
            )


def create_pdf_from_markdown(markdown_file_path, output_dir=None):
    """
    Create a PDF from a markdown file.

    Args:
        markdown_file_path (str): Path to the markdown file
        output_dir (str, optional): Directory to save the PDF. Defaults to PDF_DIR.

    Returns:
        str: Path to the generated PDF file
    """
    # Create PDF directory if it doesn't exist
    if output_dir is None:
        output_dir = PDF_DIR

    os.makedirs(output_dir, exist_ok=True)

    # Read markdown file
    with open(markdown_file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Extract title from markdown file (first heading)
    title_match = re.search(r"^# (.*?)$", text, re.MULTILINE)
    title = (
        title_match.group(1)
        if title_match
        else os.path.basename(markdown_file_path).replace(".md", "")
    )

    # Get output file path
    output_filename = os.path.basename(markdown_file_path).replace(".md", ".pdf")
    output_path = os.path.join(output_dir, output_filename)

    # Replace all Unicode characters that might cause trouble
    unicode_replacements = {
        "—": " - ",
        "–": "-",
        """: '"',
        """: '"',
        "'": "'",
        "'": "'",
        "…": "...",
        "•": "-",  # Replace bullet points with hyphens
        "→": "->",
        "←": "<-",
        "↑": "^",
        "↓": "v",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "©": "(c)",
        "®": "(R)",
        "™": "(TM)",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY",
        "×": "x",
        "÷": "/",
        "µ": "u",
        "α": "alpha",
        "β": "beta",
        "γ": "gamma",
        "δ": "delta",
        "π": "pi",
        "σ": "sigma",
        "λ": "lambda",
        "θ": "theta",
        "φ": "phi",
        "Ω": "Omega",
    }

    for char, replacement in unicode_replacements.items():
        text = text.replace(char, replacement)

    # Replace problematic characters but preserve Portuguese accented chars
    pt_chars = {
        'á': 'á', 'à': 'à', 'ã': 'ã', 'â': 'â',
        'é': 'é', 'ê': 'ê', 
        'í': 'í', 
        'ó': 'ó', 'ô': 'ô', 'õ': 'õ',
        'ú': 'ú', 'ü': 'ü',
        'ç': 'ç',
        'Á': 'Á', 'À': 'À', 'Ã': 'Ã', 'Â': 'Â',
        'É': 'É', 'Ê': 'Ê',
        'Í': 'Í',
        'Ó': 'Ó', 'Ô': 'Ô', 'Õ': 'Õ',
        'Ú': 'Ú', 'Ü': 'Ü',
        'Ç': 'Ç'
    }
    
    # First replace non-Portuguese special characters
    for char, replacement in unicode_replacements.items():
        text = text.replace(char, replacement)
    
    # Create a function that preserves Portuguese-specific characters
    def clean_text(c):
        if c in pt_chars:
            return c  # Keep Portuguese characters as is
        if ord(c) < 128 or c.isspace():
            return c  # Keep ASCII and spaces
        return '?'  # Replace other characters
        
    # Apply the cleaning function
    text = ''.join(clean_text(c) for c in text)

    # Create PDF with proper dimensions
    pdf = PDF(title=title)
    pdf.set_title(title)
    pdf.set_author("Generated by PDF Tool")
    pdf.set_auto_page_break(auto=True, margin=15)  # Enable auto page break
    pdf.add_page()

    # Set font
    pdf.set_font("helvetica", size=12)

    # Manually parse and format the markdown content
    lines = text.split("\n")
    i = 0
    in_code_block = False
    code_content = []

    while i < len(lines):
        line = lines[i].rstrip()
        i += 1

        # Skip HTML comments
        if line.startswith("<!--") or (
            line.startswith("<") and line.endswith(">") and not line.startswith("<http")
        ):
            continue

        # Handle empty lines
        if not line:
            if not in_code_block:  # Only add spacing outside code blocks
                pdf.ln(5)
            continue

        # Handle code blocks
        if MD_CODE_BLOCK_START.match(line):
            in_code_block = True
            code_content = []
            continue
        elif MD_CODE_BLOCK_END.match(line) and in_code_block:
            in_code_block = False
            if code_content:
                pdf.add_code_block("\n".join(code_content))
            continue
        elif in_code_block:
            code_content.append(line)
            continue

        # Handle different markdown elements
        if MD_HEADING1.match(line):
            match = MD_HEADING1.match(line)
            pdf.add_heading(1, match.group(1))
        elif MD_HEADING2.match(line):
            match = MD_HEADING2.match(line)
            pdf.add_heading(2, match.group(1))
        elif MD_HEADING3.match(line):
            match = MD_HEADING3.match(line)
            pdf.add_heading(3, match.group(1))
        elif MD_HEADING4.match(line):
            match = MD_HEADING4.match(line)
            pdf.add_heading(4, match.group(1))
        elif MD_BULLET.match(line):
            match = MD_BULLET.match(line)

            # Determine indentation level based on leading spaces
            leading_spaces = len(lines[i - 1]) - len(lines[i - 1].lstrip())
            level = leading_spaces // 2  # Each indentation level is roughly 2 spaces

            pdf.add_bullet_point(match.group(1), level)
        elif MD_NUMBERED.match(line):
            match = MD_NUMBERED.match(line)

            # Determine indentation level based on leading spaces
            leading_spaces = len(lines[i - 1]) - len(lines[i - 1].lstrip())
            level = leading_spaces // 2

            pdf.add_numbered_item(match.group(1), match.group(2), level)
        elif MD_BLOCKQUOTE.match(line):
            match = MD_BLOCKQUOTE.match(line)
            pdf.add_blockquote(match.group(1))
        else:
            # Handle paragraphs, which can contain inline formatting
            pdf.add_paragraph(line)

    # Save PDF
    pdf.output(output_path)
    print(f"PDF successfully generated: {output_path}")
    return output_path


# Wrapper function to match the import in app.py
def generate_pdf_from_markdown(markdown_content, title=None, output_dir=None):
    """
    Generate a PDF from markdown content string.

    Args:
        markdown_content (str): The markdown content as a string
        title (str, optional): The title for the PDF. If None, will be extracted from markdown
        output_dir (str, optional): Directory to save the PDF. Defaults to PDF_DIR.

    Returns:
        str: Path to the generated PDF file
    """
    # Create a temporary markdown file
    import tempfile

    # Generate a filename based on the title or use a timestamp
    if title:
        filename = f"{title.replace(' ', '_')}.md"
    else:
        # Extract title from markdown content (first heading)
        title_match = re.search(r"^# (.*?)$", markdown_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            filename = f"{title.replace(' ', '_')}.md"
        else:
            # Use timestamp if no title found
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    # Determine the examples directory
    examples_dir = os.path.join(os.path.dirname(CURRENT_DIR), "examples")
    os.makedirs(examples_dir, exist_ok=True)

    # Save markdown content to the examples directory
    markdown_file_path = os.path.join(examples_dir, filename)
    with open(markdown_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # Generate the PDF from the markdown file
    output_path = create_pdf_from_markdown(markdown_file_path, output_dir)

    return output_path


# Add command-line interface for direct usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert Markdown file to PDF")
    parser.add_argument("markdown_file", help="Path to the markdown file")
    parser.add_argument("--output-dir", help="Directory to save the PDF")

    args = parser.parse_args()

    output_path = create_pdf_from_markdown(args.markdown_file, args.output_dir)
    print(f"PDF saved to: {output_path}")
