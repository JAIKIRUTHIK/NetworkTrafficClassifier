# NetworkTrafficClassifier

## Network Traffic Classifier & Usage Dashboard

NetworkTrafficClassifier is a rule-based network traffic analysis system that captures IPv4 packets, reconstructs network flows, extracts traffic features, classifies traffic into meaningful categories, analyzes usage, aggregates traffic by device, and presents the results through an interactive Streamlit dashboard.

The project is designed without machine learning. Traffic classification is performed using deterministic protocol, port, packet-rate, traffic-volume, and destination-address rules.

---

## 1. Project Objectives

The system is designed to:

- Capture live network traffic.
- Parse IPv4 packets and extract relevant information.
- Reconstruct bidirectional network flows.
- Calculate flow-level traffic features.
- Classify traffic using deterministic rules.
- Analyze traffic by category, protocol, destination, and port.
- Aggregate traffic usage by device.
- Detect potentially significant traffic conditions.
- Provide an interactive network monitoring dashboard.
- Provide a genuine live packet monitoring interface.

---

## 2. System Architecture

```text
Network Traffic
      │
Packet Capture
      │
Packet Parsing
      │
Flow Reconstruction
      │
Feature Extraction
      │
Rule-Based Classification
      │
      ├───────────────┐
      |               |
Usage Analysis    Device Aggregation
      │               │
      └───────┬───────┘
              |
       Streamlit Dashboard