from pathlib import Path
import subprocess
import sys


ROOT_DIR = Path(__file__).resolve().parent


SCRIPTS = [
    "capture.packet_capture",
    "flow.flow_builder",
    "features.feature_extractor",
    "classifier.rule_classifier",
    "analysis.usage_analyzer",
    "aggregation.device_aggregator"
]


def run_pipeline():

    print()
    print("======================================")
    print("   NETWORK TRAFFIC ANALYSIS PIPELINE")
    print("======================================")
    print()

    for module in SCRIPTS:

        print("--------------------------------------")
        print("Running:", module)
        print("--------------------------------------")

        result = subprocess.run(
            [sys.executable, "-m", module],
            cwd=ROOT_DIR
        )

        if result.returncode != 0:

            print()
            print("ERROR while running:", module)
            print("Pipeline stopped.")
            print()

            return False

    print()
    print("======================================")
    print("       PIPELINE COMPLETED")
    print("======================================")
    print()

    return True


if __name__ == "__main__":
    success = run_pipeline()

    if not success:
        sys.exit(1)