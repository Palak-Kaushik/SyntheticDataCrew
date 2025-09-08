# Synthetic Data Generator Crew

This project has a crew of agents that generate and  evaluate synthetic data.


## Project Structure
```
.
├── data/                  # Output data (generated and evaluated results)
├── tools/
│   ├── data\_evaluator.py  # Tools for evaluating data
│   └── data\_generator.py  # Tools for generating data
├── agents.py              # Agent initialization
├── config.py              # Data classes for generated data & quality metrics
├── main.py                # Entry point to run the system
├── storage.py             # Save/load generated data
├── tasks.py               # Agent task creation
├── requirements.txt       # Python dependencies

```

## How to run

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. The main entry point is `main.py`.
    Run the system with:

    ```bash
    python main.py
    ```



##  Output

All generated and evaluated data will be stored in the `data/` directory.
