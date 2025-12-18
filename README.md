# 🇷🇼 Rwanda EV Policy Decision Engine

> Scenario-based policy simulator for Rwanda's electric vehicle transition

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🎯 Overview

The Rwanda EV Policy Decision Engine is an interactive web application that helps policymakers, utilities, investors, and researchers simulate different scenarios for Rwanda's electric vehicle (EV) transition. The tool provides evidence-based recommendations based on technical research, economic analysis, and stakeholder perspectives.

### Key Features
- **Scenario Simulation**: Adjust EV adoption rates, infrastructure deployment, and policy parameters
- **Grid Impact Analysis**: Technical analysis based on IPSA+ power system simulations
- **Financial Modeling**: Cost-benefit analysis and incentive optimization
- **Policy Recommendations**: Tailored advice based on stakeholder perspective
- **Visual Dashboard**: Interactive charts, risk indicators, and implementation roadmaps

## 📊 Research Basis

This tool is built on published research findings:

| Research Aspect | Key Findings |
|----------------|--------------|
| **Grid Impact (IPSA+)** | Maximum safe penetration: 1.5% private cars, 10% buses/taxis with 10kW chargers |
| **Economic Analysis (HOMER)** | Solar-PV microgrids can reduce LCOE by 139.7% (to -$0.103/kWh) |
| **Adoption Barriers** | Most significant: High initial cost (OR=1.98), Limited charging infrastructure (OR=1.77) |
| **Effective Incentives** | Financial subsidies (OR=3.39), Tax exemptions (OR=2.41) most effective |

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MutuaNdunda/rwanda-ev-policy-engine.git
   cd rwanda-ev-policy-engine