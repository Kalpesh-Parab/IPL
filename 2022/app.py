import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
import os


# Load the pre-trained model
pipe = pickle.load(open('pipe.pkl', 'rb'))

# Teams and cities lists
teams = ['Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore', 'Kolkata Knight Riders',
         'Kings XI Punjab', 'Chennai Super Kings', 'Rajasthan Royals', 'Delhi Capitals']

cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
          'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
          'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
          'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
          'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
          'Sharjah', 'Mohali', 'Bengaluru']

# Team-wise hero selection
team_heroes = {
    'Sunrisers Hyderabad': ['Abdul Samad','Aiden Markram', 'Rahul Tripathi', 'Glenn Phillips', 'Abhishek Sharma', 'Marco Jansen', 'Washington Sundar', 'Fazalhaq Farooqi', 'Kartik Tyagi', 'Bhuvneshwar Kumar', 'T. Natarajan', 'Umran Malik'],
    'Mumbai Indians': ['Rohit Sharma','Tim David','Ramandeep Singh','Tilak Varma','Suryakumar Yadav','Ishan Kishan','Tristan Stubbs','Dewald Brevis','Jofra Archer','Jasprit Bumrah','Arjun Tendulkar','Arshad Khan','Kumar Kartikeya','Hrithik Shokeen','Jason Behrendorff','Akash Madhwal'],
    'Royal Challengers Bangalore': ['Virat Kohli','Glenn Maxwell','Mohammad Siraj','Faf Du Plessis','Harshal Patel','Wanindu Hasaranga','Dinesh Karthik','Shahbaz Ahemad','Anuj Rawat','Akash Deep','Josh Hazlewood','Mahipal Lomror','Finn Allen','Suyash Prabhudessai','Karn Sharma','Siddharth Kaul','David Willey'],
    'Kolkata Knight Riders': ['Aarya Desai','Jason Roy','Johnson Charles','Mandeep Singh','Nitish Rana','Rinku Singh','Shreyas Iyer','Andre Russell','Anukul Roy','David Wiese','Sunil Narine','Venkatesh Iyer','Narayan Jagadeesan','Rahmanullah Gurbaz','Harshit Rana','Kulwant Khejroliya','Lockie Ferguson','Shardul Thakur','Suyash Sharma','Tim Southee','Umesh Yadav','Vaibhav Arora','Varun Chakaravarthy'],
    'Kings XI Punjab': ['Atharva Taide','Bhanuka Rajapaksa','Harpreet Singh','Shahrukh Khan','Shikhar Dhawan','Shivam Singh','Liam Livingstone','Matthew Short','Mohit Rathee','Rishi Dhawan','Sam Curran','Sikandar Raza','Jitesh Sharma','Prabhsimran Singh','Arshdeep Singh','Baltej Singh','Gurnoor Brar','Harpreet Brar','Kagiso Rabada','Nathan Ellis','Rahul Chahar','Vidwath Kaverappa'],
    'Chennai Super Kings': ['MS Dhoni', 'Ravindra Jadeja', 'Tushar Deshpande', 'Mukesh Choudhary', 'Matisha Pathirana', 'Devon Conway', 'Ruturaj Gaikwad', 'Ambati Rayudu', 'Subranshu Senapathy', 'Simarjeet Singh', 'Deepak Chahar', 'Prashant Solanki', 'Mahish Tekshana', 'Rajkar Dubhan', 'Rajhange', 'Moen Ali', 'Dwayne Pretorius', 'Mitchell Santner'],
    'Rajasthan Royals': ['Karun Nair','Navdeep Saini','Riyan Parag','Shimron Hetmyer','Daryl Mitchell','James Neesham','Ravichandran Ashwin','Shubham Garhwal','KC Cariappa','Jos Buttler','Anunay Singh','Corbin Bosch','Dhruv Jurel','Kuldeep Sen','Kuldip Yadav','Rassie van der Dussen','Obed McCoy','Tejas Baroka'],
    'Delhi Capitals': ['David Warner','Axar Patel','Rishabh Pant','Prithvi Shaw','Kamlesh Nagarkoti','Mitchell Marsh','Sarfaraz Khan','Anrich Nortje','Chetan Sakariya','Kuldeep Yadav','Lalit Yadav','Lungi Ngidi','Mustafizur Rahman','Pravin Dubey','Vicky Ostwal','Aman Khan']
}

# Title and page configuration
st.title('IPL Win Predictor')

# Team and city selection
col1, col2 = st.columns(2)
with col1:
    batting_team = st.selectbox('Select the batting team', sorted(teams))
    batting_heroes = st.multiselect('Select the batting heroes', team_heroes[batting_team], default=[], key='batting_heroes')
    # Ensure only two heroes are selected
    if len(batting_heroes) != 2:
        st.error("Please select exactly two batting heroes.")
        st.stop()
with col2:
    bowling_team = st.selectbox('Select the bowling team', sorted(teams))
    bowling_hero = st.selectbox('Select the bowling team hero', team_heroes[bowling_team])

selected_city = st.selectbox('Select host city', sorted(cities))

# Target and match details
target = st.number_input('Target', value=0, step=1)
score = st.number_input('Score', value=0, step=1)

col3, col4, col5 = st.columns(3)

with col3:
    overs = st.slider('Overs completed', 0, 20, 0)
with col4:
    show_wickets = st.checkbox('Include Wickets')
    if show_wickets:
        wickets = st.number_input('Wickets out', value=0, step=1)
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

        # Create input dataframe with hero information
        input_df = pd.DataFrame({
            'batting_team': [batting_team],
            'batting_heroes': [batting_heroes],
            'bowling_team': [bowling_team],
            'bowling_hero': [bowling_hero],
            'city': [selected_city],
            'runs_left': [runs_left],
            'balls_left': [balls_left],
            'wickets': [wickets],
            'total_runs_x': [target],
            'crr': [crr],
            'rrr': [rrr],
            'win_probability': [0],
            'loss_probability': [0]
        })

        # Predict probabilities
        result = pipe.predict_proba(input_df)
        win_probability = result[0][1]
        loss_probability = result[0][0]


        # Update the win and loss probabilities in the DataFrame
        input_df.loc[input_df.index[-1], 'win_probability'] = win_probability
        input_df.loc[input_df.index[-1], 'loss_probability'] = loss_probability
        if os.path.exists('user_inputs.xlsx'):
            existing_data = pd.read_excel('user_inputs.xlsx')
            input_df = pd.concat([existing_data, input_df], ignore_index=True)
        input_df.to_excel('user_inputs.xlsx', index=False)

    

        # Display live scoreboard
        st.subheader("Live Scoreboard:")
        st.text(f"{batting_team}: {score}/{10-wickets} | {bowling_team}: {target}")

        # Display additional information
        st.subheader("Match Situation:")
        st.write(f"Runs Left: {runs_left}")
        st.write(f"Balls Left: {balls_left}")
        st.write(f"Wickets Left: {wickets}")
        st.write(f"Current Run Rate (CRR): {crr:.2f}")
        st.write(f"Required Run Rate (RRR): {rrr:.2f}")

        # Display match equation
        st.subheader("Match Equation:")
        st.write(f"{runs_left} runs required from {balls_left} balls")
        

        # Display results with conditional styling
        st.header(f"{batting_team} - {round(win_probability * 100)}%")
        st.header(f"{bowling_team} - {round(loss_probability * 100)}%")

        # Conditional styling for win probability text
        if win_probability > 0.7:
            st.markdown('<p style="color: green;">High chance of winning!</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: red;">Be cautious! Lower chance of winning.</p>', unsafe_allow_html=True)

        # Visualize probabilities
        fig = px.bar(
            x=[f"{batting_team} Win", f"{bowling_team} Loss"],
            y=[win_probability, loss_probability],
            labels={'y': 'Probability'},
            title='Match Outcome Probabilities'
        )
        st.plotly_chart(fig)


# Reset button
if st.button('Reset'):
    # Clear session state
    st.session_state.clear()
    # Rerun the app to reset input values
    st.experimental_rerun()

