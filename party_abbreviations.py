import re

# Explicit mapping of party names to abbreviations
party_abbreviations = {
    '1 - Komitet Wyborczy Prawo i Sprawiedliwość': 'PiS',
    '2 - Komitet Wyborczy Platforma Obywatelska RP': 'PO',
    '8 - Komitet Wyborczy Nowoczesna Ryszarda Petru': 'N.',
    '6 - Koalicyjny Komitet Wyborczy Zjednoczona Lewica SLD+TR+PPS+UP+Zieloni': 'ZL',
    '7 - Komitet Wyborczy Wyborców „Kukiz\'15”': 'K15',
    '4 - Komitet Wyborczy KORWiN': 'KORWiN',
    '3 - Komitet Wyborczy Partia Razem': 'Razem',
    '5 - Komitet Wyborczy Polskie Stronnictwo Ludowe': 'PSL',
}

def generate_abbreviation(party_name):
    # Step 1: Drop the number and dash from the beginning
    party_name = re.sub(r'^\d+ - ', '', party_name)

    # Step 2: Drop "Komitet Wyborczy" and "Komitet Koalicyjny"
    party_name = re.sub(r'Komitet Wyborczy|Komitet Koalicyjny|Komitet Wyborczy Wyborców', '', party_name, flags=re.IGNORECASE)

    # Step 3: Use the first letter of each word, keep numbers as a whole
    words = party_name.split()
    abbreviation = ''.join([word[0] if word.isalpha() else word for word in words])

    # Step 4: Drop any special symbols
    abbreviation = re.sub(r'[^A-Za-z0-9]', '', abbreviation)

    return abbreviation.upper()

def get_party_abbreviation(party_name):
    # Check if the party name is in the explicit mapping
    if party_name in party_abbreviations:
        return party_abbreviations[party_name]
    # Otherwise, generate the abbreviation
    return generate_abbreviation(party_name)