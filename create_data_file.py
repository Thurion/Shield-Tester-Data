from __future__ import annotations
import os
import copy
import json
import csv
from typing import List, Dict, Tuple, Optional


PATH_TO_SHIPS = os.path.join(os.getcwd(), "coriolis-data", "ships")
PATH_TO_MODULES_STANDARD = os.path.join(os.getcwd(), "coriolis-data", "modules", "standard")
PATH_TO_SHIPYARD = os.path.join(os.getcwd(), "FDevIDs", "shipyard.csv")
PATH_TO_SHIELD_GENERATORS_NORMAL = os.path.join(os.getcwd(), "coriolis-data", "modules", "internal", "shield_generator.json")
PATH_TO_SHIELD_GENERATORS_PRISMATIC = os.path.join(os.getcwd(), "coriolis-data", "modules", "internal", "pristmatic_shield_generator.json")
PATH_TO_SHIELD_GENERATORS_BIWEAVE = os.path.join(os.getcwd(), "coriolis-data", "modules", "internal", "bi_weave_shield_generator.json")
PATH_TO_SHIELD_BOOSTER = os.path.join(os.getcwd(), "coriolis-data", "modules", "hardpoints", "shield_booster.json")

PATH_TO_ENGINEERING_BLUEPRINTS = os.path.join(os.getcwd(), "coriolis-data", "modifications", "blueprints.json")

PATH_TO_SHIELD_BOOSTER_ENGINEERING_SPECIALS = os.path.join(os.getcwd(), "coriolis-data", "modifications", "specials.json")
PATH_TO_SHIELD_BOOSTER_ENGINEERING_SPECIAL_ACTIONS = os.path.join(os.getcwd(), "coriolis-data", "modifications", "modifierActions.json")
MODULE_SHIELD_GENERATOR_ENGINEERING_SPECIALS = {"special_shield_regenerative",
                                                "special_shield_resistive",
                                                "special_shield_health",
                                                "special_shield_thermic",
                                                "special_shield_kinetic"}
MODULE_SHIELD_GENERATOR_ENGINEERING_BLUEPRINTS = {"ShieldGenerator_Kinetic",
                                                  "ShieldGenerator_Reinforced",
                                                  "ShieldGenerator_Thermic"}
MODULE_SHIELD_BOOSTER_ENGINEERING_BLUEPRINTS = {"ShieldBooster_HeavyDuty",
                                                "ShieldBooster_Kinetic",
                                                "ShieldBooster_Thermic",
                                                "ShieldBooster_Explosive",
                                                "ShieldBooster_Resistive"}
MODULE_SHIELD_BOOSTER_ENGINEERING_SPECIALS = {"special_shieldbooster_thermic",
                                              "special_shieldbooster_kinetic",
                                              "special_shieldbooster_explosive",
                                              "special_shieldbooster_chunky"}

MODULE_NAME_POWER_PLANT = "power plant"
MODULE_NAME_THRUSTERS = "thrusters"
MODULE_NAME_FSD = "fsd"
MODULE_NAME_LIFE_SUPPORT = "life support"
MODULE_NAME_POWER_DISTRIBUTOR = "power distributor"
MODULE_NAME_SENSORS = "sensors"
MODULE_NAME_FUEL_TANK = "fuel tank"
MODULES_STANDARD_FILE_NAMES = {MODULE_NAME_POWER_PLANT: "power_plant.json",
                               MODULE_NAME_THRUSTERS: "thrusters.json",
                               MODULE_NAME_FSD: "frame_shift_drive.json",
                               MODULE_NAME_LIFE_SUPPORT: "life_support.json",
                               MODULE_NAME_POWER_DISTRIBUTOR: "power_distributor.json",
                               MODULE_NAME_SENSORS: "sensors.json",
                               MODULE_NAME_FUEL_TANK: "fuel_tank.json"}


class Utilities:
    @staticmethod
    def generate_module_attributes(module_name, slot_name):
        return {"Item": module_name,
                "Slot": slot_name,
                "On": True,
                "Priority": 0}


class Ship:
    def __init__(self):
        self.name = ""
        self.symbol = ""
        self.highest_internal = 0
        self.utility_slots_amount = 0
        self.armour = ""
        self.power_plant = ""
        self.thrusters = ""
        self.frame_shift_drive = ""
        self.life_support = ""
        self.power_distributor = ""
        self.sensors = ""
        self.fuel_tank = ""
        self.base_shield_strength = 0
        self.hull_mass = 0

    def generate_data_entry(self):
        modules = list()
        loadout_template = {"event": "Loadout", "Ship": self.symbol, "Modules": modules}
        modules.append(Utilities.generate_module_attributes(self.armour, "armour"))
        modules.append(Utilities.generate_module_attributes(self.power_plant, "powerplant"))
        modules.append(Utilities.generate_module_attributes(self.thrusters, "mainengines"))
        modules.append(Utilities.generate_module_attributes(self.frame_shift_drive, "frameshiftdrive"))
        modules.append(Utilities.generate_module_attributes(self.life_support, "lifesupport"))
        modules.append(Utilities.generate_module_attributes(self.power_distributor, "powerdistributor"))
        modules.append(Utilities.generate_module_attributes(self.fuel_tank, "fueltank"))
        modules.append(Utilities.generate_module_attributes(self.sensors, "radar"))
        modules.append(Utilities.generate_module_attributes("int_planetapproachsuite", "planetaryapproachsuite"))
        modules.append(Utilities.generate_module_attributes("modularcargobaydoor", "cargohatch"))

        return {"ship": self.name,
                "symbol": self.symbol,
                "loadout_template": loadout_template,
                "baseShieldStrength": self.base_shield_strength,
                "hullMass": self.hull_mass,
                "utility_slots": self.utility_slots_amount,
                "highest_internal": self.highest_internal}

    @staticmethod
    def _extract_class_and_grade(s: str) -> Optional[Tuple[int, str]]:
        if len(s) != 2:
            return None
        else:
            return int(s[0]), s[1]

    @staticmethod
    def _search_standard_module(standard_modules: json, standard_string: str) -> Optional[str]:
        standard_modules = next(iter(standard_modules.values()))  # only 1 object containing a list per file
        module_class, module_grade = Ship._extract_class_and_grade(standard_string)
        for standard_module in standard_modules:
            if standard_module["class"] == module_class and standard_module["rating"] == module_grade:
                return standard_module["symbol"]
        return None

    @staticmethod
    def create_from_json(json_ships: json, standard_modules: Dict[str, json], ship_name_to_symbol: Dict[str, str]) -> Ship:
        """
        Create a ship object from coriolis data
        :param json_ships: The json object of the file, e.g. adder.json
        :param standard_modules: Default fitted modules as defined in coriolis-data/modules/standard/*
        :param ship_name_to_symbol: Dictionary containing the ship name as key and the internal identifier (symbol) as value
        :return: a Ship
        """
        json_ship = next(iter(json_ships.values()))  # only 1 ship per file
        ship = Ship()
        ship.name = json_ship["properties"]["name"]
        ship.symbol = ship_name_to_symbol.get(json_ship["properties"]["name"].lower())
        ship.base_shield_strength = json_ship["properties"]["baseShieldStrength"]
        ship.hull_mass = json_ship["properties"]["hullMass"]

        standards = json_ship["defaults"]["standard"]
        ship.power_plant = Ship._search_standard_module(standard_modules.get(MODULE_NAME_POWER_PLANT), standards[0])
        ship.thrusters = Ship._search_standard_module(standard_modules.get(MODULE_NAME_THRUSTERS), standards[1])
        ship.frame_shift_drive = Ship._search_standard_module(standard_modules.get(MODULE_NAME_FSD), standards[2])
        ship.life_support = Ship._search_standard_module(standard_modules.get(MODULE_NAME_LIFE_SUPPORT), standards[3])
        ship.power_distributor = Ship._search_standard_module(standard_modules.get(MODULE_NAME_POWER_DISTRIBUTOR), standards[4])
        ship.sensors = Ship._search_standard_module(standard_modules.get(MODULE_NAME_SENSORS), standards[5])
        ship.fuel_tank = Ship._search_standard_module(standard_modules.get(MODULE_NAME_FUEL_TANK), standards[6])
        ship.armour = "{}_armour_grade1".format(ship.symbol)

        ship.highest_internal = json_ship["slots"]["internal"][0]
        for hardpoint in json_ship["slots"]["hardpoints"]:
            if hardpoint == 0:
                ship.utility_slots_amount += 1

        return ship


class ShieldBooster:
    def __init__(self):
        self.symbol = ""
        self.engineering_name = ""
        self.engineering_symbol = ""
        self.experimental_name = ""
        self.experimental_symbol = ""
        self.integrity = 0
        self.power_draw = 0
        self.explres = 0
        self.kinres = 0
        self.thermres = 0
        self.mass = 0
        self.shield_boost = 0

    def apply_engineered(self, blueprint: json):
        self.engineering_name = blueprint["name"]
        self.engineering_symbol = blueprint["fdname"]
        grade_5_features = blueprint["grades"]["5"]["features"]

        if "integrity" in grade_5_features:
            self.integrity = self.integrity * (1 + grade_5_features["integrity"][1])
        if "power" in grade_5_features:
            self.power_draw = self.power_draw * (1 + grade_5_features["power"][1])
        if "mass" in grade_5_features:
            self.mass = self.mass * (1 + grade_5_features["mass"][1])
        if "shieldboost" in grade_5_features:
            self.shield_boost = (1 + self.shield_boost) * (1 + grade_5_features["shieldboost"][1]) - 1
        if "explres" in grade_5_features:
            self.explres = (1 + self.explres) * (1 + grade_5_features["explres"][1]) - 1
        if "kinres" in grade_5_features:
            self.kinres = (1 + self.kinres) * (1 + grade_5_features["kinres"][1]) - 1
        if "thermres" in grade_5_features:
            self.thermres = (1 + self.thermres) * (1 + grade_5_features["thermres"][1]) - 1

    def apply_experimental(self, experimental_symbol: str, specials: json, modifier_actions: json):
        self.experimental_name = specials[experimental_symbol]["name"]
        self.experimental_symbol = experimental_symbol

        special_modifier = modifier_actions[experimental_symbol]
        if "integrity" in special_modifier:
            self.integrity = self.integrity * (1 + special_modifier["integrity"])
        if "power" in special_modifier:
            self.power_draw = self.power_draw * (1 + special_modifier["power"])
        if "explres" in special_modifier:
            self.explres = 1 - (1 - self.explres) * (1 - special_modifier["explres"] / 100.0)
        if "kinres" in special_modifier:
            self.kinres = 1 - (1 - self.kinres) * (1 - special_modifier["kinres"] / 100.0)
        if "thermres" in special_modifier:
            self.thermres = 1 - (1 - self.thermres) * (1 - special_modifier["thermres"] / 100.0)
        if "mass" in special_modifier:
            self.mass = self.mass * (1 + special_modifier["mass"])
        if "shieldboost" in special_modifier:
            self.shield_boost = (1 + self.shield_boost) * (1 + special_modifier["shieldboost"]) - 1

        self.integrity = round(self.integrity, 4)
        self.power_draw = round(self.power_draw, 4)
        self.explres = round(self.explres, 4)
        self.kinres = round(self.kinres, 4)
        self.thermres = round(self.thermres, 4)
        self.mass = round(self.mass, 4)
        self.shield_boost = round(self.shield_boost, 4)

    def generate_data_entry(self, default_booster: ShieldBooster) -> Dict:
        modifiers = list()

        # create modifier for loadout template is they are changed
        if default_booster.integrity != self.integrity:
            modifiers.append({"Label": "Integrity",
                              "Value": self.integrity,
                              "OriginalValue": default_booster.integrity,
                              "LessIsGood": 0})
        if default_booster.power_draw != self.power_draw:
            modifiers.append({"Label": "PowerDraw",
                              "Value": self.power_draw,
                              "OriginalValue": default_booster.power_draw,
                              "LessIsGood": 1})
        if default_booster.shield_boost != self.shield_boost:
            modifiers.append({"Label": "DefenceModifierShieldMultiplier",
                              "Value": self.shield_boost * 100,
                              "OriginalValue": default_booster.shield_boost * 100,
                              "LessIsGood": 0})
        if default_booster.kinres != self.kinres:
            modifiers.append({"Label": "KineticResistance",
                              "Value": round(self.kinres * 100, 4),
                              "OriginalValue": default_booster.kinres * 100,
                              "LessIsGood": 0})
        if default_booster.thermres != self.thermres:
            modifiers.append({"Label": "ThermicResistance",
                              "Value": round(self.thermres * 100, 4),
                              "OriginalValue": default_booster.thermres * 100,
                              "LessIsGood": 0})
        if default_booster.explres != self.explres:
            modifiers.append({"Label": "ExplosiveResistance",
                              "Value": round(self.explres * 100, 4),
                              "OriginalValue": default_booster.explres * 100,
                              "LessIsGood": 0})

        loadout_template = Utilities.generate_module_attributes(self.symbol, "")  # slot is determined at runtime in shield tester
        loadout_template.setdefault("Engineering", {"BlueprintName": self.engineering_symbol,
                                                    "Level": 5,
                                                    "Quality": 1,
                                                    "Modifiers": modifiers,
                                                    "ExperimentalEffect": self.experimental_symbol})

        return {"engineering": self.engineering_name,
                "experimental": self.experimental_name,
                "shield_strength_bonus": self.shield_boost,
                "exp_res_bonus": self.explres,
                "kin_res_bonus": self.kinres,
                "therm_res_bonus": self.thermres,
                "can_skip": self.engineering_name.lower() == "Blast resistant".lower() or self.experimental_name.lower() == "Blast Block".lower(),
                "loadout_template": loadout_template}

    @staticmethod
    def create_engineered(default_booster: ShieldBooster, blueprint: json, specials: json, modifier_actions: json) -> List[ShieldBooster]:
        """
        Create relevant booster variations.
        :param default_booster: The default booster. It will be used as a prototype
        :param blueprint: The engineering blueprint
        :param specials: json containing all experimental descriptions (specials.json)
        :param modifier_actions: json containing all experimental efffects (modifierActions.json)
        :return: list of variations
        """
        variations = list()

        booster_prototype = copy.deepcopy(default_booster)
        booster_prototype.apply_engineered(blueprint)

        # create variations
        for special_name in MODULE_SHIELD_BOOSTER_ENGINEERING_SPECIALS:
            booster_variation = copy.deepcopy(booster_prototype)
            booster_variation.apply_experimental(special_name, specials, modifier_actions)
            variations.append(booster_variation)

        return variations

    @staticmethod
    def create_from_json(json_booster: json) -> ShieldBooster:
        """
        Create a new shield booster from json.
        :param json_booster: json object of the file coriolis-data/modules/hardpoints/shield_booster.json
        :return:
        """
        booster = ShieldBooster()
        booster.symbol = json_booster["symbol"]
        booster.integrity = json_booster["integrity"]
        booster.mass = json_booster["mass"]
        booster.power_draw = json_booster["power"]
        booster.shield_boost = json_booster["shieldboost"]
        booster.explres = json_booster["explres"]
        booster.kinres = json_booster["kinres"]
        booster.thermres = json_booster["thermres"]

        return booster


def load_shield_generators(filename):
    a_rated_generators = list()

    with open(filename, "r") as shield_generator_file:
        shield_generator_file_json = json.load(shield_generator_file)
        shield_generators = next(iter(shield_generator_file_json.values()))
        for shield_generator in shield_generators:
            # we only want A rated when not going through bi-weave shields
            if shield_generator["ukName"] != "Bi-Weave Shield" and shield_generator["rating"] != "A":
                continue
            a_rated_generators.append({"symbol": shield_generator["symbol"],
                                       "integrity": shield_generator["integrity"],
                                       "power": shield_generator["power"],
                                       "explres": shield_generator["explres"],
                                       "kinres": shield_generator["kinres"],
                                       "thermres": shield_generator["thermres"],
                                       "name": shield_generator["ukName"],
                                       "class": shield_generator["class"],
                                       "regen": shield_generator["regen"],
                                       "brokenregen": shield_generator["brokenregen"],
                                       "distdraw": shield_generator["distdraw"],
                                       "maxmass": shield_generator["maxmass"],
                                       "maxmul": shield_generator["maxmul"],
                                       "minmass": shield_generator["minmass"],
                                       "minmul": shield_generator["minmul"],
                                       "optmass": shield_generator["optmass"],
                                       "optmul": shield_generator["optmul"]})
    return a_rated_generators


def main():
    ships = list()
    standard_modules = dict()

    # default loadout for a ship
    for standard_module, file in MODULES_STANDARD_FILE_NAMES.items():
        with open(os.path.join(PATH_TO_MODULES_STANDARD, file)) as module_file:
            standard_modules.setdefault(standard_module, json.load(module_file))

    # ship name in game vs internal name
    ship_name_to_symbol = dict()
    ship_symbol_to_name = dict()
    with open(PATH_TO_SHIPYARD, "r") as shipyard_file:
        reader = csv.DictReader(shipyard_file)
        for row in reader:
            ship_name_to_symbol.setdefault(row["name"].lower(), row["symbol"])
            ship_symbol_to_name.setdefault(row["symbol"], row["name"])

    # ships
    for root, dirs, files in os.walk(PATH_TO_SHIPS):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), "r") as json_file:
                    ships.append(Ship.create_from_json(json.load(json_file), standard_modules, ship_name_to_symbol))

    with open(PATH_TO_ENGINEERING_BLUEPRINTS, "r") as blueprints_file:
        blueprints = json.load(blueprints_file)
    with open(PATH_TO_SHIELD_BOOSTER_ENGINEERING_SPECIALS, "r") as specials_file:
        engineering_specials = json.load(specials_file)
    with open(PATH_TO_SHIELD_BOOSTER_ENGINEERING_SPECIAL_ACTIONS, "r") as specials_actions_file:
        engineering_special_actions = json.load(specials_actions_file)

    # shield generators
    shield_generator_modules = {"bi-weave": load_shield_generators(PATH_TO_SHIELD_GENERATORS_BIWEAVE),
                                "prismatic": load_shield_generators(PATH_TO_SHIELD_GENERATORS_PRISMATIC),
                                "normal": load_shield_generators(PATH_TO_SHIELD_GENERATORS_NORMAL)}

    # blueprints for shield generators
    shield_generator_engineering_blueprints = list()
    for blueprint_symbol in MODULE_SHIELD_GENERATOR_ENGINEERING_BLUEPRINTS:
        # extract only the best value from the features
        features = dict()
        for k, v in blueprints[blueprint_symbol]["grades"]["5"]["features"].items():
            features.setdefault(k, v[1])
        sg_blueprint = {"symbol": blueprints[blueprint_symbol]["fdname"],
                        "features": features,
                        "name": blueprints[blueprint_symbol]["name"]}
        shield_generator_engineering_blueprints.append(sg_blueprint)

    # experimental effects for shield generators
    shield_generator_engineering_experimentals = list()
    for experimental_symbol in MODULE_SHIELD_GENERATOR_ENGINEERING_SPECIALS:
        experimental = {"symbol": engineering_specials[experimental_symbol]["edname"],
                        "name": engineering_specials[experimental_symbol]["name"],
                        "features": engineering_special_actions[experimental_symbol]}
        shield_generator_engineering_experimentals.append(experimental)

    # put all information about shield generators in 1 dictionary
    shield_generators = {"modules": shield_generator_modules,
                         "engineering": {"blueprints": shield_generator_engineering_blueprints,
                                         "experimental_effects": shield_generator_engineering_experimentals}
                         }

    # shield boosters
    shield_booster_variants = list()
    with open(PATH_TO_SHIELD_BOOSTER, "r") as boosters_file:
        booster_json = None
        for booster in next(iter(json.load(boosters_file).values())):
            if booster["rating"] == "A":
                booster_json = booster
                break
        shield_booster_default = ShieldBooster.create_from_json(booster_json)
        for blueprint_symbol in MODULE_SHIELD_BOOSTER_ENGINEERING_BLUEPRINTS:
                shield_booster_variants += ShieldBooster.create_engineered(shield_booster_default, blueprints.get(blueprint_symbol),
                                                                           engineering_specials, engineering_special_actions)

    data_entries_ships = list()
    for ship in ships:
        data_entries_ships.append(ship.generate_data_entry())

    # dictionary for output
    data_entries = {"ships": data_entries_ships,
                    "shield_booster_variants": [x.generate_data_entry(shield_booster_default) for x in shield_booster_variants],
                    "shield_generators": shield_generators}

    with open("data.json", "w+") as ship_data_file:
        json.dump(data_entries, ship_data_file, indent="  ")


if __name__ == '__main__':
    main()
