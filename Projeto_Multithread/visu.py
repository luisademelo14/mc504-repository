import time
import os
import re

HACKER_SYMBOL = "(^.^)"
SERF_SYMBOL = "(◣_◢)"

BOAT_ART = [
    "     __/__",
    " ___/_____\\___",
    " \\___________/",
    "     ~  ~"
]

MAP_TEMPLATE = [
    "________.,,,,,,.:*S%*                         ~         +%S*;,,.,,,,,,,,,,,,,,,,",
    "________.,,,,.:?S*     ~            ~                 :S%;,.,,,,,,,,,,,,,,,,,,,,",
    "________.,,,,*S*                                     :S+.,,,,,,,,,,,,,,,,,,,,,,,",
    "________,,,,SS,                                     .?*.,,,,,,,,,,,,,,,,,,,,,,,,",
    "________.,,%?                    ~                  ;S,,,,,,,,,,,,,,,,,,,,,,,,,,",
    "________..*%,                                      .*?.,,,,,,,,,,,,,,,,,,,,,,,,,",
    "________.,S:                                        :S*,.,,,,,,,,,,,,,,,,,,,,,,,",
    "________.*?.                                        .:SS+,,,,,,,,,,,,,,,,,,,,,,,",
    "________.S:                                          :;;SS;.,,,,,,,,,,,,,,,,,,,,,",
    "________:S                                            +.,+S?:,,,,,,,,,,,,,,,,,,,,",
    "________;%.                                           *;.,,*S;,,,,,,,,,,,,,,,,,,,",
    "________;%,   ~                                        *+,,.+S,,,,,,,,,,,,,,,,,,,",
    "________:%;.                                     ~      **,,%;.,,,,,,,,,,,,,,,,,,",
    "________+:S;.     ~                                      +?:S%+:,,,,,,,,,,,,,,,,,",
    "________?.;S+                                      ~     .:?**%#?,,,,,,,,,,,,,,,,",
    "________S,.:SS:.         ~               ~                  +?,,?S:,,,,,,,,,,,,,,",
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

    if boat_x is not None:
        boat_y = 8  
        for i, line in enumerate(BOAT_ART):
            if boat_y + i < len(map_copy):
                row = map_copy[boat_y + i]
                for j, c in enumerate(line):
                    if 0 <= boat_x + j < len(row):
                        row[boat_x + j] = c

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

def animate_boat(people_positions, person_info):
    for boat_x in range(10, 50, 3):
        draw_map(people_positions, person_info, [], None, False, boat_x=boat_x)

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
            draw_map(people_positions, person_info, boat, captain, False)
            animate_boat(people_positions, person_info)
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

        elif "Boarding..." in line:
            id_ = int(line.split()[0])
            for pid in waiting_list:
                if person_info[pid]["id"] == id_:
                    boat.append(person_info[pid])
                    if pid in people_positions:
                        del people_positions[pid]  
                    waiting_list.remove(pid)
                    break
                    

        elif "captain" in line.lower():
            captain = int(re.findall(r"\d+", line)[0])

        elif "rowing" in line.lower():
            
            draw_map(people_positions, person_info, boat, captain, False)
            time.sleep(0.8)

            id_ = int(line.split()[0])
            for pid in waiting_list:
                if person_info[pid]["id"] == id_:
                    boat.append(person_info[pid])
                    if pid in people_positions:
                        del people_positions[pid]  
                    waiting_list.remove(pid)
                    break

            animate_boat(people_positions, person_info)

            boat = []
            captain = None
            continue  

        draw_map(people_positions, person_info, boat, captain, False)


if __name__ == "__main__":
    parse_log("output.txt")
