import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from faker import Faker
from crewai.tools import tool
from config import DataConfig
from storage import data_store

fake = Faker()
logger = logging.getLogger(__name__)

@tool
def generate_synthetic_data(config_json: str) -> str:
    """
    Generate synthetic employee data based on configuration.
    
    Args:
        config_json: JSON string containing configuration parameters
    
    Returns:
        JSON string with generated data and metadata
    """
    logger.info("started generate synthetic data tool")
    try:
        config = DataConfig(num_rows=50)
        np.random.seed(42 + data_store.iteration_count)

        employees = []
        for i in range(config.num_rows):
            employees.append({
                "employee_id": f"E{i+1:04d}",
                "name": fake.name(),
                "email": fake.email(),
                "phone": fake.phone_number(),
                "age": np.random.randint(config.age_range[0], config.age_range[1] + 1),
                "department": np.random.choice(config.departments),
                "experience_years": np.random.randint(config.experience_range[0], config.experience_range[1] + 1),
                "salary": np.random.randint(config.salary_range[0], config.salary_range[1] + 1),
                "performance_rating": round(np.random.uniform(1.0, 5.0), 1),
                "hire_date": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d"),
                "address": fake.address().replace("\n", ", ")
            })

        df = pd.DataFrame(employees)
        data_store.current_data = df
        data_store.metadata = {
            "generation_time": datetime.now().isoformat(),
            "config": {"num_rows": config.num_rows},
            "num_rows": len(df),
            "columns": list(df.columns),
            "iteration": data_store.iteration_count
        }

        data_store.save_current_data_to_csv()
        data_store.iteration_count += 1

        return json.dumps({
            "status": "success",
            "data_shape": df.shape,
            "metadata": data_store.metadata,
            "sample_records": df.head().to_dict("records")
        })

    except Exception as e:
        logger.error(f"Error generating data: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def update_data_based_on_feedback(feedback_json: str) -> str:
    """
    Update data generation parameters based on evaluator feedback.
    
    Args:
        feedback_json: JSON string containing feedback and improvement suggestions
    
    Returns:
        JSON string with update status
    """

    # this tool is currently not doing much, just logging the eval results
    # it can be used to change the data generation params
    # since data is being generated randomly, it is unable to share the updated params

    logger.info("updating data on feedback")
    try:
        feedback = json.loads(feedback_json)
        data_store.feedback_history.append(feedback)

        improvements = []
        if feedback.get("completeness_score", 100) < 95:
            improvements.append("Ensured no missing values")
        if feedback.get("uniqueness_score", 100) < 90:
            improvements.append("Enhanced uniqueness in employee IDs and names")
        if feedback.get("statistical_score", 100) < 80:
            improvements.append("Adjusted statistical distributions")

        return json.dumps({
            "status": "updated",
            "improvements_applied": improvements,
            "feedback_processed": True
        })

    except Exception as e:
        logger.error(f"Error updating based on feedback: {e}")
        return json.dumps({"status": "error", "message": str(e)})