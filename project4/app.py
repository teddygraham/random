import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import product

def calculate_joint_probability(parameters):
    """
    Calculate joint probability based on user-defined parameters and conditions
    
    Parameters:
    parameters (dict): Dictionary containing parameter names, possible values, 
                       probabilities, and conditions
    
    Returns:
    float: Joint probability
    """
    # Extract individual probabilities based on conditions
    probs = []
    for param_name, param_info in parameters.items():
        values = param_info['values']
        probabilities = param_info['probabilities']
        conditions = param_info.get('conditions', [])
        
        # If no conditions, use base probability
        if not conditions:
            selected_value_index = values.index(param_info['selected_value'])
            probs.append(probabilities[selected_value_index])
        else:
            # Apply conditional probabilities
            for condition in conditions:
                condition_param = condition['param']
                condition_value = condition['value']
                condition_prob_map = condition['prob_map']
                
                # Check if condition is met
                for param, info in parameters.items():
                    if param == condition_param and info['selected_value'] == condition_value:
                        selected_value_index = values.index(param_info['selected_value'])
                        # Use conditional probability if available
                        if selected_value_index in condition_prob_map:
                            probs.append(condition_prob_map[selected_value_index])
                            break
                        else:
                            # Fall back to base probability
                            probs.append(probabilities[selected_value_index])
                            break
                else:
                    # If condition wasn't met, use base probability
                    selected_value_index = values.index(param_info['selected_value'])
                    probs.append(probabilities[selected_value_index])
    
    # Calculate joint probability (product of all individual probabilities)
    joint_prob = np.prod(probs)
    return joint_prob

def main():
    st.title("Joint Probability Calculator")
    st.write("Calculate the joint probability of multiple parameters with conditions")
    
    # Initialize parameters dictionary in session state if not exists
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {}
        
    # Add parameter section
    with st.expander("Add New Parameter", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            param_name = st.text_input("Parameter Name")
        
        # Input for comma-separated values
        values_input = st.text_input("Possible Values (comma-separated)")
        
        # Input for comma-separated probabilities
        prob_input = st.text_input("Probabilities (comma-separated)")
        
        if st.button("Add Parameter"):
            if param_name and values_input and prob_input:
                values = [val.strip() for val in values_input.split(',')]
                probabilities = [float(p.strip()) for p in prob_input.split(',')]
                
                # Validate probabilities sum to 1 (with more tolerance for floating point errors)
                if len(values) != len(probabilities):
                    st.error("Number of values must match number of probabilities")
                elif abs(sum(probabilities) - 1.0) > 0.01:  # Increased tolerance to 0.01
                    st.error(f"Probabilities must sum to 1. Current sum: {sum(probabilities):.2f}")
                    st.info("Tip: For example, if you have 3 values, probabilities could be 0.3, 0.4, 0.3")
                else:
                    # Normalize probabilities to ensure they sum to exactly 1
                    total = sum(probabilities)
                    normalized_probs = [p/total for p in probabilities]
                    
                    st.session_state.parameters[param_name] = {
                        'values': values,
                        'probabilities': normalized_probs,
                        'selected_value': values[0],
                        'conditions': []
                    }
                    st.success(f"Added parameter: {param_name}")
    
    # Add conditions section
    if st.session_state.parameters:
        with st.expander("Add Condition", expanded=True):
            param_to_condition = st.selectbox("Parameter to add condition to", 
                                             options=list(st.session_state.parameters.keys()))
            
            condition_param = st.selectbox("Condition Parameter", 
                                          options=[p for p in st.session_state.parameters.keys()
                                                 if p != param_to_condition])
            
            if condition_param:
                condition_value = st.selectbox("When this value is selected", 
                                              options=st.session_state.parameters[condition_param]['values'])
                
                st.write("Specify new probabilities for each value of", param_to_condition)
                
                condition_probs = {}
                param_values = st.session_state.parameters[param_to_condition]['values']
                
                for i, val in enumerate(param_values):
                    new_prob = st.number_input(f"New probability for {val}", 
                                              min_value=0.0, max_value=1.0, 
                                              value=st.session_state.parameters[param_to_condition]['probabilities'][i])
                    condition_probs[i] = new_prob
                
                # Validate probabilities sum to 1 with more tolerance
                prob_sum = sum(condition_probs.values())
                if abs(prob_sum - 1.0) > 0.01:
                    st.warning(f"Condition probabilities should sum to 1. Current sum: {prob_sum:.2f}")
                
                if st.button("Add Condition"):
                    # Normalize condition probabilities
                    total = sum(condition_probs.values())
                    normalized_cond_probs = {k: v/total for k, v in condition_probs.items()}
                    new_condition = {
                        'param': condition_param,
                        'value': condition_value,
                        'prob_map': normalized_cond_probs
                    }
                    
                    st.session_state.parameters[param_to_condition]['conditions'].append(new_condition)
                    st.success(f"Added condition to {param_to_condition} based on {condition_param}")
    
    # Parameters and calculation section
    if st.session_state.parameters:
        st.write("---")
        st.subheader("Parameter Selection")
        
        # Create selection widgets for each parameter
        for param_name, param_info in st.session_state.parameters.items():
            selected_value = st.selectbox(f"Select value for {param_name}", 
                                         options=param_info['values'],
                                         key=f"select_{param_name}")
            
            # Update selected value in session state
            st.session_state.parameters[param_name]['selected_value'] = selected_value
        
        if st.button("Calculate Joint Probability"):
            joint_prob = calculate_joint_probability(st.session_state.parameters)
            st.success(f"Joint Probability: {joint_prob:.6f}")
            
            # Display the calculation breakdown
            st.subheader("Calculation Breakdown")
            st.write("Selected values:")
            for param, info in st.session_state.parameters.items():
                st.write(f"- {param}: {info['selected_value']}")
                
            st.write("Conditions applied:")
            for param, info in st.session_state.parameters.items():
                if info['conditions']:
                    for condition in info['conditions']:
                        cond_param = condition['param']
                        cond_value = condition['value']
                        is_active = st.session_state.parameters[cond_param]['selected_value'] == cond_value
                        status = "✅ Applied" if is_active else "❌ Not applied"
                        st.write(f"- Condition on {param} when {cond_param}={cond_value}: {status}")
        
        # Reset button
        if st.button("Reset All Parameters"):
            st.session_state.parameters = {}
            st.experimental_rerun()

if __name__ == "__main__":
    main()