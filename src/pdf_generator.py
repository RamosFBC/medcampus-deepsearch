"""
Enhanced PDF generator for medical residency reporting system.
Uses WeasyPrint to generate high-quality PDFs with visualizations.
"""

import os
import re
from datetime import datetime
import base64
from io import BytesIO
import tempfile
from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "pdf")
TEMPLATES_DIR = os.path.join(CURRENT_DIR, "templates")

# Create templates directory if it doesn't exist
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# Default CSS styling
DEFAULT_CSS = (
    """
body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 210mm;
    margin: 0 auto;
    padding: 0 15mm;
}

h1, h2, h3, h4, h5, h6 {
    color: #1e5079;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h1 { 
    font-size: 24px; 
    text-align: center;
    margin-top: 2em;
    border-bottom: 2px solid #1e5079;
    padding-bottom: 10px;
}

h2 { font-size: 20px; color: #1e5079; }
h3 { font-size: 18px; color: #2a6496; }
h4 { font-size: 16px; color: #3a7ab2; }

p {
    margin-bottom: 1em;
    text-align: justify;
}

ul, ol {
    margin-bottom: 1em;
    padding-left: 2em;
}

li {
    margin-bottom: 0.5em;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
    color: #333;
}

tr:nth-child(even) {
    background-color: #f9f9f9;
}

img {
    display: block;
    margin: 1em auto;
    max-width: 100%;
}

.chart-container {
    width: 100%;
    margin: 20px 0;
    text-align: center;
}

.chart-title {
    font-weight: bold;
    color: #1e5079;
    margin-bottom: 10px;
    font-size: 16px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #ddd;
    margin-bottom: 20px;
}

.header img {
    height: 60px;
}

.header-right {
    text-align: right;
    font-size: 14px;
    color: #777;
}

.footer {
    border-top: 1px solid #ddd;
    padding-top: 10px;
    margin-top: 30px;
    font-size: 12px;
    color: #777;
    text-align: center;
}

.metric-card {
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
    margin: 10px 0;
    background-color: #f9f9f9;
}

.metric-title {
    font-size: 14px;
    color: #777;
    margin-bottom: 5px;
}

.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #1e5079;
}

.metric-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    margin: 20px 0;
}

code {
    background-color: #f5f5f5;
    padding: 2px 5px;
    border-radius: 3px;
    font-family: monospace;
}

blockquote {
    border-left: 4px solid #1e5079;
    padding-left: 15px;
    color: #555;
    font-style: italic;
    margin: 1em 0;
}

@page {
    margin: 25mm 20mm;
    @bottom-center {
        content: "Página " counter(page) " de " counter(pages);
        font-size: 10px;
        color: #777;
    }
    @bottom-right {
        content: "Gerado em: """
    + datetime.now().strftime("%d/%m/%Y")
    + """";
        font-size: 10px;
        color: #777;
    }
}
"""
)

# Create the base HTML template
BASE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        {{ css }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1>MedCampus</h1>
        </div>
        <div class="header-right">
            <p>Relatório gerado em: {{ date }}</p>
        </div>
    </div>
    
    <div class="content">
        {{ content }}
    </div>
    
    <div class="footer">
        <p>© {{ year }} MedCampus | Todos os direitos reservados</p>
    </div>
</body>
</html>
"""


def fig_to_base64(fig):
    """Convert a plotly figure to a base64 encoded image."""
    try:
        img_bytes = fig.to_image(format="png", width=800, height=500, scale=2)
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        # TEMPORARY FIX: Return a placeholder or dummy image if Kaleido fails
        print(f"Error converting figure to image: {e}")
        # Return a very small transparent PNG as fallback
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


def save_base_template():
    """Save the base template to the templates directory."""
    template_path = os.path.join(TEMPLATES_DIR, "base.html")
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(BASE_TEMPLATE)
    return template_path


def save_default_css():
    """Save the default CSS to the templates directory."""
    css_path = os.path.join(TEMPLATES_DIR, "default.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(DEFAULT_CSS)
    return css_path


def extract_charts_from_session():
    """Extract charts from Streamlit session state."""
    charts = []

    if "specialty_chart" in st.session_state:
        charts.append(
            {
                "title": "Evolução de Vagas de R1",
                "figure": st.session_state.specialty_chart,
                "description": "Gráfico mostrando a evolução do número de vagas de R1 ao longo dos anos.",
            }
        )

    if "comparison_chart" in st.session_state:
        charts.append(
            {
                "title": "Comparação com Especialidades Relacionadas",
                "figure": st.session_state.comparison_chart,
                "description": "Comparação do número de vagas com especialidades relacionadas.",
            }
        )

    if "specialist_chart" in st.session_state:
        charts.append(
            {
                "title": "Distribuição de Especialistas",
                "figure": st.session_state.specialist_chart,
                "description": "Distribuição geográfica e demográfica de especialistas.",
            }
        )

    return charts


def generate_chart_html(charts):
    """Generate HTML for charts."""
    chart_html = ""

    # TEMPORARY FIX: Return empty string if charts list is empty
    if not charts:
        return chart_html

    for chart in charts:
        try:
            img_base64 = fig_to_base64(chart["figure"])
            chart_html += f"""
            <div class="chart-container">
                <div class="chart-title">{chart['title']}</div>
                <img src="{img_base64}" alt="{chart['title']}">
                <p><em>{chart['description']}</em></p>
            </div>
            """
        except Exception as e:
            # If image generation fails, just add a note instead
            print(f"Error generating chart image: {e}")
            chart_html += f"""
            <div class="chart-container">
                <div class="chart-title">{chart['title']} (Imagem não disponível)</div>
                <p><em>{chart['description']}</em></p>
            </div>
            """

    return chart_html


def convert_markdown_to_html(markdown_content):
    """Convert markdown content to HTML."""
    # Use Python-Markdown to convert
    html_content = markdown.markdown(
        markdown_content,
        extensions=[
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.codehilite",
            "markdown.extensions.toc",
            "markdown.extensions.sane_lists",
        ],
    )
    return html_content


def generate_pdf_from_markdown(markdown_content, title=None, charts=None):
    """
    Generate a PDF from markdown content with embedded charts.

    Args:
        markdown_content (str): The markdown content as a string
        title (str, optional): The title for the PDF
        charts (list, optional): List of chart objects with title, figure and description

    Returns:
        str: Path to the generated PDF file
    """
    # Extract title from markdown if not provided
    if not title:
        title_match = re.search(r"^# (.*?)$", markdown_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
        else:
            title = f"Relatório {datetime.now().strftime('%d/%m/%Y')}"

    # Create output directory if it doesn't exist
    os.makedirs(PDF_DIR, exist_ok=True)

    # Create a clean filename from the title
    filename = re.sub(r"[^\w\-_]", "_", title)
    output_path = os.path.join(PDF_DIR, f"{filename}.pdf")

    # Convert markdown to HTML
    html_content = convert_markdown_to_html(markdown_content)

    # Extract charts from session state if not provided
    if not charts:
        charts = extract_charts_from_session()

    # Generate HTML for charts
    chart_html = generate_chart_html(charts)

    # Combine content and charts
    full_html_content = html_content

    # Insert charts at appropriate position (after the introduction)
    intro_end = html_content.find("</h2>", html_content.find("<h2"))
    if intro_end > -1:
        full_html_content = (
            html_content[: intro_end + 5] + chart_html + html_content[intro_end + 5 :]
        )
    else:
        # If no h2 found, append charts at the end
        full_html_content = html_content + chart_html

    # Save base template and CSS files
    save_base_template()
    css_path = save_default_css()

    # Prepare template data
    template_data = {
        "title": title,
        "content": full_html_content,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "year": datetime.now().year,
        "css": DEFAULT_CSS,
    }

    # Render template
    template = env.get_template("base.html")
    rendered_html = template.render(**template_data)

    # Create PDF using WeasyPrint with fallback
    try:
        html = HTML(string=rendered_html)
        css = CSS(string=DEFAULT_CSS)

        # Generate PDF
        html.write_pdf(output_path, stylesheets=[css])

        return output_path
    except Exception as e:
        # Log the error
        print(f"Error generating PDF with WeasyPrint: {e}")
        st.error(f"Error generating PDF: {e}")

        # Fallback: Save HTML file instead
        html_path = os.path.join(PDF_DIR, f"{filename}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)

        print(f"Fallback: HTML saved to {html_path}")
        return html_path


def convert_streamlit_fig_to_chart_object(fig, title, description):
    """
    Convert a Streamlit-rendered figure to a chart object for PDF generation.

    Args:
        fig (plotly.graph_objects.Figure): The plotly figure object
        title (str): The title of the chart
        description (str): A description of the chart

    Returns:
        dict: A chart object dictionary
    """
    return {"title": title, "figure": fig, "description": description}


def save_charts_to_session_state(chart_objects):
    """
    Save chart objects to session state for later use in PDF generation.

    Args:
        chart_objects (list): List of chart objects from convert_streamlit_fig_to_chart_object
    """
    for i, chart in enumerate(chart_objects):
        key_name = f"chart_{i}"
        st.session_state[key_name] = chart


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


def test_pdf_generation():
    """Test PDF generation with sample data."""
    markdown_content = """
# Relatório de Análise: Cardiologia

## Introdução

Este relatório apresenta uma análise detalhada sobre a especialidade médica de Cardiologia no Brasil, com foco na evolução do número de vagas de residência médica e na distribuição de especialistas pelo território nacional.

## Evolução das Vagas de Residência Médica

A especialidade de Cardiologia tem apresentado crescimento consistente no número de vagas de residência médica ao longo dos anos. Entre 2018 e 2024, observou-se um aumento significativo na oferta de vagas, especialmente nas regiões Sudeste e Sul do país.

## Distribuição de Especialistas

A distribuição de especialistas em Cardiologia pelo Brasil apresenta concentração significativa nos grandes centros urbanos, principalmente nas capitais e cidades com mais de 300 mil habitantes.

## Comparativo com Especialidades Relacionadas

Em comparação com outras especialidades da área clínica, a Cardiologia se destaca pelo número expressivo de especialistas e pela ampla oferta de programas de residência médica.

## Conclusões

A análise permite concluir que a Cardiologia é uma especialidade em expansão no Brasil, com tendência de crescimento no número de vagas de residência médica e de especialistas formados anualmente.
"""

    # Create sample chart objects
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=["2018", "2019", "2020", "2021", "2022", "2023", "2024"],
            y=[150, 165, 180, 195, 210, 230, 250],
            name="Vagas",
        )
    )
    fig1.update_layout(title="Evolução de Vagas R1 em Cardiologia")

    # Create comparison chart
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=[
                "Cardiologia",
                "Clínica Médica",
                "Endocrinologia",
                "Nefrologia",
                "Pneumologia",
            ],
            y=[250, 350, 120, 80, 90],
            name="Vagas",
        )
    )
    fig2.update_layout(title="Vagas por Especialidade")

    # Create distribution chart
    fig3 = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Distribuição por Região", "Distribuição por Área"),
    )

    # Add pie charts
    fig3.add_trace(
        go.Pie(
            labels=["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"],
            values=[55, 18, 15, 6, 6],
        ),
        row=1,
        col=1,
    )

    fig3.add_trace(
        go.Pie(
            labels=[
                "Capital",
                "Interior > 300k",
                "Interior 100k-300k",
                "Interior < 100k",
            ],
            values=[45, 30, 15, 10],
        ),
        row=1,
        col=2,
    )

    fig3.update_layout(title="Distribuição de Especialistas")

    # Create chart objects
    charts = [
        {
            "title": "Evolução de Vagas de R1 em Cardiologia",
            "figure": fig1,
            "description": "Gráfico mostrando a evolução do número de vagas de R1 ao longo dos anos.",
        },
        {
            "title": "Comparação com Especialidades Relacionadas",
            "figure": fig2,
            "description": "Comparação do número de vagas com especialidades relacionadas.",
        },
        {
            "title": "Distribuição de Especialistas em Cardiologia",
            "figure": fig3,
            "description": "Distribuição geográfica e demográfica de especialistas em Cardiologia.",
        },
    ]

    # Generate PDF
    output_path = generate_pdf_from_markdown(
        markdown_content, title="Análise de Cardiologia", charts=charts
    )
    print(f"PDF generated: {output_path}")
    return output_path


if __name__ == "__main__":
    test_pdf_generation()
