from crewai import Task
from storage import data_store
from tools.data_generator import generate_synthetic_data, update_data_based_on_feedback
from tools.data_evaluator import evaluate_data_quality, provide_improvement_suggestions

def create_tasks(generator_agent, evaluator_agent, max_iterations=3):
    tasks = []
    for i in range(max_iterations):
        gen_task = Task(
            description=f"Generate synthetic employee data (iteration {i+1})",
            expected_output="Synthetic employee dataset",
            agent=generator_agent,
            tools=[generate_synthetic_data, update_data_based_on_feedback]
        )
        eval_task = Task(
            description=f"Evaluate data from iteration {i+1}",
            expected_output="Quality metrics and feedback",
            agent=evaluator_agent,
            tools=[evaluate_data_quality, provide_improvement_suggestions]
        )
        tasks.extend([gen_task, eval_task])
        if i < max_iterations - 1:
            fb_task = Task(
                description="Process feedback and prepare for next iteration",
                expected_output="Feedback processed",
                agent=generator_agent,
                tools=[update_data_based_on_feedback]
            )
            tasks.append(fb_task)
    return tasks
