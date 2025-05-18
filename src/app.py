import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from open_deep_research.multi_agent import graph
from generate_pdf import generate_pdf_from_markdown
from inputs import input_prompt

import asyncio
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="Open Deep Research", page_icon=":guardsman:", layout="wide"
)
load_dotenv()
agent = graph
input_prompt = input_prompt

# Initialize session state variables
if "result" not in st.session_state:
    st.session_state.result = None
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False
if "report_info" not in st.session_state:
    st.session_state.report_info = {
        "especialidade": "",
        "local": "",
        "residents_number": 0,
        "growth": 0.0,  # Initialize as float
    }


async def run_graph(initial_input):
    """Runs the graph asynchronously and prints the result."""
    # You might need to pass a config here if your graph expects it
    # e.g., config = {"configurable": {"search_api": "tavily", "supervisor_model": "your_model", "researcher_model": "your_model"}}
    result = await graph.ainvoke(initial_input)

    return result


residents_number_path = "data/residents_1_n.csv"
residents_growth_path = "data/residency_growth_cleaned.csv"
# Load the CSV file into a DataFrame
residents_number_df = pd.read_csv(residents_number_path)
residents_growth_df = pd.read_csv(residents_growth_path)

specialties = sorted(residents_number_df["Especialidade"].unique().tolist())
estados = [
    "Paraná",
    "São Paulo",
    "Rio de Janeiro",
    "Minas Gerais",
    "Bahia",
    "Rio Grande do Sul",
    "Santa Catarina",
    "Ceará",
    "Pernambuco",
    "Pará",
    "Maranhão",
    "Goiás",
    "Espírito Santo",
    "Alagoas",
    "Sergipe",
    "Paraíba",
    "Rio Grande do Norte",
    "Tocantins",
    "Amapá",
    "Rondônia",
    "Acre",
    "Mato Grosso do Sul",
    "Mato Grosso",
    "Distrito Federal",
]

st.title("🎓 MedCampus")
st.subheader("Esteja preparado, esteja na frente.")

with st.form(key="input_form"):
    faculdade = st.text_input("Em qual faculdade você estuda?")
    ciclo = st.selectbox(
        "Qual ciclo você está cursando?", options=["Básico", "Clínico", "Internato"]
    )
    especialidade = st.selectbox(
        "Qual especialidade você pensa em fazer?", options=specialties
    )
    local = st.selectbox(
        "Em qual estado você pensa em fazer residência?", options=estados
    )
    preocupacoes = st.text_area(
        "Quais são suas preocupações ou dúvidas em relação à sua carreira médica?"
    )

    specialty_data = residents_number_df[
        residents_number_df["Especialidade"] == especialidade
    ]
    specialty_growth_data = residents_growth_df[
        residents_growth_df["Especialidade"] == especialidade
    ]

    residents_number = specialty_data["Medicos_residentes_total_N"].values[0]

    # Create a submit button
    if st.form_submit_button(label="Enviar"):

        # Prepare the input for the agent
        initial_input = {
            "messages": [
                {
                    "role": "user",
                    "content": input_prompt.format(
                        especialidades=especialidade,
                        estado=local,
                        faculdade=faculdade,
                        preocupacoes=preocupacoes,
                        ciclo=ciclo,
                    ),
                }
            ]
        }
        report_title = f"Relatório sobre {especialidade} em {local}"

        # Store report info in session state
        # Safely get the growth value with proper error handling
        try:
            if not specialty_growth_data.empty:
                growth_str = str(specialty_growth_data["crescimento_total"].values[0])
                # Handle potential formatting issues (commas, spaces, etc.)
                growth_str = growth_str.replace(',', '.').strip()
                # Remove any quotes or non-numeric characters except decimal point and minus sign
                growth_str = ''.join(c for c in growth_str if c.isdigit() or c in '.-')
                growth_value = float(growth_str)
            else:
                growth_value = 0.0
                
            # For debugging
            print(f"Growth value for {especialidade}: {growth_value}")
        except (ValueError, TypeError, IndexError) as e:
            print(f"Error processing growth value: {e}")
            growth_value = 0.0

        st.session_state.report_info = {
            "especialidade": especialidade,
            "local": local,
            "residents_number": residents_number,
            "growth": growth_value,
        }

        # Create a loading spinner with messages
        with st.spinner("Iniciando a geração do relatório..."):

            # Create a placeholder for progress messages
            progress_placeholder = st.empty()

            # Define loading messages to show while report is being generated
            loading_messages = [
                "Analisando dados sobre a especialidade...",
                "Avaliando cenário de residência médica...",
                "Processando informações sobre vagas e concorrência...",
                "Construindo recomendações personalizadas...",
                "Formatando relatório final...",
                "Quase pronto...",
            ]

            # Show each message for a moment to simulate progress
            import time

            # Show loading messages with a more reasonable delay
            for i, message in enumerate(loading_messages):
                # If it's the last message, keep it showing longer while the model works
                if i == len(loading_messages) - 1:
                    progress_placeholder.info(message)
                else:
                    progress_placeholder.info(message)
                    time.sleep(2)  # Show each message for 2 seconds

            # Run the agent asynchronously
            st.session_state.result = asyncio.run(run_graph(initial_input))
            st.session_state.report_generated = True

            # Clear the progress messages when done
            progress_placeholder.empty()

            # Show success message
            st.success("Relatório gerado com sucesso!")


# Function to reset session state
def reset_report():
    st.session_state.result = None
    st.session_state.report_generated = False
    st.session_state.report_info = {
        "especialidade": "",
        "local": "",
        "residents_number": 0,
        "growth": 0.0,  # Ensure this is a float
    }
    st.rerun()  # Use st.rerun() instead of st.experimental_rerun()


# Outside the form, check if a report has been generated
if st.session_state.report_generated and st.session_state.result:
    # Add a button to generate a new report
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Novo Relatório", on_click=reset_report):
            pass

    # Display summary in a card
    with st.container():
        st.subheader(
            f"Resumo: {st.session_state.report_info['especialidade']} em {st.session_state.report_info['local']}"
        )
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label=f"Médicos residentes na especialidade",
                value=f"{st.session_state.report_info['residents_number']}",
            )
        with col2:
            # Handle the growth value safely - convert to float first and handle potential errors
            try:
                growth_value = float(st.session_state.report_info["growth"])
                growth_display = f"{growth_value:.1f}%"
                
                # Set delta color for visualization (red for negative, green for positive)
                delta_color = "normal"
                if growth_value < 0:
                    delta_color = "inverse"  # Red for negative growth
                elif growth_value > 0:
                    delta_color = "normal"   # Green for positive growth
                    
                # Create delta value for the metric
                delta = f"{growth_value:.1f}% desde 2018"
                
            except (ValueError, TypeError):
                growth_display = f"{st.session_state.report_info['growth']}"
                delta = None
                delta_color = "off"

            st.metric(
                label=f"Taxa de crescimento",
                value=growth_display,
                delta=delta,
                delta_color=delta_color,
            )

    # Create a chart for the specialty growth
    st.subheader(f"Evolução de Vagas em {st.session_state.report_info['especialidade']} (2018-2024)")
    
    # Get the selected specialty data
    specialty = st.session_state.report_info['especialidade']
    specialty_history = residents_growth_df[residents_growth_df['Especialidade'] == specialty]
    
    if not specialty_history.empty:
        # Extract years and values for plotting
        years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
        values = specialty_history[years].values.flatten().tolist()
        
        # Create a DataFrame for plotting
        plot_df = pd.DataFrame({
            'Ano': years,
            'Vagas': values
        })
        
        # Calculate year-over-year growth percentages
        yoy_growth = []
        for i in range(1, len(values)):
            if values[i-1] > 0:  # Avoid division by zero
                pct_change = ((values[i] - values[i-1]) / values[i-1]) * 100
            else:
                pct_change = 0
            yoy_growth.append(pct_change)
        
        # Create the chart using Plotly
        fig = go.Figure()
        
        # Add bars for number of positions
        fig.add_trace(go.Bar(
            x=years,
            y=values,
            name='Vagas',
            marker_color='rgba(58, 71, 180, 0.8)'
        ))
        
        # Add line for growth trend
        fig.add_trace(go.Scatter(
            x=years[1:],
            y=values[1:],
            name='Tendência',
            line=dict(color='rgba(246, 78, 139, 1.0)', width=3),
            mode='lines'
        ))
        
        # Customize layout
        fig.update_layout(
            title=f'Evolução de Vagas em {specialty} (2018-2024)',
            title_font_size=18,
            xaxis_title='Ano',
            yaxis_title='Número de Vagas',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
            height=400,
        )
        
        # Add annotations for growth/decline
        growth = float(specialty_history['crescimento_total'].values[0])
        color = 'green' if growth >= 0 else 'red'
        
        fig.add_annotation(
            x=years[-1],
            y=values[-1],
            text=f"Crescimento Total: {growth:.1f}%",
            showarrow=True,
            arrowhead=1,
            arrowcolor=color,
            arrowsize=1,
            arrowwidth=2,
            bgcolor="white",
            bordercolor=color,
            borderwidth=2,
            borderpad=4,
            font=dict(color=color, size=12)
        )
        
        # Display the chart in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a small data table with yearly values
        st.caption("Dados Anuais")
        st.dataframe(plot_df.set_index('Ano').T.style.format("{:.0f}"))
    else:
        st.warning(f"Dados históricos não disponíveis para {specialty}")

    # Get the final report content
    final_report = st.session_state.result["final_report"]
    report_title = f"Relatório sobre {st.session_state.report_info['especialidade']} em {st.session_state.report_info['local']}"

    # Display the report in a nicely formatted container
    st.markdown("## Relatório Completo")
    report_container = st.container()
    with report_container:
        st.markdown(final_report)

    # Uncomment the PDF generation when ready to enable it
    # # Generate the PDF from the final report
    # pdf_path = generate_pdf_from_markdown(final_report, title=report_title)
    # # Provide a download link for the PDF
    # with open(pdf_path, "rb") as file:
    #     btn = st.download_button(
    #         label="Baixar PDF do Relatório",
    #         data=file,
    #         file_name=os.path.basename(pdf_path),
    #         mime="application/pdf",
    #     )
    # st.write(f"Relatório salvo em: {pdf_path}")

    # Add a comparison chart with related specialties
    st.subheader("Comparação com Outras Especialidades")
    
    specialty = st.session_state.report_info['especialidade']
    
    # Get the category of the specialty to find related ones
    # This is a simplified approach - in a real app you might have a more sophisticated categorization
    surgical_specialties = ['Cirurgia', 'Ortopedia', 'Neurocirurgia', 'Urologia', 'Otorrinolaringologia']
    clinical_specialties = ['Clínica', 'Medicina', 'Cardiologia', 'Pneumologia', 'Neurologia', 'Gastroenterologia']
    
    # Determine if this is a surgical or clinical specialty
    is_surgical = any(term in specialty for term in surgical_specialties)
    is_clinical = any(term in specialty for term in clinical_specialties)
    
    # Find related specialties
    related_specialties = []
    if is_surgical:
        # Find other surgical specialties
        for spec in residents_growth_df['Especialidade'].unique():
            if any(term in spec for term in surgical_specialties) and spec != specialty:
                related_specialties.append(spec)
    elif is_clinical:
        # Find other clinical specialties
        for spec in residents_growth_df['Especialidade'].unique():
            if any(term in spec for term in clinical_specialties) and spec != specialty:
                related_specialties.append(spec)
    
    # Select 2-4 related specialties
    if len(related_specialties) > 4:
        related_specialties = related_specialties[:4]
    
    # Create comparison dataframe
    specialties_to_compare = [specialty] + related_specialties
    comparison_data = []
    
    for spec in specialties_to_compare:
        spec_data = residents_growth_df[residents_growth_df['Especialidade'] == spec]
        if not spec_data.empty:
            growth = float(spec_data['crescimento_total'].values[0])
            comparison_data.append({
                'Especialidade': spec,
                'Crescimento (%)': growth
            })
    
    # Add the average growth as well
    avg_growth = residents_growth_df['crescimento_total'].astype(float).mean()
    comparison_data.append({
        'Especialidade': 'Média Nacional',
        'Crescimento (%)': avg_growth
    })
    
    # Create the comparison dataframe
    comparison_df = pd.DataFrame(comparison_data)
    
    # Plot the comparison chart
    if not comparison_df.empty:
        fig = px.bar(
            comparison_df, 
            x='Especialidade', 
            y='Crescimento (%)',
            color='Crescimento (%)',
            color_continuous_scale=['red', 'orange', 'green'],
            title='Comparação de Crescimento entre Especialidades (2018-2024)',
            height=400
        )
        
        fig.update_layout(
            xaxis_title='Especialidade',
            yaxis_title='Crescimento Total (%)',
            coloraxis_showscale=False,
            plot_bgcolor='rgba(240, 240, 240, 0.8)',
        )
        
        # Add a horizontal line for zero growth
        fig.add_shape(
            type="line", 
            x0=-0.5, 
            y0=0, 
            x1=len(comparison_df)-0.5, 
            y1=0,
            line=dict(color="black", width=1, dash="dash")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show a small data table with the values
        st.caption("Dados de Crescimento")
        formatted_df = comparison_df.set_index('Especialidade')
        st.dataframe(formatted_df.style.format({'Crescimento (%)': '{:.1f}%'}))
    
    # Add a divider before showing the debug input
    st.divider()
    st.caption("Detalhes da Consulta:")
    with st.expander("Ver entrada do sistema"):
        st.write(st.session_state.result.get("messages", []))
# Display the DataFrames in Streamlit for debugging
if st.checkbox("Debug Mode"):
    st.subheader("Dados sobre Residentes")
    st.dataframe(residents_number_df)

    st.subheader("Dados sobre Crescimento")
    st.dataframe(residents_growth_df)
