import subprocess
import json
import time
import concurrent.futures
from find_bounties import FindBounties
from algorithm.pathfinder import Pathfinder

class BountyProcessor:
    def __init__(self):
        self.bounty_names = [
            "CARROTS", "SOAP", "RIBS", "MEAT_WRAP", "BEEF_JOINT", "CLOCKWORK_SHEEP",
            "PORCELAIN_DOLL", "PLATES", "PIN_BADGE", "PUMPKIN", "PIZZA", "BANANAS",
            "TIN_POCKET_WATCH", "HOMESPUN_CLOTH", "RAINBOW_CHEESE", "ARGANIAN_WINE",
            "OAK_PATTERNED_VASE", "SCENTED_CANDLE", "UNICORN_DUST", "LANDSCAPE_PAINTING",
            "CARRIAGE_CLOCK", "SPECTACLES", "SHARPSEED_WINE", "RUG", "CAVIAR", "BATH_SALTS",
            "TOMATOES", "STEAK", "BURGER", "HAM_LEG", "CLOCKWORK_DRAGON", "SNOW_GLOBE",
            "CUPS", "POSTCARDS", "RHUBARB", "CURRY", "ORANGES", "PRECISE_POCKET_WATCH",
            "SILK", "OLD_RARG", "FARGUST_WINE", "STRIPED_VASE", "TEA_LIGHTS", "UNICORN_HAIR",
            "PORTRAIT_PAINTING", "PENDULUM_CLOCK", "MONOCLE", "TOPHILL_WINE", "ANTIQUE_BOOK",
            "TRUFFLES"
        ]
        self.fbounties = FindBounties()

    def process(self, region, detective_level, battle_of_fortunehold_completed, inventory_space):
        bounties = []
        start_time = time.time()

        # Run bounty search concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.fbounties.find_item, bounty, region): bounty for bounty in self.bounty_names}

            for future in concurrent.futures.as_completed(futures):
                bounty = futures[future]
                try:
                    for i in range(future.result()):
                        bounties.append(bounty)
                except Exception as exc:
                    print(f"Error finding item {bounty}: {exc}")

        result = self._get_result(bounties, detective_level, battle_of_fortunehold_completed, inventory_space)
        elapsed_time = time.time() - start_time
        print(elapsed_time)
        return bounties, result, elapsed_time

    @staticmethod
    def _get_result(bounties, detective_level, battle_of_fortunehold_completed, inventory_space):
        return Pathfinder(inventory_space).find_best_bounties(
            bounties=bounties,
            detective_level=detective_level,
            battle_of_fortunehold_completed=battle_of_fortunehold_completed
        )
