def test_dhondt():
    from dhondt import dhondt

    # Define the parties and their votes
    parties = {"Party A": 100, "Party B": 80, "Party C": 60, "Party D": 40, "Party E": 20}
    # Define the number of seats
    seats = 5

    # Calculate the allocation of seats
    allocation = dhondt(parties, seats)
    expected_allocation = {
        "Party A": 2,
        "Party B": 2,
        "Party C": 1,
        "Party D": 0,
        "Party E": 0
    }

    # Check if the allocation matches the expected allocation
    assert allocation == expected_allocation, f"Expected {expected_allocation}, but got {allocation}"

def test_dhondt_not_sorted_20_seats():
    from dhondt import dhondt

    # Define the parties and their votes
    parties = {"Party A": 2137, "Party B": 420, "Party C": 8123, "Party D": 3544, "Party E": 6200}
    # Define the number of seats
    seats = 20

    # Calculate the allocation of seats
    allocation = dhondt(parties, seats)
    expected_allocation = {
        "Party A": 2,
        "Party B": 0,
        "Party C": 9,
        "Party D": 3,
        "Party E": 6
    }

    # Check if the allocation matches the expected allocation
    assert allocation == expected_allocation, f"Expected {expected_allocation}, but got {allocation}"

def test_dhondt_13_seats_thousends():
    from dhondt import dhondt

    # Define the parties and their votes
    parties = {"Party A": 69700, "Party B": 21332, "Party C": 70100, "Party D": 5333, "Party E": 31000}
    # Define the number of seats
    seats = 13

    # Calculate the allocation of seats
    allocation = dhondt(parties, seats)
    expected_allocation = {
        "Party A": 5,
        "Party B": 1,
        "Party C": 5,
        "Party D": 0,
        "Party E": 2
    }

    # Check if the allocation matches the expected allocation
    assert allocation == expected_allocation, f"Expected {expected_allocation}, but got {allocation}"