"""SkillPulse Spark RDD Pipeline Runner.
Invokes the unified Spark RDD Analytical & ML Pipeline.
Usage: python spark_jobs/pipeline.py [path/to/postings.csv]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from backend.spark.pipeline import run_pipeline

if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(data_csv_path=csv_arg)
