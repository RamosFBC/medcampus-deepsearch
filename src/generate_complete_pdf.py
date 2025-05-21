import os
import re
from datetime import datetime
import base64
import markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

# Import from pdf_generator.py
from pdf_generator import (
    PDF_DIR,
    TEMPLATES_DIR,
    DEFAULT_CSS,
    generate_pdf_from_markdown,
    fig_to_base64,
)


def generate_complete_pdf(
    markdown_content, figures=None, title=None, subtitle=None, metadata=None
):
    """
    Generate a complete PDF report with markdown content, charts, and metadata.

    Args:
        markdown_content (str): The markdown content as a string
        figures (dict): Dictionary of Plotly figures to include
        title (str, optional): The title for the PDF
        subtitle (str, optional): The subtitle for the PDF
        metadata (dict, optional): Additional metadata to include in the report

    Returns:
        str: Path to the generated PDF file
    """
    # Create PDF directory if it doesn't exist
    os.makedirs(PDF_DIR, exist_ok=True)

    # Extract title from markdown content if not provided
    if not title:
        title_match = re.search(r"^# (.*?)$", markdown_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = "Relatório MedCampus"

    # Generate a filename based on the title
    filename = re.sub(r"[^\w\-_]", "_", title)
    output_path = os.path.join(PDF_DIR, f"{filename}.pdf")

    # Add metadata section to markdown if provided
    if metadata:
        metadata_section = ["## Metadados do Relatório", ""]
        for key, value in metadata.items():
            metadata_section.append(f"**{key}:** {value}")

        markdown_content += "\n\n" + "\n".join(metadata_section)

    # If figures provided as a dictionary, convert to list of chart objects
    charts = []
    if figures:
        for key, fig in figures.items():
            if fig:
                # Create a descriptive title from the key
                title_text = key.replace("_", " ").title()
                charts.append(
                    {
                        "title": title_text,
                        "figure": fig,
                        "description": f"{title_text} para {title}",
                    }
                )

    # Generate PDF with charts
    return generate_pdf_from_markdown(markdown_content, title=title, charts=charts)
