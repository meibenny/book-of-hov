import csv
import json
import math
from decimal import Decimal

def load_cards(cards_file, config):
    include_list = set(config.get("include_cards", []))
    cards = {}
    with open(cards_file, encoding="utf-8-sig") as csvfile:
        cardreader = csv.DictReader(csvfile)
        for row in cardreader:
            if include_list and not str(row["card_id"]) in include_list:
                continue
            cards[row["card_id"]] = row["card"]
    return cards
    

def load_libraries(library_file, config):
    include_list = set(config.get("include_libraries", []))
    #[
    #    "22",
    #    "21",
    #    "45",
    #    "54",
    #    "14",
    #    "27",
    #    "28",
    #    "29",
    #    "7",
    #])
    library_card_map = {}
    with open(library_file, encoding="utf-8-sig") as csvfile:
        libraryreader = csv.DictReader(csvfile)
        for row in libraryreader:
            if not row["latitude"]:
                continue
            if include_list and not str(row["lib_id"]) in include_list:
                continue
            library_card_map[row["lib_id"]] = row
    return library_card_map

def distance(lat1, long1, lat2, long2):
    return math.sqrt((lat2 - lat1)**2 + (long2 - long1)**2)

def get_libraries_to_visit(cards_to_collect):
    libraries = []
    for card, libs in cards_to_collect.items():
        libraries.extend(libs)
    return libraries
            
def find_closest_library(current_location, libs_to_visit, libraries):

    min_distance = 10.0
    nearest_library_id = -1

    for library in libs_to_visit:
        this_library = libraries[library]
        lib_distance = distance(
            Decimal(current_location["latitude"]),
            Decimal(current_location["longitude"]),
            Decimal(this_library["latitude"]),
            Decimal(this_library["longitude"])
        )
        
        if lib_distance < min_distance:
            min_distance = lib_distance
            nearest_library_id = this_library["lib_id"]

    return nearest_library_id

def load_config(config_path):
    config = ""
    with open(config_path) as cfile:
        config = json.load(cfile)
    return config


def main():
    print("loading configuration...")
    config = load_config("config.json")
    print("loaded configuration")
    print("loading cards...")
    cards = load_cards("cards.csv", config)
    print(f"loaded {len(cards)} cards")

    print("loading libraries...")
    libraries = load_libraries("libraries.csv", config)
    print(f"loaded {len(libraries)} libraries")

    cards_to_collect = {}
    for card, _ in cards.items():
        cards_to_collect[card] = []

    for lib_id, library in libraries.items():
        try:
            cards_to_collect[library["card"]].append(library["lib_id"])
        except:
            continue
    
    starting_lib = libraries["22"]
    libraries_to_visit = get_libraries_to_visit(cards_to_collect)
    nearest_library_id = find_closest_library(starting_lib, libraries_to_visit, libraries)

    visited_libraries = [nearest_library_id]

    cards_to_collect.pop(libraries[nearest_library_id]["card"])
    max_iterations = len(cards_to_collect) + 10
    iterations = 0
    print("\n***********************")
    print("* simulating route... *")
    print("***********************\n")
    while len(cards_to_collect):
        iterations += 1
        if iterations > max_iterations:
            print("unsolvable")
            break
        latest_visited_library_id = visited_libraries[-1]
        latest_visited_library = libraries[latest_visited_library_id]
        print(f"Currently at library {latest_visited_library['name']}")
        libraries_to_visit = get_libraries_to_visit(cards_to_collect)

        nearest_library_id = find_closest_library(latest_visited_library, libraries_to_visit, libraries)
        if nearest_library_id == -1:
            print("\n***********************")
            print("* stopping simulation *")
            print("***********************\n")

            print(f"unable to collect all cards. {len(cards_to_collect)} remaining cards")
            for card, _ in cards_to_collect.items():
                print(cards[card])
            break

        print(f"Next stop {libraries[nearest_library_id]['name']}")
        visited_libraries.append(nearest_library_id)
        cards_to_collect.pop(libraries[nearest_library_id]["card"])

    print("\n******************")
    print("* shortest route *")
    print("******************\n")

    for library in visited_libraries:
        this_library = libraries[library]
        library_name = this_library["name"]
        card_name = cards[this_library["card"]]
        print(f"Library: {library_name} | Card: {card_name}")

main()
