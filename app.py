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

# Store original seat allocation for comparison
original_global_seat_allocation = {}
# Calculate original seat allocation
for district, votes in election_data.district_party_votes.items():
    parties_votes = {party: votes for party, votes in votes.items() if party in election_data.eligible_parties}
    allocation = dhondt(parties_votes, DISTRICTS_SEATS[district])
    for party, seats in allocation.items():
        if party not in original_global_seat_allocation:
            original_global_seat_allocation[party] = 0
        original_global_seat_allocation[party] += seats

# Define party colors
party_colors = {
    '1 - Komitet Wyborczy Prawo i Sprawiedliwość': 'darkblue',
    '2 - Komitet Wyborczy Platforma Obywatelska RP': 'orange',
    '8 - Komitet Wyborczy Nowoczesna Ryszarda Petru': 'blue',
    '6 - Koalicyjny Komitet Wyborczy Zjednoczona Lewica SLD+TR+PPS+UP+Zieloni': 'red',
    '7 - Komitet Wyborczy Wyborców „Kukiz\'15”': 'black',
    '4 - Komitet Wyborczy KORWiN': 'yellow',
    '3 - Komitet Wyborczy Partia Razem': 'purple',
    '5 - Komitet Wyborczy Polskie Stronnictwo Ludowe': 'green',
}


# Streamlit app
st.title('Wyniki Wyborów')

# Add sliders for adjusting votes
percent_to_lewica = st.slider('Procent który jednak zagłosował na Nową Lewicę', 0, 100, 0)
percent_stayed_home = st.slider('Ilu zostało w domu', 0, 100, 0)

# Adjust votes based on slider values for each district
for district, votes in election_data.district_party_votes.items():
    total_votes_razem = votes.get('3 - Komitet Wyborczy Partia Razem', 0)
    votes_to_lewica = int(total_votes_razem * (percent_to_lewica / 100))
    votes_stayed_home = int(total_votes_razem * (percent_stayed_home / 100))
    adjusted_votes_razem = total_votes_razem - votes_to_lewica - votes_stayed_home

    # Update the votes in the election data
    election_data.district_party_votes[district]['3 - Komitet Wyborczy Partia Razem'] = adjusted_votes_razem
    if '6 - Koalicyjny Komitet Wyborczy Zjednoczona Lewica SLD+TR+PPS+UP+Zieloni' in election_data.district_party_votes[district]:
        election_data.district_party_votes[district]['6 - Koalicyjny Komitet Wyborczy Zjednoczona Lewica SLD+TR+PPS+UP+Zieloni'] += votes_to_lewica
    else:
        election_data.district_party_votes[district]['6 - Koalicyjny Komitet Wyborczy Zjednoczona Lewica SLD+TR+PPS+UP+Zieloni'] = votes_to_lewica

# Recalculate the election data
election_data.recalculate()

# Calculate total votes and seats for all districts
total_votes_all_districts = {}
total_seats_all_districts = 0
global_seat_allocation = {}

for district, votes in election_data.district_party_votes.items():
    for party, vote_count in votes.items():
        if party not in total_votes_all_districts:
            total_votes_all_districts[party] = 0
        total_votes_all_districts[party] += vote_count
    total_seats_all_districts += DISTRICTS_SEATS[district]

    # Calculate seat allocation for the district
    parties_votes = {party: votes for party, votes in votes.items() if party in election_data.eligible_parties}
    allocation = dhondt(parties_votes, DISTRICTS_SEATS[district])

    # Aggregate seat allocation
    for party, seats in allocation.items():
        if party not in global_seat_allocation:
            global_seat_allocation[party] = 0
        global_seat_allocation[party] += seats

# Calculate percentage of votes for each party
total_votes_sum = sum(total_votes_all_districts.values())
total_votes_df = pd.DataFrame(list(total_votes_all_districts.items()), columns=['Partia', 'Głosy'])
total_votes_df['Procent'] = (total_votes_df['Głosy'] / total_votes_sum) * 100
total_votes_df['Mandaty'] = total_votes_df['Partia'].map(global_seat_allocation).fillna(0).astype(int)
total_votes_df['Nazwa Partii'] = total_votes_df['Partia'].map(lambda x: get_party_abbreviation(x))
total_votes_df = total_votes_df[total_votes_df['Procent'] > 0.5]  # Filter parties with more than 0.5%
total_votes_df = total_votes_df.sort_values(by='Głosy', ascending=False)

# Calculate the difference in seats compared to the original seat allocation
total_votes_df['Różnica Mandaty'] = total_votes_df.apply(lambda row: row['Mandaty'] - original_global_seat_allocation.get(row['Partia'], 0), axis=1)

# Display total votes, percentage, seats, and difference in seats for all districts
st.header('Suma głosów, procentów, mandatów i różnicy mandatów dla wszystkich okręgów')
st.write(total_votes_df[['Nazwa Partii', 'Głosy', 'Procent', 'Mandaty', 'Różnica Mandaty']])

# Plot bar chart for percentage of votes
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(15, 8))  # Adjust figure size
barplot = sns.barplot(x='Nazwa Partii', y='Procent', data=total_votes_df, palette=total_votes_df['Partia'].map(party_colors).fillna('gray').tolist(), ax=ax)
barplot.set_xticklabels(barplot.get_xticklabels(), rotation=45, horizontalalignment='right')
ax.set_ylabel('Procent')
ax.set_title('Procent głosów dla wszystkich okręgów')
fig.tight_layout()  # Ensure the plot uses the available space
st.pyplot(fig)

# Plot stacked bar chart for total seats
fig, ax = plt.subplots(figsize=(15, 8))  # Adjust figure size
bottom = 0
for party, color in party_colors.items():
    seats = total_votes_df[total_votes_df['Partia'] == party]['Mandaty'].values[0] if party in total_votes_df['Partia'].values else 0
    ax.barh(['Mandaty'], seats, left=bottom, color=color, label=party)
    bottom += seats
ax.set_xlim(0, 460)
ax.set_title('Suma mandatów dla wszystkich okręgów')
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=4)  # Adjust legend position and shape
fig.tight_layout()  # Ensure the plot uses the available space
st.pyplot(fig)

# Display eligible parties
st.header('Uprawnione Partie')
st.write(election_data.eligible_parties)

# Select district
districts = list(election_data.district_party_votes.keys())
selected_district = st.selectbox('Wybierz Okręg', districts)

# Display bar chart for selected district
if selected_district:
    st.header(f'Wyniki dla Okręgu {selected_district}')
    district_data = election_data.district_party_votes[selected_district]
    # setup map for party names to abbreviations
    abbreviations = {party: get_party_abbreviation(party) for party in district_data.keys()}
    # Create DataFrame for plotting and sorting. Attach abbreviations
    df = pd.DataFrame(list(district_data.items()), columns=['Partia', 'Głosy'])
    df['Nazwa Partii'] = df['Partia'].map(abbreviations)
    # Sort DataFrame by votes
    df = df.sort_values(by='Głosy', ascending=False)

    # Calculate percentage of votes
    total_votes = df['Głosy'].sum()
    df['Procent'] = (df['Głosy'] / total_votes) * 100

    # Assign colors to parties, default to 'gray' if not found
    df['Kolor'] = df['Partia'].map(party_colors).fillna('gray')

    # Plot bar chart with seaborn
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(15, 8))  # Adjust figure size
    barplot = sns.barplot(x='Nazwa Partii', y='Procent', data=df, palette=df['Kolor'].tolist(), ax=ax)
    barplot.set_xticklabels(barplot.get_xticklabels(), rotation=45, horizontalalignment='right')
    ax.set_ylabel('Procent')
    ax.set_title(f'Wyniki dla Okręgu {selected_district}')
    fig.tight_layout()  # Ensure the plot uses the available space
    st.pyplot(fig)

    # Display sorted results below the chart
    st.write(df[['Nazwa Partii', 'Głosy', 'Procent']])

    # Get the number of seats for the selected district
    seats = DISTRICTS_SEATS[selected_district]
    st.write(f'Liczba mandatów: {seats}')
    # For the allocation we need to filter the parties
    parties_votes = {party: votes for party, votes in district_data.items() if party in election_data.eligible_parties}
    # Calculate the allocation of seats
    allocation = dhondt(parties_votes, seats)
    # Display the allocation of seats
    allocation_df = pd.DataFrame(list(allocation.items()), columns=['Partia', 'Mandaty'])
    allocation_df['Nazwa Partii'] = allocation_df['Partia'].map(abbreviations)
    allocation_df = allocation_df.sort_values(by='Mandaty', ascending=False)
    allocation_df['Kolor'] = allocation_df['Partia'].map(party_colors).fillna('gray')

    # Create a plot with squares representing seats
    fig, ax = plt.subplots(figsize=(15, 3))  # Adjust figure size
    seat_colors = []
    for party, row in allocation_df.iterrows():
        seat_colors.extend([row['Kolor']] * row['Mandaty'])
    for i in range(seats):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, color=seat_colors[i]))
    ax.set_xlim(0, seats)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title(f'Podział mandatów dla Okręgu {selected_district}')
    fig.tight_layout()  # Ensure the plot uses the available space
    st.pyplot(fig)
    # Display the allocation of seats
    st.write(allocation_df[['Nazwa Partii', 'Mandaty']])