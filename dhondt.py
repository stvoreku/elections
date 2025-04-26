"""This module implements the D'Hondt method for apportionment of seats in a voting system."""

import math
from typing import List, Dict, Tuple, Any

# this method takes dictionary of party and its votes and returns a dict of party and its seats
def dhondt(votes: Dict[str, int], seats: int) -> Dict[str, int]:
    """
    Calculate the apportionment of seats using the D'Hondt method.

    :param votes: A dictionary where keys are party names and values are the number of votes received.
    :param seats: The total number of seats to be apportioned.
    :return: A dictionary where keys are party names and values are the number of seats allocated.
    """
    # Initialize a dictionary to hold the number of seats for each party
    apportionment = {party: 0 for party in votes.keys()}

    # Create a list of tuples (party, votes) sorted by votes in descending order
    sorted_votes = sorted(votes.items(), key=lambda item: item[1], reverse=True)

    # Create a list to hold the quotients for each party
    quotients = [(party, votes) for party, votes in sorted_votes]

    # Loop until all seats are apportioned
    for _ in range(seats):
        # Find the party with the highest quotient
        party, quotient = max(quotients, key=lambda x: x[1])

        # Allocate a seat to that party
        apportionment[party] += 1

        # Update the quotient for that party
        new_quotient = votes[party] / (apportionment[party] + 1)

        # Update the quotients list
        quotients = [(p, new_quotient if p == party else q) for p, q in quotients]


    return apportionment