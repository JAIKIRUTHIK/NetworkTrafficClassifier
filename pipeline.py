import subprocess
import sys


scripts = [
    ["-m", "capture.packet_capture"],
    ["-m", "flow.flow_builder"],
    ["-m", "features.feature_extractor"],
    ["-m", "classifier.rule_classifier"],
    ["-m", "analysis.usage_analyzer"],
    ["-m", "aggregation.device_aggregator"]
]


print()
print("======================================")
print("   NETWORK TRAFFIC ANALYSIS PIPELINE")
print("======================================")
print()


for script in scripts:

    display_name = " ".join(script)

    if script[0] == "-m":
        display_name = script[1]

    print("--------------------------------------")
    print("Running:", display_name)
    print("--------------------------------------")

    result = subprocess.run(
        [sys.executable] + script
    )

    if result.returncode != 0:

        print()
        print("ERROR while running:", display_name)
        print("Pipeline stopped.")

        sys.exit(1)


print()
print("======================================")
print("       PIPELINE COMPLETED")
print("======================================")
print()