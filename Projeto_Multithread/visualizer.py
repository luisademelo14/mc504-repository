import os
import re
import time

HACKER_SYMBOL = "(^.^)"
SERF_SYMBOL = "(◣_◢)"

BOAT_ART = [
    "         __\___           ",
    "        /      \\         ",
    "  \\‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾/",
    "   \\                   / ",
    " ~~ ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾   ",
    "  ~~~  ~~~   ~  ~ ~~~     ",
    "     ~~~   ~~~            ",
]

MAP_TEMPLATE = [
    "________.,,,,,,.:*S%*                               ~                     +%S*;,,.,,,,,",
    "________.,,,,.:?S*     ~                ~                               :S%;,.,,,,,,,,,",
    "________.,,,,*S*                                                       :S+.,,,,,,,,,,,,",
    "________,,,,SS,                                                       .?*.,,,,,,,,,,,,,",
    "________.,,%?                        ~                                ;S,,,,,,,,,,,,,,,",
    "________..*%,                                                        .*?.,,,,,,,,,,,,,,",
    "________.,S:    ~                                                     :S*,.,,,,,,,,,,,,",
    "________.*?.                                                          .:SS+,,,,,,,,,,,,",
    "________.S:                                                            :;;SS;.,,,,,,,,,",
    "________:S                                                              +.,+S?:,,,,,,,,",
    "________;%.                                                             *;.,,*S;,,,,,,,",
    "________;%,                                                              *+,,.+S,,,,,,,",
    "________:%;.                                                              **,,%;.,,,,,,",
    "________+:S;.     ~                                                        +?:S%+:,,,,,",
    "________?.;S+                                                        ~     .:?**%#?,,,,",
    "________S,.:SS:.                             ~                                +?,,?S:,,",
]

HACKER_X = 0
SERF_X = 0
START_Y = 0  


class Person:
    """ Class representing a person in the river crossing simulation."""
    def __init__(self, type_: str, id_: int) -> None:
        """ Initialize a person with a type and ID. """
        self.type = type_
        self.id = id_
        self.symbol = HACKER_SYMBOL if self.type == "Hacker" else SERF_SYMBOL
        self.position = None


class Boat:
    """ Class representing the boat in the river crossing simulation."""
    def __init__(self) -> None:
        """ Initialize the boat with no passengers and no captain. """
        self.clear()

    def board(self, person: Person) -> None:
        """ Board a person onto the boat. """
        self.passengers.append(person)

    def clear(self) -> None:
        """ Clear the boat's passengers and captain. """
        self.passengers = []
        self.captain_id = None
        self.automatic = False

    def draw_boat(self) -> list:
        """
        Draw the boat with its passengers.
        Returns a list of strings representing the boat's ASCII art.
        """
        symbols = [p.symbol for p in self.passengers]
        symbols = symbols[:4] + [""] * (4 - len(symbols))
        boat = BOAT_ART[:]

        # Captain's hat
        if self.passengers is not None and len(self.passengers) > 0:
            if self.passengers[0].type == "Hacker":
                boat[0] = "         __\___  __M__  "
            else:
                boat[0] = "         __\___  __A__  "

        # All hackers
        if all(p.type == "Hacker" for p in self.passengers) and len(self.passengers) == 4:
            boat[1] = f"        /  ☠️   \\ {symbols[0]:^5}"
        elif all(p.type == "Serf" for p in self.passengers) and len(self.passengers) == 4:
            boat[1] = f"        /  🪟   \\ {symbols[0]:^5}"
        elif self.automatic:
            boat[1] = f"        /  🦆   \\   {chr(0)}{chr(0)}🤖"
        else:
            boat[1] = f"        /      \\ {symbols[0]:^5}"

        # Rest of the crew
        boat[3] = f"   \\ {symbols[1]:^5} {symbols[2]:^5} {symbols[3]:^5} /"

        return boat


class RiverMap:
    """ Class representing the river map in the simulation."""
    def __init__(self) -> None:
        """ Initialize the river map with a template. """
        self.template = [list(row) for row in MAP_TEMPLATE]

    def draw(self,
             waiting_list: list,
             boat: Boat,
             rowing: bool = False,
             boat_x: int = None,
             boat_y: int = 8,
             returning: bool = False) -> None:
        """ Draw the river map with the current state of the simulation. """
        map_copy = [row.copy() for row in self.template]

        # Draw people
        for person in waiting_list:
            symbol = person.symbol
            x, y = person.position
            for i, c in enumerate(symbol):
                if 0 <= x + i < len(map_copy[y]):
                    map_copy[y][x + i] = c

        # Draw boat
        if boat_x is not None:
            boat_art = boat.draw_boat()
            self.animate_boat(map_copy, boat_art, boat_x, boat_y)

        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 60)
        print("RIVER CROSSING - ASCII VISUALIZER")
        print("=" * 60)

        # Print map
        for row in map_copy:
            print("".join(row))

        # Print log
        print("\nBOAT STATUS:")
        for p in boat.passengers:
            print(f"{p.symbol} #{p.id}")
        if boat.captain_id:
            print(f"👨‍✈️ Captain: #{boat.captain_id}")
        if rowing:
            print("🚣 Boat is ROWING!\n")
        if returning:
            print("🤖 Boat is RETURNING!\n")
        print("=" * 60)
        time.sleep(0.4 if not returning else 0.1)

    def animate_boat(self, map: list, boat_art: list, boat_x: int, boat_y: int = 8) -> None:
        """ Animate the boat on the map. """
        for i, line in enumerate(boat_art):
            if boat_y + i < len(map):
                row = map[boat_y + i]
                for j, c in enumerate(line):
                    if 0 <= boat_x + j < len(row):
                        row[boat_x + j] = c


class RiverCrossingSimulator:
    """ Class representing the river crossing simulation. """
    def __init__(self, filepath: str) -> None:
        """ Initialize the simulator with a file path. """
        self.filepath = filepath
        self.map = RiverMap()
        self.boat = Boat()
        self.waiting_list = []

    def parse(self) -> None:
        """ Parse the log file and simulate the river crossing. """
        with open(self.filepath, 'r') as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            line = line.strip()

            if line in ["ALL HACKERS", "ALL SERFS", "SERF: METADE CADA!!", "HACKER: METADE CADA!!"]:
                idx = self._handle_boarding(lines, idx + 1)
                self._update_queue_positions()
                self._cross_river()
                self._handle_disembark()
                self.boat.clear()
                self._new_boat()
                continue

            if "is waiting on queue" in line:
                self._add_to_queue(line)

            self.map.draw(self.waiting_list, self.boat, boat_x=10, rowing=False)

    def _handle_boarding(self, lines: list, start_idx: int) -> int:
        """ Handle the boarding process of the boat. Return the next index to process. """
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()

            if "captain" in line.lower():
                self.boat.captain_id = int(re.findall(r"\d+", line)[0])

            if "rowing" in line.lower():
                self.map.draw(self.waiting_list, self.boat, boat_x=10, rowing=True)
                time.sleep(0.6)
                break

            elif "Boarding..." in line:
                person_id = int(line.split()[0])
                person = next((p for p in self.waiting_list if p.id == person_id), None)
                if person:
                    self.boat.board(person)
                    self.waiting_list.remove(person)
                self.map.draw(self.waiting_list, self.boat, boat_x=10)

            i += 1
        return i

    def _handle_disembark(self) -> None:
        """ Handle the disembarking process of the boat. """
        for i in range(3, -1, -1):
            if self.boat.passengers[i] is not None:
                person = self.boat.passengers[i]
                self.boat.passengers.remove(person)
                self.map.draw(self.waiting_list, self.boat, boat_x=45)
            self.map.draw(self.waiting_list, self.boat, boat_x=45)

    def _update_queue_positions(self) -> None:
        """ Update the positions of people in the queue. """
        y = START_Y
        for person in self.waiting_list:
            x = HACKER_X if person.type == "Hacker" else SERF_X
            person.position = (x, y)
            y += 1

    def _add_to_queue(self, line: str) -> None:
        """ Add a person to the waiting list based on the log line. """
        type_ = "Serf" if "Serf" in line else "Hacker"
        id_ = int(re.findall(r"\d+", line)[0])
        person = Person(type_, id_)
        self.waiting_list.append(person)
        self._update_queue_positions()

    def _cross_river(self) -> None:
        """ Simulate the crossing of the river. """
        for boat_x in range(10, 45, 3):
            self.map.draw(self.waiting_list, self.boat, rowing=True, boat_x=boat_x)

    def _new_boat(self) -> None:
        """ Simulate the arrival of a new boat. """
        self.boat.automatic = True
        for boat_y in range(8, -1, -1):
            self.map.draw(self.waiting_list, self.boat, boat_x=45, boat_y=boat_y, returning=True)
        for boat_x in range(45, 9, -2):
            self.map.draw(self.waiting_list, self.boat, rowing=False, boat_x=boat_x, boat_y=0, returning=True)
        for boat_y in range(0, 9):
            self.map.draw(self.waiting_list, self.boat, boat_x=10, boat_y=boat_y, returning=True)
        self.boat.clear()

if __name__ == "__main__":
    try:
        sim = RiverCrossingSimulator("log.txt")
    except FileNotFoundError:
        sim = RiverCrossingSimulator("exemplo_out.txt")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    sim.parse()