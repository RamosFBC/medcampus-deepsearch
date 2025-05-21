import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_specialty_growth_chart(specialty, specialty_history):
    """
    Create a chart showing the evolution of residency positions for a specialty from 2018-2024.

    Args:
        specialty (str): Name of the medical specialty
        specialty_history (DataFrame): DataFrame containing the specialty's historical data

    Returns:
        Figure: The Plotly figure object is both displayed in Streamlit and stored in session_state
    """
    if specialty_history.empty:
        st.warning(f"Dados históricos não disponíveis para {specialty}")
        return

    # Extract years and values for plotting
    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]
    values = specialty_history[years].values.flatten().tolist()

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame({"Ano": years, "Vagas": values})

    # Calculate year-over-year growth percentages
    yoy_growth = []
    for i in range(1, len(values)):
        if values[i - 1] > 0:  # Avoid division by zero
            pct_change = ((values[i] - values[i - 1]) / values[i - 1]) * 100
        else:
            pct_change = 0
        yoy_growth.append(pct_change)

    # Create the chart using Plotly with specific width to distribute data
    fig = go.Figure()

    # Calculate min and max for better scaling
    min_value = min(values) if values else 0
    max_value = max(values) if values else 100
    y_range = [0, max_value * 1.2]  # Add 20% padding to the top

    # Add bars for number of positions with proper spacing
    fig.add_trace(
        go.Bar(
            x=years,
            y=values,
            name="Vagas",
            marker_color="rgba(58, 71, 180, 0.6)",  # Adjusted transparency
            width=0.5,  # Slightly narrower bars for better spacing
        )
    )

    # Add line for growth trend
    fig.add_trace(
        go.Scatter(
            x=years,
            y=values,
            name="Tendência",
            line=dict(color="rgba(246, 78, 139, 1.0)", width=2),  # Thinner line
            mode="lines+markers",  # Add markers at data points
            marker=dict(
                size=6,
                color="rgba(246, 78, 139, 1.0)",
                line=dict(width=1, color="white"),
            ),
        )
    )

    # Customize layout
    fig.update_layout(
        title=f"Vagas de R1: {specialty} (2018-2024)",
        title_font_size=20,
        title_x=0.5,  # Center the title
        xaxis_title="Ano",
        yaxis_title="Número de Vagas R1",
        yaxis_range=y_range,  # Apply calculated range
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12),
        ),
        plot_bgcolor="white",  # White background for cleaner look
        paper_bgcolor="white",  # White paper background
        height=400,
        # Improve x-axis with better distribution
        xaxis=dict(
            tickmode="array",
            tickvals=years,
            ticktext=years,
            tickangle=0,
            type="category",  # Use category type to ensure even spacing
            gridcolor="rgba(240, 240, 240, 0.8)",  # Light grid lines
            showgrid=True,  # Show grid
            rangeslider=dict(  # Add range slider for interactive exploration
                visible=False
            ),
            constrain="domain",  # This helps with spacing
        ),
        # Improve y-axis with better range distribution
        yaxis=dict(
            gridcolor="rgba(240, 240, 240, 0.8)",  # Light grid lines
            showgrid=True,  # Show grid
            rangemode="tozero",  # Start y-axis at zero
            automargin=True,  # Add margin as needed
            fixedrange=False,  # Allow zooming
        ),
        # Add margin for better spacing
        margin=dict(l=60, r=40, t=80, b=40),  # Increased left margin for y-axis labels
    )

    # # Add annotations for growth/decline
    # growth = float(specialty_history["crescimento_total"].values[0])
    # color = "green" if growth >= 0 else "red"

    # # Add a box annotation at the top of the chart for growth
    # fig.add_annotation(
    #     x=0.5,  # Center of the chart
    #     y=1.05,  # Just above the chart
    #     xref="paper",
    #     yref="paper",
    #     text=f"Crescimento Total: {growth:.1f}%",
    #     showarrow=True,
    #     arrowhead=2,
    #     arrowcolor=color,
    #     arrowsize=1,
    #     arrowwidth=2,
    #     ax=0,  # Make arrow point straight down
    #     ay=30,  # Length of the arrow
    #     bgcolor="white",
    #     bordercolor=color,
    #     borderwidth=2,
    #     borderpad=4,
    #     font=dict(color=color, size=12),
    #     align="center",
    # )

    # Store the figure in session_state for PDF generation
    if "figures" not in st.session_state:
        st.session_state.figures = {}

    # Store the chart with a descriptive key
    st.session_state.figures["specialty_growth_chart"] = fig

    # Display the chart in Streamlit with full width to prevent condensing
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True, "responsive": True},
    )

    # Add a small data table with yearly values - with expandable container
    with st.expander("Ver Dados Anuais"):
        st.dataframe(
            plot_df.set_index("Ano").T.style.format("{:.0f}"), use_container_width=True
        )

    return fig


def create_specialties_comparison_chart(specialty, residents_growth_df):
    """
    Create a comparison chart showing growth rates of the selected specialty and related ones.

    Args:
        specialty (str): The selected medical specialty
        residents_growth_df (DataFrame): DataFrame containing growth data for all specialties

    Returns:
        None: Displays the chart and data table directly in Streamlit
    """
    # Get the category of the specialty to find related ones
    # This is a simplified approach - in a real app you might have a more sophisticated categorization
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

    # Determine if this is a surgical or clinical specialty
    is_surgical = any(term in specialty for term in surgical_specialties)
    is_clinical = any(term in specialty for term in clinical_specialties)

    # Find related specialties
    related_specialties = []
    if is_surgical:
        # Find other surgical specialties
        for spec in residents_growth_df["Especialidade"].unique():
            if any(term in spec for term in surgical_specialties) and spec != specialty:
                related_specialties.append(spec)
    elif is_clinical:
        # Find other clinical specialties
        for spec in residents_growth_df["Especialidade"].unique():
            if any(term in spec for term in clinical_specialties) and spec != specialty:
                related_specialties.append(spec)

    # Select 2-4 related specialties
    if len(related_specialties) > 4:
        related_specialties = related_specialties[:4]

    # Create comparison dataframe
    specialties_to_compare = [specialty] + related_specialties
    comparison_data = []

    for spec in specialties_to_compare:
        spec_data = residents_growth_df[residents_growth_df["Especialidade"] == spec]
        if not spec_data.empty:
            growth = float(spec_data["crescimento_total"].values[0])
            comparison_data.append({"Especialidade": spec, "Crescimento (%)": growth})

    # Add the average growth as well
    avg_growth = residents_growth_df["crescimento_total"].astype(float).mean()
    comparison_data.append(
        {"Especialidade": "Média Nacional", "Crescimento (%)": avg_growth}
    )

    # Create the comparison dataframe
    comparison_df = pd.DataFrame(comparison_data)

    # Plot the comparison chart
    if not comparison_df.empty:
        fig = px.bar(
            comparison_df,
            x="Especialidade",
            y="Crescimento (%)",
            color="Crescimento (%)",
            color_continuous_scale=["red", "orange", "green"],
            title="Crescimento de Vagas R1 por Especialidade",
            height=400,
        )

        fig.update_layout(
            xaxis_title="Especialidade",
            yaxis_title="Crescimento de Vagas R1 (%)",
            coloraxis_showscale=False,
            plot_bgcolor="rgba(240, 240, 240, 0.8)",
            # Improve axis display
            xaxis=dict(
                tickangle=45,  # Angle labels for better readability with long names
                type="category",  # Use category type for better spacing
            ),
            # Add margin for better spacing
            margin=dict(
                l=40, r=20, t=60, b=80
            ),  # Increase bottom margin for angled labels
        )

        # Add a horizontal line for zero growth
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=0,
            x1=len(comparison_df) - 0.5,
            y1=0,
            line=dict(color="black", width=1, dash="dash"),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show a small data table with the values
        st.caption("Dados de Crescimento")
        formatted_df = comparison_df.set_index("Especialidade")
        st.dataframe(formatted_df.style.format({"Crescimento (%)": "{:.1f}%"}))
    else:
        st.warning(
            "Não foi possível encontrar especialidades relacionadas para comparação."
        )
