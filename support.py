from csv import reader

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:  # level_map is a TextIOWrapper
        layout = reader(level_map, delimiter = ',')  # layout is a csv.reader object
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map