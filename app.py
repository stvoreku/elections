import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from election_data import ElectionData
from dhondt import dhondt
from party_abbreviations import get_party_abbreviation
import csv

# Load election data
election_data = ElectionData('2015-gl-lis-okr.csv')

DISTRICTS_SEATS = {}
# Load district seats
with open('okregi-mandaty.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        DISTRICTS_SEATS[int(row['Nr'])] = int(row['LM'])



# Store original votes for reset functionality
if 'original_votes' not in st.session_state:
    st.session_state.original_votes = election_data.district_party_votes.copy()

# Reset button
if st.button('Reset to Original Values'):
    election_data.district_party_votes = st.session_state.original_votes.copy()
    st.session_state.modifications = []

# Initialize modifications in session state
if 'modifications' not in st.session_state:
    st.session_state.modifications = []

# Add a new modification
if st.button('Add a Modification'):
    st.session_state.modifications.append({
        'selected_party': None,
        'modification_type': None,
        'target_party': None,
        'modification_percentage': 0
    })

# Display and apply modifications
for i, modification in enumerate(st.session_state.modifications):
    st.write(f"Modification {i + 1}")
    modification['selected_party'] = st.selectbox(
        f"Select Party to Modify (Modification {i + 1})",
        list(election_data.total_votes.keys()),
        key=f"selected_party_{i}"
    )
    modification['modification_type'] = st.selectbox(
        f"Select Modification Type (Modification {i + 1})",
        ['Przenieś głosy', 'Usuń głosy'],
        key=f"modification_type_{i}"
    )
    if modification['modification_type'] == 'Przenieś głosy':
        modification['target_party'] = st.selectbox(
            f"Select Target Party (Modification {i + 1})",
            [p for p in election_data.total_votes.keys() if p != modification['selected_party']],
            key=f"target_party_{i}"
        )
    modification['modification_percentage'] = st.slider(
        f"Percentage of Votes to Modify (Modification {i + 1})",
        0, 100, 0, key=f"modification_percentage_{i}"
    )

# Apply all modifications
for modification in st.session_state.modifications:
    for district, votes in election_data.district_party_votes.items():
        total_votes_selected = votes.get(modification['selected_party'], 0)
        votes_to_modify = int(total_votes_selected * (modification['modification_percentage'] / 100))

        if modification['modification_type'] == 'Przenieś głosy' and modification['target_party']:
            votes[modification['selected_party']] -= votes_to_modify
            if modification['target_party'] in votes:
                votes[modification['target_party']] += votes_to_modify
            else:
                votes[modification['target_party']] = votes_to_modify
        elif modification['modification_type'] == 'Usuń głosy':
            votes[modification['selected_party']] -= votes_to_modify

# Recalculate the election data
election_data.recalculate()

# Calculate total votes and seats for all districts
total_votes_all_districts = {}
global_seat_allocation = {}

for district, votes in election_data.district_party_votes.items():
    for party, vote_count in votes.items():
        if party not in total_votes_all_districts:
            total_votes_all_districts[party] = 0
        total_votes_all_districts[party] += vote_count

    # Calculate seat allocation for the district
    parties_votes = {party: votes for party, votes in votes.items() if party in election_data.eligible_parties}
    allocation = dhondt(parties_votes, DISTRICTS_SEATS[district])

    # Aggregate seat allocation
    for party, seats in allocation.items():
        if party not in global_seat_allocation:
            global_seat_allocation[party] = 0
        global_seat_allocation[party] += seats

# Store original seat allocation for reset functionality
if 'original_global_seat_allocation' not in st.session_state:
    st.session_state.original_global_seat_allocation = {}

# Calculate original seat allocation (only once)
if not st.session_state.original_global_seat_allocation:
    for district, votes in election_data.district_party_votes.items():
        parties_votes = {party: votes for party, votes in votes.items() if party in election_data.eligible_parties}
        allocation = dhondt(parties_votes, DISTRICTS_SEATS[district])
        for party, seats in allocation.items():
            if party not in st.session_state.original_global_seat_allocation:
                st.session_state.original_global_seat_allocation[party] = 0
            st.session_state.original_global_seat_allocation[party] += seats

# Calculate percentage of votes for each party
total_votes_sum = sum(total_votes_all_districts.values())
total_votes_df = pd.DataFrame(list(total_votes_all_districts.items()), columns=['Partia', 'Głosy'])
total_votes_df['Procent'] = (total_votes_df['Głosy'] / total_votes_sum) * 100
total_votes_df['Mandaty'] = total_votes_df['Partia'].map(global_seat_allocation).fillna(0).astype(int)
total_votes_df['Mandaty Oryginalne'] = total_votes_df['Partia'].map(st.session_state.original_global_seat_allocation).fillna(0).astype(int)
total_votes_df['Różnica Mandaty'] = total_votes_df['Mandaty'] - total_votes_df['Mandaty Oryginalne']
total_votes_df['Nazwa Partii'] = total_votes_df['Partia'].map(lambda x: get_party_abbreviation(x))
total_votes_df = total_votes_df[total_votes_df['Procent'] > 0.5]  # Filter parties with more than 0.5%
total_votes_df = total_votes_df.sort_values(by='Głosy', ascending=False)

# Display total votes, percentage, seats, original seats, and difference in seats
st.header('Suma głosów, procentów, mandatów, mandatów oryginalnych i różnicy mandatów')
st.write(total_votes_df[['Nazwa Partii', 'Głosy', 'Procent', 'Mandaty', 'Mandaty Oryginalne', 'Różnica Mandaty']])

# Add a selector for districts at the bottom
st.header('Wyniki dla wybranego okręgu')
selected_district = st.selectbox('Wybierz Okręg', list(election_data.district_party_votes.keys()))

# Display results for the selected district
if selected_district:
    district_data = election_data.district_party_votes[selected_district]
    # Filter eligible parties for the district
    parties_votes = {party: votes for party, votes in district_data.items() if party in election_data.eligible_parties}
    # Calculate seat allocation for the district
    allocation = dhondt(parties_votes, DISTRICTS_SEATS[selected_district])

    # Create a DataFrame for the district results
    district_results_df = pd.DataFrame(list(allocation.items()), columns=['Partia', 'Mandaty'])
    district_results_df['Nazwa Partii'] = district_results_df['Partia'].map(lambda x: get_party_abbreviation(x))
    district_results_df = district_results_df.sort_values(by='Mandaty', ascending=False)

    # Display the district results table
    st.write(district_results_df[['Nazwa Partii', 'Mandaty']])