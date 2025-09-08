import logging

logger = logging.getLogger(__name__)

class DataStorage:
    """Enhanced data storage with feedback-driven generation parameters"""
    def __init__(self):
        self.current_data = None
        self.metadata = {}
        self.feedback_history = []
        self.iteration_count = 0
        self.all_versions = []

    
    def save_current_data_to_csv(self):
        if self.current_data is not None:
            filename = f"./data/employee_data_iteration_{self.iteration_count}.csv"
            self.current_data.to_csv(filename, index=False)
            self.all_versions.append(filename)
            logger.info(f"Saved data to {filename}")
            return filename
        return None


# Global data store
data_store = DataStorage()
