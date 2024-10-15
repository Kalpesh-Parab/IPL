import streamlit as st
import pickle
import pandas as pd

# Load the pre-trained model
pipe = pickle.load(open('pipe.pkl', 'rb'))

# Teams and cities lists
teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore', 'Kolkata Knight Riders',
         'Kings XI Punjab', 'Chennai Super Kings', 'Rajasthan Royals', 'Delhi Capitals']

cities = ['Hyderabad', 'Bengaluru', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
          'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
          'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
          'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
          'Sharjah', 'Mohali']

# Title and page configuration
st.title('IPL Win Predictor')

# Initialize session state
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = []

# Team and city selection
col1, col2 = st.columns(2)
with col1:
    batting_team = st.selectbox('Select the batting team', sorted(teams))
with col2:
    bowling_team = st.selectbox('Select the bowling team', sorted(teams))

# Validate that batting and bowling teams are different
if batting_team == bowling_team:
    st.error("Batting team and bowling team can't be the same. Please select different teams.")
    st.stop()

selected_city = st.selectbox('Select host city', sorted(cities))

# Target and match details
target = st.number_input('Target', value=0, step=1)
score = st.number_input('Score', value=0, step=1)

# Slider for overs completed
overs = st.slider('Overs completed', 0, 20, 0)

# Checkbox for including wickets
show_wickets = st.checkbox('Include Wickets')
if show_wickets:
    wickets = st.number_input('Wickets out', min_value=0, max_value=9, value=0, step=1)
else:
    wickets = 0  # Default value when not visible

# Error handling for invalid inputs
if target <= score:
    st.error("Target must be greater than the current score.")
elif overs > 20:
    st.error("Overs completed cannot be more than 20.")
else:
    # Prediction button
    if st.button('Predict Probability'):
        runs_left = target - score
        balls_left = 120 - (overs * 6)
        wickets = 10 - wickets
        crr = score / overs
        rrr = (runs_left * 6) / balls_left

        # Create input dataframe
        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'bowling_team': [bowling_team],
            'city': [selected_city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets': [wickets],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr]
        })

        # Predict probabilities
        result = pipe.predict_proba(input_df)
        win_probability = result[0][1]
        loss_probability = result[0][0]

        # Display results with conditional styling
        st.header(f"{batting_team} - {round(win_probability * 100)}%")
        st.header(f"{bowling_team} - {round(loss_probability * 100)}%")

        # Conditional styling for win probability text
        if win_probability > 0.7:
            st.markdown(f'<p style="color: green;">High chance of {batting_team} winning!</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color: red;">Be cautious! Lower chance of {batting_team} winning.</p>', unsafe_allow_html=True)

        # Live Scoreboard and Match Situation
        st.subheader('Live Scoreboard:')
        st.write(f"**{batting_team}**: {score}/{wickets} in {overs} overs")
        st.write(f"{runs_left} runs required from {balls_left} balls")
        st.write(f"**Target**: {target}")

        st.subheader('Match Situation:')
        st.write(f"**Current Run Rate (CRR)**: {crr:.2f}")
        st.write(f"**Required Run Rate (RRR)**: {rrr:.2f}")


        # Save user inputs to session state
        user_inputs = {
            'Batting Team': batting_team,
            'Bowling Team': bowling_team,
            'Host City': selected_city,
            'Target': target,
            'Score': score,
            'Overs Completed': overs,
            'Include Wickets': show_wickets,
            'Wickets Out': 10-wickets,
            'Win Probability': win_probability,
            'Loss Probability': loss_probability
        }
        st.session_state.user_inputs.append(user_inputs)

# Display saved user inputs
if st.session_state.user_inputs:
    st.subheader('Saved User Inputs:')
    saved_user_inputs_df = pd.DataFrame(st.session_state.user_inputs)
    st.write(saved_user_inputs_df)

    # Save user inputs to Excel
    saved_user_inputs_df.to_excel('user_inputs.xlsx', index=False)
    st.success('User inputs saved to user_inputs.xlsx')

# Reset button
if st.button('Reset'):
    st.session_state.user_inputs = []
    st.experimental_rerun()  # Rerun the app to reset input values
