import logging
from crewai import Crew, Process
from storage import data_store
from agents import create_agents
from tasks import create_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_crew():
    generator, evaluator = create_agents()
    tasks = create_tasks(generator, evaluator, max_iterations=3)
    crew = Crew(agents=[generator, evaluator], tasks=tasks, process=Process.sequential, verbose=True)

    try:
        result = crew.kickoff()
        print("execution done")
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = run_crew()
    if data_store.current_data is not None:
        print("\nFinal output sample:")
        print(data_store.current_data.head())
        data_store.current_data.to_csv("employee_data_final.csv", index=False)
        print("Final dataset saved as employee_data_final.csv")
