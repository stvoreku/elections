import csv
from dhondt import dhondt

DISTRICTS_SEATS = {}
RESULTS_PER_DISTRICT = {}
TOTAL_VOTES = {}

# Read csv file where first column is a key, and the second is a value and create a dict out of it:
with open('okregi-mandaty.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        DISTRICTS_SEATS[row['Nr']] = int(row['LM'])

assert sum(DISTRICTS_SEATS.values()) == 460

# Read the votes from the csv file and calculate total votes for each party
with open('2015-gl-lis-okr.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        for key in row.keys():
            if ' - ' in key:
                try:
                    votes = int(row[key].replace(' ', ''))
                    if key not in TOTAL_VOTES:
                        TOTAL_VOTES[key] = 0
                    TOTAL_VOTES[key] += votes
                except ValueError:
                    pass

# Calculate the total number of votes
total_votes = sum(TOTAL_VOTES.values())

# Determine which parties meet the threshold
eligible_parties = {}
for party, votes in TOTAL_VOTES.items():
    if "Koalicyjny" in party:
        threshold = 0.08
    elif "Mniejszość" in party:
        threshold = 0.00
    else:
        threshold = 0.05

    if votes / total_votes >= threshold:
        eligible_parties[party] = votes

print(f"Parties that met the threshold: {eligible_parties.keys()}")

# Calculate the seats for each district using only eligible parties
with open('2015-gl-lis-okr.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        district_nr = row['Nr okr.']
        seats = DISTRICTS_SEATS[district_nr]
        parties_votes = {}
        for key in row.keys():
            if key in eligible_parties:
                try:
                    parties_votes[key] = int(row[key].replace(' ', ''))
                except ValueError:
                    pass
        RESULTS_PER_DISTRICT[district_nr] = dhondt(parties_votes, seats)

# Go over the RESULTS_PER_DISTRICT and sum the votes for each party globally
global_results = {}
for district, results in RESULTS_PER_DISTRICT.items():
    for party, seats in results.items():
        if party not in global_results:
            global_results[party] = 0
        global_results[party] += seats

print(global_results)
# Check if sum of global_results is equal to 460
assert sum(global_results.values()) == 460