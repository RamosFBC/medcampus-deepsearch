import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np


def create_specialist_visualization(specialty, specialty_data_df):
    """
    Create visualizations for the specialist data distribution for a specialty.

    Args:
        specialty (str): Name of the medical specialty
        specialty_data_df (DataFrame): DataFrame containing the specialist data

    Returns:
        None: Displays the charts directly in Streamlit
    """
    # Filter data for the selected specialty
    specialty_row = specialty_data_df[specialty_data_df["especialidade"] == specialty]

    if specialty_row.empty:
        st.warning(f"Dados de especialistas não disponíveis para {specialty}")
        return

    # Extract data for the specialty
    n_specialists = int(specialty_row["n_especialistas"].values[0])
    specialists_per_100k = float(specialty_row["especialistas_100k"].values[0])

    # Create a container for the first set of visualizations
    st.subheader(f"Distribuição de Especialistas: {specialty}")

    # Create metrics columns
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Total de Especialistas no Brasil",
            value=f"{n_specialists:,}".replace(
                ",", "."
            ),  # Format with dots for thousands
            help="Número total de especialistas registrados no Brasil",
        )
    with col2:
        st.metric(
            label="Especialistas por 100 mil habitantes",
            value=f"{specialists_per_100k:.2f}",
            help="Densidade de especialistas por 100 mil habitantes no Brasil",
        )

    # Create subplots for regional distributions
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "domain"}, {"type": "domain"}]],
        subplot_titles=("Distribuição por Região", "Distribuição por Área"),
        horizontal_spacing=0.1,
    )

    # Add regional distribution (pie chart)
    region_labels = ["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"]
    region_values = [
        float(specialty_row["sudeste (%)"].values[0]),
        float(specialty_row["sul (%)"].values[0]),
        float(specialty_row["nordeste (%)"].values[0]),
        float(specialty_row["norte (%)"].values[0]),
        float(specialty_row["centro_oeste (%)"].values[0]),
    ]

    # Custom colors for regions
    region_colors = ["#4C78A8", "#72B7B2", "#F58518", "#E45756", "#54A24B"]

    fig.add_trace(
        go.Pie(
            labels=region_labels,
            values=region_values,
            textinfo="label+percent",
            insidetextorientation="radial",
            pull=[0.05, 0, 0, 0, 0],  # Emphasize the largest region
            marker=dict(colors=region_colors),
            textfont=dict(size=12, color="white"),
        ),
        row=1,
        col=1,
    )

    # Add urban/rural distribution (pie chart)
    area_labels = [
        "Capital",
        "Interior > 300k",
        "Interior 100k-300k",
        "Interior < 100k",
    ]
    area_values = [
        float(specialty_row["capital (%)"].values[0]),
        float(specialty_row["interior_mais_300k (%)"].values[0]),
        float(specialty_row["interior_100k_300k (%)"].values[0]),
        float(specialty_row["interior_menos_100k (%)"].values[0]),
    ]

    # Custom colors for urban/rural areas
    area_colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]

    fig.add_trace(
        go.Pie(
            labels=area_labels,
            values=area_values,
            textinfo="label+percent",
            insidetextorientation="radial",
            pull=[0.05, 0, 0, 0],  # Emphasize capital
            marker=dict(colors=area_colors),
            textfont=dict(size=12, color="white"),
        ),
        row=1,
        col=2,
    )

    # Update layout with nice styling
    fig.update_layout(
        height=500,
        legend_title_text="Distribuição",
        font=dict(family="Arial", size=14),
        title_text=f"Distribuição dos {n_specialists:,} Especialistas em {specialty}".replace(
            ",", "."
        ),
        title_x=0.2,
        paper_bgcolor="white",
        plot_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Create a bar chart comparison with similar specialties
    create_specialists_comparison(specialty, specialty_data_df)


def create_specialists_comparison(specialty, specialty_data_df):
    """
    Create a comparison chart showing the number of specialists across related specialties.

    Args:
        specialty (str): The selected medical specialty
        specialty_data_df (DataFrame): DataFrame containing data for all specialties

    Returns:
        None: Displays the chart directly in Streamlit
    """
    # Define specialty categories for grouping
    surgical_specialties = [
        "Cirurgia",
        "Ortopedia",
        "Neurocirurgia",
        "Urologia",
        "Otorrinolaringologia",
    ]
    clinical_specialties = [
        "Clínica",
        "Medicina",
        "Cardiologia",
        "Pneumologia",
        "Neurologia",
        "Gastroenterologia",
    ]

    # Determine category based on specialty name
    is_surgical = any(term in specialty for term in surgical_specialties)
    is_clinical = any(term in specialty for term in clinical_specialties)

    # Find related specialties
    related_specialties = []
    if is_surgical:
        for spec in specialty_data_df["especialidade"].unique():
            if any(term in spec for term in surgical_specialties) and spec != specialty:
                related_specialties.append(spec)
    elif is_clinical:
        for spec in specialty_data_df["especialidade"].unique():
            if any(term in spec for term in clinical_specialties) and spec != specialty:
                related_specialties.append(spec)

    # Limit to 5 related specialties (plus the selected one)
    if len(related_specialties) > 5:
        related_specialties = related_specialties[:5]

    specialties_to_compare = [specialty] + related_specialties
    comparison_data = []

    # Extract data for comparison
    for spec in specialties_to_compare:
        spec_data = specialty_data_df[specialty_data_df["especialidade"] == spec]
        if not spec_data.empty:
            n_specialists = int(spec_data["n_especialistas"].values[0])
            per_100k = float(spec_data["especialistas_100k"].values[0])
            comparison_data.append(
                {
                    "Especialidade": spec,
                    "Número de Especialistas": n_specialists,
                    "Por 100 mil habitantes": per_100k,
                }
            )

    # Create comparison dataframe
    comparison_df = pd.DataFrame(comparison_data)

    # Only proceed if we have comparison data
    if not comparison_df.empty:
        # Create two bar charts side by side
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=(
                "Número total de especialistas",
                "Especialistas por 100 mil habitantes",
            ),
            specs=[[{"type": "bar"}, {"type": "bar"}]],
            horizontal_spacing=0.1,
        )

        # First bar chart - Total number of specialists
        fig.add_trace(
            go.Bar(
                x=comparison_df["Especialidade"],
                y=comparison_df["Número de Especialistas"],
                marker_color=[
                    "#1F77B4" if x == specialty else "#7F7F7F"
                    for x in comparison_df["Especialidade"]
                ],
                text=comparison_df["Número de Especialistas"].apply(
                    lambda x: f"{x:,}".replace(",", ".")
                ),
                textposition="auto",
            ),
            row=1,
            col=1,
        )

        # Second bar chart - Specialists per 100k
        fig.add_trace(
            go.Bar(
                x=comparison_df["Especialidade"],
                y=comparison_df["Por 100 mil habitantes"],
                marker_color=[
                    "#1F77B4" if x == specialty else "#7F7F7F"
                    for x in comparison_df["Especialidade"]
                ],
                text=comparison_df["Por 100 mil habitantes"].apply(
                    lambda x: f"{x:.2f}"
                ),
                textposition="auto",
            ),
            row=1,
            col=2,
        )

        # Update layout
        fig.update_layout(
            title_text="Comparação com Especialidades Relacionadas",
            title_x=0.2,
            height=500,
            showlegend=False,
            font=dict(family="Arial", size=14),
            plot_bgcolor="white",
        )

        # Update y-axes
        fig.update_yaxes(title_text="Número de Especialistas", row=1, col=1)
        fig.update_yaxes(title_text="Por 100 mil habitantes", row=1, col=2)

        # Update x-axes with angled labels for better readability
        fig.update_xaxes(tickangle=45, row=1, col=1)
        fig.update_xaxes(tickangle=45, row=1, col=2)

        st.plotly_chart(fig, use_container_width=True)

        # Add a small data table with the values as an expandable container
        with st.expander("Ver Dados Comparativos"):
            formatted_df = comparison_df.set_index("Especialidade")

            # Use a custom formatter function for brazilian number format
            def format_number(x):
                return f"{x:,.0f}".replace(",", ".")

            st.dataframe(
                formatted_df.style.format(
                    {
                        "Número de Especialistas": format_number,
                        "Por 100 mil habitantes": "{:.2f}",
                    }
                ),
                use_container_width=True,
            )
    else:
        st.warning(
            "Não foi possível encontrar especialidades relacionadas para comparação."
        )
