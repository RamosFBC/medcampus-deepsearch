from open_deep_research.multi_agent import graph
import asyncio
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

agent = graph

input_prompt = """
Gere um guia de planejamento de carreira médica e preparação para residência. O guia deve cobrir as seguintes especialidades: Cardiologia, Cirurgia do Aparelho Digestivo.

Por favor, inclua informações relevantes sobre bem como análise comparativa caso haja duas ou mais especialidades:
- Quantidade de vagas e concorrência para residência médica nas especialidades indicadas.
- Instituições de referência e programas de destaque para a residência médica.
- Perspectivas de mercado de trabalho para médicos especialistas nas áreas escolhidas, incluindo remuneração média.
- Requisitos para a aprovação na residência, como provas, entrevistas e currículo, considerando o ano de realização da prova 2027.
- Com foco na região de Curitiba, Paraná e considerando o contexto para estudantes da FEMPAR.

 """

initial_input = {"messages": [{"role": "user", "content": input_prompt}]}


async def run_graph():
    """Runs the graph asynchronously and prints the result."""
    # You might need to pass a config here if your graph expects it
    # e.g., config = {"configurable": {"search_api": "tavily", "supervisor_model": "your_model", "researcher_model": "your_model"}}
    # result = await graph.ainvoke(initial_input, config=config)
    # result = await graph.ainvoke(initial_input)

    # print(result)

    data_path = "data/combined_table_cleaned.csv"
    df = pd.read_csv(data_path)
    print(df.head())


if __name__ == "__main__":
    asyncio.run(run_graph())
