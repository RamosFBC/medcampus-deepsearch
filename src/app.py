import streamlit as st
import pandas as pd

from open_deep_research.multi_agent import graph
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


async def run_graph(initial_input):
    """Runs the graph asynchronously and prints the result."""
    # You might need to pass a config here if your graph expects it
    # e.g., config = {"configurable": {"search_api": "tavily", "supervisor_model": "your_model", "researcher_model": "your_model"}}
    result = await graph.ainvoke(initial_input)

    return result


data_path = "data/combined_table_cleaned.csv"
# Load the CSV file into a DataFrame
df = pd.read_csv(data_path)

# Map all specialties to a list
specialties = sorted(df["Especialidade"].unique().tolist())
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
        "Qual ciclo você está cursando?", options=["Básico", "Clínico" "Internato"]
    )
    especialidade = st.selectbox(
        "Qual especialidade você pensa em fazer?", options=specialties
    )
    local = st.selectbox("Qual local você pensa em fazer residência?", options=estados)
    preocupacoes = st.text_area(
        "Quais são suas preocupações ou dúvidas em relação à sua carreira médica?"
    )
    # Create a text input for the user to enter their prompt
    user_input = st.text_area(
        "Digite sua pergunta ou solicitação:", value=input_prompt, height=200
    )

    # Create a submit button
    if st.form_submit_button(label="Enviar"):
        # Display the user input
        st.write("Você digitou:")
        st.write(user_input)

        # Display the other inputs
        st.write("Faculdade:", faculdade)
        st.write("Ciclo:", ciclo)
        st.write("Especialidade:", especialidade)
        st.write("Local:", local)
        st.write("Preocupações:", preocupacoes)

        # Prepare the input for the agent
        initial_input = {
            "messages": [
                {
                    "role": "user",
                    "content": user_input.format(
                        especialidades=especialidade,
                        estado=local,
                        faculdade=faculdade,
                        preocupacoes=preocupacoes,
                    ),
                }
            ]
        }
        # Run the agent asynchronously
        result = asyncio.run(run_graph(initial_input))
        # Display the result
        st.write("Resultado:")
        st.write(result["final_report"])
        st.write(initial_input)
    specialty_data = df[df["Especialidade"] == especialidade]
    st.write(specialty_data)
# Display the DataFrame in Streamlit
if st.checkbox("debug"):
    st.dataframe(df)
