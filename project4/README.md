# Joint Probability Calculator

A Streamlit application for calculating joint probabilities with dynamic parameter conditions.

## Features

- Add multiple parameters with their possible values and probabilities
- Create conditional probabilities between parameters
- Calculate joint probability based on selected values and conditions
- Visualize the calculation breakdown
- Dynamic UI that updates as parameters and conditions are added

## Usage Instructions

1. **Add Parameters**:
   - Enter a parameter name (e.g., "Weather")
   - Enter possible values separated by commas (e.g., "Sunny, Rainy, Cloudy")
   - Enter corresponding probabilities separated by commas (e.g., "0.6, 0.3, 0.1")
   - Probabilities must sum to 1

2. **Add Conditions** (optional):
   - Select a parameter to add a condition to
   - Select which other parameter it depends on
   - Select the specific value of the dependent parameter
   - Specify new probabilities for each value when the condition is met

3. **Calculate Joint Probability**:
   - Select values for each parameter using the dropdown menus
   - Click "Calculate Joint Probability"
   - View the result and calculation breakdown

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-directory>

# Install dependencies
pip install streamlit pandas numpy matplotlib

# Run the app
streamlit run app.py
```

## Examples

Example 1: Basic weather and activity probability
- Parameter 1: Weather (Sunny [0.6], Rainy [0.3], Cloudy [0.1])
- Parameter 2: Activity (Outdoor [0.7], Indoor [0.3])
- Condition: When Weather=Rainy, Activity probabilities change to (Outdoor [0.2], Indoor [0.8])

Example 2: Medical diagnosis
- Parameter 1: Disease (Present [0.01], Absent [0.99])
- Parameter 2: Test Result (Positive [0.05], Negative [0.95])
- Condition: When Disease=Present, Test Result probabilities change to (Positive [0.9], Negative [0.1])