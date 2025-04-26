import pandas as pd
import math

class ElectionData:
    def __init__(self, votes_file, threshold_koalicyjny=0.08, threshold_mniejszosc=0.00, threshold_default=0.05):
        self.votes_file = votes_file
        self.threshold_koalicyjny = threshold_koalicyjny
        self.threshold_mniejszosc = threshold_mniejszosc
        self.threshold_default = threshold_default
        self.votes_df = pd.read_csv(self.votes_file, delimiter=';', encoding='utf-8-sig')
        self.total_votes = {}
        self.eligible_parties = []
        self.district_party_votes = {}

        self.store_district_party_votes()
        self.calculate_total_votes()
        self.determine_eligible_parties()


    def calculate_total_votes(self):
        for district in self.district_party_votes:
            for party, votes in self.district_party_votes[district].items():
                if party not in self.total_votes:
                    self.total_votes[party] = 0
                self.total_votes[party] += votes

    def determine_eligible_parties(self):
        total_votes_sum = sum(self.total_votes.values())
        for party, votes in self.total_votes.items():
            if "Koalicyjny" in party:
                threshold = self.threshold_koalicyjny
            elif "Mniejszość" in party:
                threshold = self.threshold_mniejszosc
            else:
                threshold = self.threshold_default

            if votes / total_votes_sum >= threshold and party not in self.eligible_parties:
                self.eligible_parties.append(party)

    def store_district_party_votes(self):
        for _, row in self.votes_df.iterrows():
            district_nr = row['Nr okr.']
            if district_nr not in self.district_party_votes:
                self.district_party_votes[district_nr] = {}
            for key in row.keys():
                if ' - ' in key:
                    try:
                        value = float(str(row[key]).replace(' ', ''))
                        self.district_party_votes[district_nr][key] = int(value)
                    except ValueError:
                            if math.isnan(row[key]):
                                pass
                            else:
                                raise
    def recalculate(self):
        self.total_votes = {}
        self.eligible_parties = []
        self.calculate_total_votes()
        self.determine_eligible_parties()
