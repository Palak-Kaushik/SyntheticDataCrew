from crewai import Agent
from crewai.llm import LLM
from config import GEMINI_API_KEY
from tools.data_generator import generate_synthetic_data, update_data_based_on_feedback
from tools.data_evaluator import evaluate_data_quality, provide_improvement_suggestions

llm = LLM(model="gemini/gemini-2.0-flash-lite", api_key=GEMINI_API_KEY)

def create_agents():
    generator_agent = Agent(
        role="Data Generator",
        goal="Generate synthetic employee data and improve generated datawith feedback",
        backstory="synthetic data generator",
        tools=[generate_synthetic_data, update_data_based_on_feedback],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    evaluator_agent = Agent(
        role="Data Evaluator",
        goal="Evaluate synthetic data quality and provide feedback",
        backstory="data quality evaluator",
        tools=[evaluate_data_quality, provide_improvement_suggestions],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )
    return generator_agent, evaluator_agent
