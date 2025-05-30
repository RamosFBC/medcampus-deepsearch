import streamlit as st
import pandas as pd
import numpy as np
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from open_deep_research.multi_agent import graph
from pdf_generator import generate_complete_pdf
from inputs import input_prompt
from plot import create_specialty_growth_chart, create_specialties_comparison_chart
from plot_specialists import create_specialist_visualization

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
specialty_data_path = "data/specialty_data.csv"

# Load the CSV files into DataFrames
residents_number_df = pd.read_csv(residents_number_path)
residents_growth_df = pd.read_csv(residents_growth_path)
specialty_data_df = pd.read_csv(specialty_data_path)

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
                growth_str = growth_str.replace(",", ".").strip()
                # Remove any quotes or non-numeric characters except decimal point and minus sign
                growth_str = "".join(c for c in growth_str if c.isdigit() or c in ".-")
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
                    delta_color = "normal"  # Green for positive growth

                # Create delta value for the metric
                delta = f"{growth_value:.1f}% desde 2018"

            except (ValueError, TypeError):
                growth_display = f"{st.session_state.report_info['growth']}"
                delta = None
                delta_color = "off"

            st.metric(
                label=f"Crescimento de Vagas R1",
                value=growth_display,
                delta=delta,
                delta_color=delta_color,
            )

    # Create a chart for the specialty growth
    st.subheader(f"Vagas de R1: {st.session_state.report_info['especialidade']}")

    # Get the selected specialty data
    specialty = st.session_state.report_info["especialidade"]
    specialty_history = residents_growth_df[
        residents_growth_df["Especialidade"] == specialty
    ]

    # Create and display the specialty growth chart using the imported function
    create_specialty_growth_chart(specialty, specialty_history)

    # Add a divider before the specialist visualization section
    st.divider()

    # Create and display the specialist distribution visualization
    create_specialist_visualization(specialty, specialty_data_df)

    # Add a divider after the specialist visualization
    st.divider()

    # Get the final report content
    final_report = st.session_state.result["final_report"]
    report_title = f"Relatório sobre {st.session_state.report_info['especialidade']} em {st.session_state.report_info['local']}"

    # Display the report in a nicely formatted container
    st.markdown("## Relatório Completo")
    report_container = st.container()
    with report_container:
        st.markdown(final_report)

    # All charts are now stored directly in session_state.figures from our updated visualization functions

    # Generate PDF with charts
    from pdf_generator import generate_complete_pdf

    # TEMPORARY FIX: Use empty figures dictionary to bypass Kaleido errors
    # Original code:
    # figures = st.session_state.figures if "figures" in st.session_state else {}
    figures = {}  # Empty dictionary to bypass image handling

    # Generate the PDF from the final report with metadata
    metadata = {
        "Especialidade": st.session_state.report_info["especialidade"],
        "Região": st.session_state.report_info["local"],
        "Data de Geração": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Fonte de Dados": "MedCampus - Sistema de Análise de Residência Médica",
    }

    # Generate PDF with enhanced styling
    subtitle = f"Análise da Residência Médica em {st.session_state.report_info['especialidade']}"
    pdf_path = generate_complete_pdf(
        markdown_content=final_report,
        figures=figures,
        title=report_title,
        subtitle=subtitle,
        metadata=metadata,
    )

    # Provide a download link for the PDF
    with open(pdf_path, "rb") as file:
        btn = st.download_button(
            label="Baixar PDF do Relatório",
            data=file,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf",
        )
    # st.write(f"Relatório salvo em: {pdf_path}")

    # # Add a comparison chart with related specialties
    # st.subheader("Crescimento Comparativo de Vagas R1")

    # specialty = st.session_state.report_info["especialidade"]

    # # Create and display the specialties comparison chart using the imported function
    # create_specialties_comparison_chart(specialty, residents_growth_df)

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
