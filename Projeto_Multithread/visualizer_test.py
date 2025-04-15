import time
import os
import re

HACKER_SYMBOL = "(^.^)"
SERF_SYMBOL = "(◣_◢)"

BOAT_ART = [
    "         __/___",
    "  ______/______\\_______",
    "  \\                   /",
    "   \\                 /",
    " ~~ ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾",
    "  ~~~  ~~~   ~  ~ ~~~",
    "     ~~~   ~~~",
]

MAP_TEMPLATE = [
    "________.,,,,,,.:*S%*                               ~         +%S*;,,.,,,,,,,,,,,,,,,,",
    "________.,,,,.:?S*     ~                ~                   :S%;,.,,,,,,,,,,,,,,,,,,,,",
    "________.,,,,*S*                                           :S+.,,,,,,,,,,,,,,,,,,,,,,,",
    "________,,,,SS,                                           .?*.,,,,,,,,,,,,,,,,,,,,,,,,",
    "________.,,%?                        ~                    ;S,,,,,,,,,,,,,,,,,,,,,,,,,,",
    "________..*%,                                            .*?.,,,,,,,,,,,,,,,,,,,,,,,,,",
    "________.,S:    ~                                         :S*,.,,,,,,,,,,,,,,,,,,,,,,,",
    "________.*?.                                              .:SS+,,,,,,,,,,,,,,,,,,,,,,,",
    "________.S:                                                :;;SS;.,,,,,,,,,,,,,,,,,,,,,",
    "________:S                                                  +.,+S?:,,,,,,,,,,,,,,,,,,,,",
    "________;%.                                                 *;.,,*S;,,,,,,,,,,,,,,,,,,,",
    "________;%,                                                  *+,,.+S,,,,,,,,,,,,,,,,,,,",
    "________:%;.                                                  **,,%;.,,,,,,,,,,,,,,,,,,",
    "________+:S;.     ~                                            +?:S%+:,,,,,,,,,,,,,,,,,",
    "________?.;S+                                            ~     .:?**%#?,,,,,,,,,,,,,,,,",
    "________S,.:SS:.                             ~                    +?,,?S:,,,,,,,,,,,,,,",
]

HACKER_X = 0
SERF_X = 0
START_Y = 0  

def draw_map(people_positions, person_info, boat, captain, rowing, boat_x=None):
    map_copy = [list(row) for row in MAP_TEMPLATE]

    for person_id, (y, x) in people_positions.items():
        person = person_info[person_id]
        symbol = HACKER_SYMBOL if person['type'] == 'Hacker' else SERF_SYMBOL
        for i, c in enumerate(symbol):
            if 0 <= x + i < len(map_copy[y]):
                map_copy[y][x + i] = c

    boat_art = draw_passengers_in_boat(boat)

    if boat_x is not None:
        animate_boat(map_copy, boat_art, boat_x)

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("RIVER CROSSING - ASCII VISUALIZER")
    print("=" * 60)

    for row in map_copy:
        print("".join(row))

    print("\nBOAT STATUS:")
    for p in boat:
        sym = HACKER_SYMBOL if p["type"] == "Hacker" else SERF_SYMBOL
        print(f"{sym} #{p['id']}")
    if captain is not None:
        print(f"👨‍✈️ Captain: #{captain}")
    if rowing:
        print("🚣 Boat is ROWING!\n")
    print("=" * 60)
    time.sleep(0.6)


def animate_boat(map, boat_art, boat_x):
    boat_y = 8
    for i, line in enumerate(boat_art):
        # Check if the boat fits in the map
        if boat_y + i < len(map):
            # Get the current row of the map
            row = map[boat_y + i]
            # Iterate through the characters of the boat line
            for j, c in enumerate(line):
                # Check if the character fits in the row
                if 0 <= boat_x + j < len(row):
                    # Place the character in the map
                    row[boat_x + j] = c


def draw_passengers_in_boat(boat):
    symbols = [HACKER_SYMBOL if p["type"] == "Hacker" else SERF_SYMBOL for p in boat]
    symbols = symbols[:4] + [""] * (4 - len(symbols))

    line3 = "  \\   {:^5}   {:^5}   /".format(symbols[0], symbols[1])
    line4 = "   \\  {:^5}   {:^5}  /".format(symbols[2], symbols[3])

    filled_art = BOAT_ART[:]
    filled_art[2] = line3
    filled_art[3] = line4
    return filled_art


def board_passengers(lines, start_index, waiting_list, people_positions, person_info, boat, captain):
    i = start_index

    while i < len(lines):
        line = lines[i].strip()

        if "captain" in line.lower():
            captain = int(re.findall(r"\d+", line)[0])

        if "rowing" in line.lower():
            # Último draw antes de cruzar o rio
            draw_map(people_positions, person_info, boat, captain, True, boat_x=10)
            time.sleep(0.5)
            break

        elif "Boarding..." in line:
            id_ = int(line.split()[0])
            for pid in waiting_list:
                if person_info[pid]["id"] == id_:
                    boat.append(person_info[pid])
                    if pid in people_positions:
                        del people_positions[pid]
                    waiting_list.remove(pid)
                    break
            draw_map(people_positions, person_info, boat, captain, False, boat_x=10)

        i += 1

    return captain, i  # retorna o novo índice para continuar o parse


def cross_river(people_positions, person_info, boat, captain):
    for boat_x in range(10, 45, 3):
        draw_map(people_positions, person_info, boat, captain, True, boat_x=boat_x)


def parse_log(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    people_positions = {}
    person_info = {}
    waiting_list = []
    boat = []
    captain = None
    current_y = START_Y
    pending_rowing = False

    for idx, line in enumerate(lines):
        line = line.strip()

        if line in ["ALL HACKERS", "ALL SERFS", "SERF: METADE CADA!!", "HACKER: METADE CADA!!"]:
            idx, captain = board_passengers(lines, idx + 1, waiting_list, people_positions, person_info, boat, captain)
            cross_river(people_positions, person_info, boat, captain)
            boat = []
            captain = None
            continue

        if "is waiting on queue" in line:
            type_ = "Serf" if "Serf" in line else "Hacker"
            id_ = int(re.findall(r"\d+", line)[0])
            person_id = f"{type_}#{id_}"
            person = {"type": type_, "id": id_}
            person_info[person_id] = person
            waiting_list.append(person_id)

            y = current_y % len(MAP_TEMPLATE)
            x = HACKER_X if type_ == "Hacker" else SERF_X
            people_positions[person_id] = (y, x)
            current_y += 1

        draw_map(people_positions, person_info, boat, captain, False)


if __name__ == "__main__":
    parse_log("output.txt")