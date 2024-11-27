import json
from algorithm.nodes import markets

class Bounties:
    bounties = {}

    @classmethod
    def read_file(cls, file_path="app/data/bounties_data.json"):
        """Reads bounty data from the JSON file and returns it as a dictionary."""
        with open(file_path, "r") as file:
            # Load the JSON data from the file
            bounties_data = json.load(file)

        # Replace the seller and buyer market names with actual market data
        for bounty_name, bounty_info in bounties_data.items():
            seller = bounty_info.get("seller")
            buyer = bounty_info.get("buyer")

            # Ensure that the seller and buyer fields are properly mapped from strings to market objects
            bounty_info["seller"] = markets.get(seller, None)
            bounty_info["buyer"] = markets.get(buyer, None)

        # Store the bounty data in the static bounties attribute
        cls.bounties = bounties_data

    @staticmethod
    def get_bounty(name):
        """Retrieve a specific bounty by name."""
        if not Bounties.bounties:
            Bounties.read_file()

        return Bounties.bounties.get(name)
