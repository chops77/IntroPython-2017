#!/usr/bin/env python
"""
The command line interface to mailroom package.

The only code in here should deal with the command line interface.

Nothing to do with the logic code, etc that does the real work.
"""

import sys
import math

# handy utility to make pretty printing easier
from textwrap import dedent
import pathlib
from mailroom import model, data_dir

# create a DB with the sample data
# data_file = pathlib.Path(__file__).parent / "data" / "sample_data.json"
print("***\nloading sample data\n***")
db = model.DonorDB.load_from_file(data_dir / "sample_data.json")


def main_menu_selection():
    """
    Print out the main application menu and then read the user input.
    """
    action = input(dedent('''
      Choose an action:

      1 - Send a Thank You
      2 - Create a Report
      3 - Send letters to everyone
      4 - Quit

      > '''))
    return action.strip()


def send_thank_you():
    """
    Record a donation and generate a thank you message.
    """
    # Read a valid donor to send a thank you from, handling special commands to
    # let the user navigate as defined.
    while True:
        name = input("Enter a donor's name"
                     "(or 'list' to see all donors or 'menu' to exit)> ").strip()
        if name == "list":
            print(db.list_donors())
        elif name == "menu":
            return
        else:
            break

    # Now prompt the user for a donation amount to apply. Since this is
    # also an exit point to the main menu, we want to make sure this is
    # done before mutating the db.
    while True:
        amount_str = input("Enter a donation amount (or 'menu' to exit)> ").strip()
        if amount_str == "menu":
            return
        # Make sure amount is a valid amount before leaving the input loop
        try:
            amount = float(amount_str)
            # extra check here -- unlikely that someone will type "NaN", but
            # it IS possible, and it is a valid floating point number:
            # http://en.wikipedia.org/wiki/NaN
            if math.isnan(amount) or math.isinf(amount) or round(amount, 2) == 0.00:
                raise ValueError
        # in this case, the ValueError could be raised by the float() call, or by the NaN-check
        except ValueError:
            print("error: donation amount is invalid\n")
        else:
            break

    # If this is a new user, ensure that the database has the necessary
    # data structure.
    donor = db.find_donor(name)
    if donor is None:
        donor = db.add_donor(name)

    # Record the donation
    donor.add_donation(amount)
    print(db.gen_letter(donor))


def print_donor_report():
    print(db.generate_donor_report())


def quit():
    sys.exit(0)


def main():
    selection_dict = {"1": send_thank_you,
                      "2": print_donor_report,
                      "3": db.save_letters_to_disk,
                      "4": quit}

    while True:
        selection = main_menu_selection()
        try:
            selection_dict[selection]()
        except KeyError:
            print("error: menu selection is invalid!")

if __name__ == "__main__":

    main()
