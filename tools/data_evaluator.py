import json
import logging
from crewai.tools import tool
from config import QualityMetrics
from storage import data_store

logger = logging.getLogger(__name__)

@tool
def evaluate_data_quality() -> str:
    """
    Evaluate the quality of generated synthetic data.
    
    Returns:
        JSON string with quality metrics and feedback
    """
    logger.info("evaluating the data")
    try:
        if data_store.current_data is None:
            return json.dumps({"status": "error", "message": "No data to evaluate"})

        df = data_store.current_data
        metrics = QualityMetrics()

        # Completeness
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        metrics.completeness = ((total_cells - missing_cells) / total_cells) * 100

        # Uniqueness
        metrics.uniqueness = (df["employee_id"].nunique() / len(df)) * 100

        # Statistical validity
        stats_score = 100.0
        if not ((df["age"] >= 22).all() and (df["age"] <= 65).all()):
            stats_score -= 20
        if df["salary"].corr(df["experience_years"]) < 0.3:
            stats_score -= 20
        if df["department"].value_counts().min() < 5:
            stats_score -= 10
        metrics.statistical_validity = max(0, stats_score)

        # Overall score
        metrics.overall_score = (
            metrics.completeness * 0.3 +
            metrics.uniqueness * 0.3 +
            metrics.statistical_validity * 0.4
        )

        feedback_points = []
        if metrics.completeness < 100:
            feedback_points.append("Data has missing values")
        if metrics.uniqueness < 100:
            feedback_points.append("Duplicate employee IDs found")
        if metrics.statistical_validity < 90:
            feedback_points.append("Statistical distributions need improvement")

        metrics.feedback = "; ".join(feedback_points)

        return json.dumps({
            "status": "evaluated",
            "metrics": vars(metrics),
            "feedback": metrics.feedback,
            "detailed_feedback": feedback_points,
            "iteration": data_store.iteration_count - 1
        })

    except Exception as e:
        logger.error(f"Error evaluating data: {e}")
        return json.dumps({"status": "error", "message": str(e)})

@tool
def provide_improvement_suggestions(evaluation_json: str) -> str:
    """
    Provide specific improvement suggestions based on evaluation results.
    
    Args:
        evaluation_json: JSON string containing evaluation results
    
    Returns:
        JSON string with improvement suggestions
    """
    logger.info("generating suggestions")
    try:
        evaluation = json.loads(evaluation_json)
        metrics = evaluation.get("metrics", {})
        suggestions = []

        if metrics.get("completeness", 100) < 100:
            suggestions.append({"area": "completeness", "suggestion": "Ensure no null values", "priority": "high"})
        if metrics.get("uniqueness", 100) < 100:
            suggestions.append({"area": "uniqueness", "suggestion": "Use robust unique ID generation", "priority": "high"})
        if metrics.get("statistical_validity", 100) < 85:
            suggestions.append({"area": "statistical_validity", "suggestion": "Improve salary-experience correlation", "priority": "medium"})
        if metrics.get("overall_score", 0) < 70:
            suggestions.append({"area": "general", "suggestion": "Consider advanced data generation algorithms", "priority": "medium"})

        return json.dumps({
            "status": "suggestions_ready",
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        })

    except Exception as e:
        logger.error(f"Error providing suggestions: {e}")
        return json.dumps({"status": "error", "message": str(e)})
