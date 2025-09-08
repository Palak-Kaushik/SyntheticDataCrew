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
    Update data generation parameters based on evaluator feedback and regenerate improved data.
    
    Args:
        feedback_json: JSON string containing feedback and improvement suggestions
    
    Returns:
        JSON string with update status
    """
    logger.info("updating data based on feedback")
    try:
        feedback = json.loads(feedback_json)
        data_store.feedback_history.append(feedback)
        
        if data_store.current_data is None:
            return json.dumps({"status": "error", "message": "No current data to improve"})
        
        df = data_store.current_data.copy()
        improvements = []

        # --- Extract feedback scores ---
        completeness_score = feedback.get("completeness_score", 100)
        uniqueness_score = feedback.get("uniqueness_score", 100)
        statistical_score = feedback.get("statistical_score", 100)

        # --- Apply modular improvements ---
        if completeness_score < 95:
            df, fix_notes = fix_completeness_issues(df)
            improvements.extend(fix_notes)

        if uniqueness_score < 100:
            df, fix_notes = fix_uniqueness_issues(df)
            improvements.extend(fix_notes)

        if statistical_score < 80:
            df, fix_notes = fix_statistical_issues(df)
            improvements.extend(fix_notes)

        # --- Save updated data ---
        data_store.current_data = df
        improved_filename = f"./data/employee_data_improved_iteration_{data_store.iteration_count - 1}.csv"
        df.to_csv(improved_filename, index=False)
        data_store.all_versions.append(improved_filename)

        logger.info(f"Applied {len(improvements)} improvements to data")
        
        return json.dumps({
            "status": "updated",
            "improvements_applied": improvements,
            "feedback_processed": True,
            "improved_file": improved_filename,
            "new_correlation": df['salary'].corr(df['experience_years']),
            "completeness_check": df.isnull().sum().sum() == 0,
            "unique_ids_check": df['employee_id'].nunique() == len(df)
        })
    
    except Exception as e:
        logger.error(f"Error updating based on feedback: {e}")
        return json.dumps({"status": "error", "message": str(e)})


# ---------- Helper Functions ----------

def fix_completeness_issues(df):
    """Fill in missing values with realistic defaults or synthetic data."""
    improvements = []
    missing_cols = df.columns[df.isnull().any()].tolist()

    for col in missing_cols:
        if col == 'age':
            df[col].fillna(np.random.randint(22, 66), inplace=True)
        elif col == 'salary':
            df[col].fillna(np.random.randint(30000, 150001), inplace=True)
        elif col == 'experience_years':
            df[col].fillna(np.random.randint(0, 31), inplace=True)
        elif col == 'performance_rating':
            df[col].fillna(round(np.random.uniform(1.0, 5.0), 1), inplace=True)
        elif col == 'department':
            departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']
            df[col].fillna(np.random.choice(departments), inplace=True)
        elif col in ['name', 'email', 'phone', 'address']:
            num_missing = df[col].isnull().sum()
            if col == 'name':
                df[col].fillna([fake.name() for _ in range(num_missing)], inplace=True)
            elif col == 'email':
                df[col].fillna([fake.email() for _ in range(num_missing)], inplace=True)
            elif col == 'phone':
                df[col].fillna([fake.phone_number() for _ in range(num_missing)], inplace=True)
            elif col == 'address':
                df[col].fillna([fake.address().replace('\n', ', ') for _ in range(num_missing)], inplace=True)

    if missing_cols:
        improvements.append("Fixed missing values in data")
    return df, improvements


def fix_uniqueness_issues(df):
    """Ensure employee_id column has unique values."""
    improvements = []
    duplicates = df[df['employee_id'].duplicated()].index
    for idx in duplicates:
        new_id = f"E{idx+1000:04d}"
        while new_id in df['employee_id'].values:
            new_id = f"E{np.random.randint(1000, 9999):04d}"
        df.loc[idx, 'employee_id'] = new_id
    if len(duplicates) > 0:
        improvements.append("Fixed duplicate employee IDs")
    return df, improvements


def fix_statistical_issues(df):
    """Improve statistical consistency in salary, age, and department distributions."""
    improvements = []

    # Salary-experience correlation
    correlation = df['salary'].corr(df['experience_years'])
    if correlation < 0.3:
        df = adjust_salary_experience(df)
        improvements.append("Improved salary-experience correlation")

    # Department balancing
    if df['department'].value_counts().max() - df['department'].value_counts().min() > 15:
        df = balance_departments(df)
        improvements.append("Balanced department distributions")

    # Age-experience relationship
    df = adjust_age_experience(df)
    improvements.append("Improved age-experience relationship")

    return df, improvements


def adjust_salary_experience(df):
    """Recalculate salaries to better match experience and department multipliers."""
    base_salary = 35000
    dept_multipliers = {
        'Engineering': 1.3,
        'Finance': 1.2,
        'Sales': 1.1,
        'Marketing': 1.0,
        'HR': 0.95
    }
    for idx, row in df.iterrows():
        exp = row['experience_years']
        dept = row['department']
        new_salary = base_salary + (exp * 3500) + np.random.randint(-8000, 12000)
        new_salary *= dept_multipliers.get(dept, 1.0)
        df.loc[idx, 'salary'] = max(30000, min(180000, int(new_salary)))
    return df


def balance_departments(df):
    """Reassign employees to departments if distribution is too uneven."""
    departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance']
    target_per_dept = len(df) // len(departments)
    dept_counts = df['department'].value_counts()

    for dept in departments:
        while dept_counts.get(dept, 0) < target_per_dept - 2:
            over_dept = dept_counts.idxmax()
            if dept_counts[over_dept] > target_per_dept + 2:
                employee_to_move = df[df['department'] == over_dept].index[0]
                df.loc[employee_to_move, 'department'] = dept
                dept_counts = df['department'].value_counts()
            else:
                break
    return df


def adjust_age_experience(df):
    """Ensure age and experience years align realistically."""
    for idx, row in df.iterrows():
        age, exp = row['age'], row['experience_years']
        expected_min_age = exp + 22
        if age < expected_min_age:
            df.loc[idx, 'age'] = min(65, expected_min_age + np.random.randint(0, 8))
        elif age > expected_min_age + 20:
            if np.random.random() > 0.5:
                df.loc[idx, 'experience_years'] = min(30, age - 22 - np.random.randint(0, 8))
            else:
                df.loc[idx, 'age'] = min(65, expected_min_age + np.random.randint(0, 15))
    return df
