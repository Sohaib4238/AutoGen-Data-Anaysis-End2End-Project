"""
test.py
A quick script to test the backend pipeline in isolation.
"""
from src.core.orchestrator import DataAnalyzerPipeline

def main():
    # 1. Define our test parameters
    filename = "sample.csv" # Must be exactly what you named it in temp_workspace
    query = "Load the dataset, check for missing values, calculate the average salary by department, and generate a bar chart showing these averages."
    
    print("🚀 Initializing AutoGen Data Analyzer Pipeline...")
    
    # 2. Instantiate and run the pipeline
    pipeline = DataAnalyzerPipeline(user_query=query, filename=filename)
    result = pipeline.execute()
    
    # 3. Output the final summary
    print("\n" + "="*50)
    print("🎯 FINAL REPORT FROM AGENTS:")
    print("="*50)
    print(result.summary)

if __name__ == "__main__":
    main()