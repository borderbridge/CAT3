"""
CAT3 Catalog Imports - Messier, NGC, Caldwell Kataloge
Datenquellen: Standard astronomical catalogs
"""
import sqlite3
from typing import List, Dict, Any
from db import insert_object, get_conn

# ============================================================================
# MESSIER KATALOG
# ============================================================================

MESSIER_OBJECTS = [
    # Nr,  Name,                  Typ,              RA(h m s),      DEC(d m s),     Mag,   Größe(arcmin), Sternbild
    (1,   "Krebsnebel",           "supernova_remnant",  5, 34, 32,      22, 0, 52,     8.4,   6.0,   "Taurus"),
    (2,   "Kugelsternhaufen M2",  "globular_cluster",  21, 33, 27,     -0, 49, 24,    6.3,   16.0,  "Aquarius"),
    (3,   "Kugelsternhaufen M3",  "globular_cluster",  13, 42, 11,     28, 22, 38,    6.2,   18.0,  "Canes Venatici"),
    (4,   "Kugelsternhaufen M4",  "globular_cluster",  16, 23, 35,     -26, 31, 32,   5.9,   36.0,  "Scorpius"),
    (5,   "Kugelsternhaufen M5",  "globular_cluster",  15, 18, 33,     2, 5, 58,      6.0,   23.0,  "Serpens"),
    (6,   "Schmetterlingshaufen", "open_cluster",      17, 40, 20,     -32, 15, 15,   4.2,   25.0,  "Scorpius"),
    (7,   "Ptolemäus-Haufen",     "open_cluster",      17, 53, 51,     -34, 49, 0,    3.3,   80.0,  "Scorpius"),
    (8,   "Lagunennebel",         "nebula",            18, 3, 37,       -24, 23, 12,   6.0,   90.0,  "Sagittarius"),
    (11,  "Entenhaufen",          "open_cluster",      18, 51, 5,      -6, 16, 12,    5.8,   14.0,  "Scutum"),
    (13,  "Herkuleshaufen",       "globular_cluster",  16, 41, 41,     36, 27, 37,    5.8,   20.0,  "Hercules"),
    (15,  "Kugelsternhaufen M15", "globular_cluster",  21, 29, 58,     12, 10, 0,     6.2,   18.0,  "Pegasus"),
    (16,  "Adlernebel",           "nebula",            18, 18, 48,     -13, 47, 24,   6.4,   7.0,   "Serpens"),
    (17,  "Omeganebel",          "nebula",            18, 20, 47,     -16, 10, 18,   6.0,   46.0,  "Sagittarius"),
    (20,  "Trifidnebel",         "nebula",            18, 2, 23,       -23, 1, 48,    6.3,   28.0,  "Sagittarius"),
    (27,  "Hantelnebel",         "planetary_nebula",  19, 59, 36,     22, 43, 16,    7.5,   8.0,   "Vulpecula"),
    (31,  "Andromedagalaxie",     "galaxy",            0, 42, 44,       41, 16, 9,     3.4,   178.0, "Andromeda"),
    (42,  "Orionnebel",          "nebula",            5, 35, 17,       -5, 23, 28,    4.0,   85.0,  "Orion"),
    (43,  "M43",                 "nebula",            5, 35, 31,       -5, 16, 3,     9.0,   20.0,  "Orion"),
    (44,  "Praesepe",            "open_cluster",      8, 40, 24,       19, 59, 0,     3.1,   95.0,  "Cancer"),
    (45,  "Plejaden",            "open_cluster",      3, 47, 0,        24, 7, 0,      1.6,   110.0, "Taurus"),
    (46,  "Offener Haufen M46",  "open_cluster",      7, 41, 46,       -14, 48, 36,  6.1,   27.0,  "Puppis"),
    (47,  "Offener Haufen M47",  "open_cluster",      7, 36, 35,       -14, 29, 0,   4.4,   30.0,  "Puppis"),
    (51,  "Whirlpoolgalaxie",    "galaxy",            13, 29, 52,       47, 11, 43,    8.4,   11.0,  "Canes Venatici"),
    (57,  "Ringnebel",           "planetary_nebula",  18, 53, 35,     33, 1, 45,     8.8,   1.4,   "Lyra"),
    (63,  "Sonnenblumengalaxie", "galaxy",            13, 15, 49,       42, 1, 45,     8.6,   12.0,  "Canes Venatici"),
    (64,  "Schwarzaugen-Galaxie","galaxy",            12, 56, 43,       21, 41, 0,     8.5,   10.0,  "Coma Berenices"),
    (81,  "Bodes Galaxie",       "galaxy",            9, 55, 33,       69, 3, 55,     6.9,   26.0,  "Ursa Major"),
    (82,  "Zigarrengalaxie",     "galaxy",            9, 55, 52,       69, 40, 47,    8.4,   11.0,  "Ursa Major"),
    (92,  "Kugelsternhaufen M92","globular_cluster",  17, 17, 7,       43, 8, 9,      6.5,   14.0,  "Hercules"),
    (97,  "Eulennebel",          "planetary_nebula",  11, 14, 48,       55, 1, 0,      9.9,   3.4,   "Ursa Major"),
    (101, "Windmühlengalaxie",   "galaxy",            14, 3, 12,       54, 20, 57,    7.9,   28.0,  "Ursa Major"),
    (104, "Sombrerogalaxie",     "galaxy",            12, 39, 59,       -11, 37, 23,  8.0,   9.0,   "Virgo"),
    (106, "Spiralgalaxie M106",  "galaxy",            12, 18, 57,       47, 18, 14,    8.4,   19.0,  "Canes Venatici"),
]

def import_messier_catalog() -> int:
    """Import Messier catalog objects"""
    conn = get_conn()
    
    # Check if already imported
    cur = conn.execute("SELECT * FROM catalog_imports WHERE catalog_name = 'messier'")
    if cur.fetchone():
        print("Messier catalog already imported, skipping...")
        return 0
    
    count = 0
    for obj in MESSIER_OBJECTS:
        nr, name, obj_type, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, mag, size, const = obj
        catalog_id = f"M{nr}"
        
        try:
            insert_object(
                name=name,
                catalog_id=catalog_id,
                object_type=obj_type,
                ra_hours=ra_h,
                ra_minutes=ra_m,
                ra_seconds=ra_s,
                dec_degrees=dec_d,
                dec_minutes=dec_m,
                dec_seconds=dec_s,
                magnitude=mag,
                size_arcmin=size,
                constellation=const,
                description=f"Messier {nr}: {name}"
            )
            count += 1
        except Exception as e:
            print(f"Error importing {catalog_id}: {e}")
    
    # Mark as imported
    with conn:
        conn.execute(
            "INSERT INTO catalog_imports (catalog_name, count_objects) VALUES (?, ?)",
            ("messier", count)
        )
    
    print(f"Imported {count} Messier objects")
    return count


# ============================================================================
# BRIGHT NGC OBJECTS (ausgewählte Highlights)
# ============================================================================

NGC_HIGHLIGHTS = [
    # NGC, Name, Typ, RA(h m s), DEC(d m s), Mag, Größe(arcmin), Sternbild
    (7000, "Nordamerikanebel",     "nebula",            20, 58, 47,       44, 20, 0,     4.0,   120.0, "Cygnus"),
    (2237, "Rosettennebel",        "nebula",            6, 33, 45,         5, 0, 0,       9.0,   80.0,  "Monoceros"),
    (1976, "Orionnebel (M42)",    "nebula",            5, 35, 17,       -5, 23, 28,    4.0,   85.0,  "Orion"),  # Duplikat zu M42
    (7293, "Helixnebel",           "planetary_nebula",  22, 29, 39,       -20, 50, 14,   7.3,   16.0,  "Aquarius"),
    (6888, "Halbmondnebel",        "nebula",            20, 12, 7,        38, 21, 18,    7.4,   20.0,  "Cygnus"),
    (6960, "Westliche Schleife",   "supernova_remnant", 20, 45, 42,       30, 43, 0,     7.0,   70.0,  "Cygnus"),
    (6992, "Östliche Schleife",    "supernova_remnant", 20, 56, 24,       31, 43, 0,     7.0,   60.0,  "Cygnus"),
    (2024, "Flammennebel",         "nebula",            5, 41, 43,       -1, 51, 0,     10.0,  30.0,  "Orion"),
    (6618, "Omeganebel (M17)",    "nebula",            18, 20, 47,       -16, 10, 18,   6.0,   46.0,  "Sagittarius"),  # Duplikat
    (1952, "Krebsnebel (M1)",     "supernova_remnant", 5, 34, 32,       22, 0, 52,     8.4,   6.0,   "Taurus"),  # Duplikat
    (2244, "Rosette (offener Haufen)", "open_cluster", 6, 32, 18,       4, 52, 0,      4.8,   24.0,  "Monoceros"),
    (2264, "Weihnachtsbaumhaufen", "open_cluster",      6, 41, 0,         9, 53, 0,      3.9,   20.0,  "Monoceros"),
    (869,  "Doppelhaufen h Persei","open_cluster",      2, 19, 0,         57, 9, 0,      4.3,   30.0,  "Perseus"),
    (884,  "Doppelhaufen chi Persei","open_cluster",    2, 22, 0,         57, 7, 0,      4.4,   30.0,  "Perseus"),
    (457,  "E.T. Cluster",         "open_cluster",      1, 19, 0,         58, 17, 0,     6.4,   13.0,  "Cassiopeia"),
    (869,  "h Persei",             "open_cluster",      2, 19, 0,         57, 9, 0,      4.3,   30.0,  "Perseus"),
    (253,  "Silberdollar-Galaxie", "galaxy",            0, 47, 33,       -25, 17, 18,   7.1,   27.0,  "Sculptor"),
    (2403, "Spiralgalaxie NGC2403","galaxy",            7, 36, 51,       65, 36, 0,     8.4,   18.0,  "Camelopardalis"),
    (3628, "Leo-Triplet Galaxie",  "galaxy",            11, 20, 17,       13, 35, 0,     9.5,   15.0,  "Leo"),
]

def import_ngc_highlights() -> int:
    """Import selected bright NGC objects"""
    conn = get_conn()
    
    cur = conn.execute("SELECT * FROM catalog_imports WHERE catalog_name = 'ngc_highlights'")
    if cur.fetchone():
        print("NGC highlights already imported, skipping...")
        return 0
    
    count = 0
    for obj in NGC_HIGHLIGHTS:
        ngc, name, obj_type, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, mag, size, const = obj
        catalog_id = f"NGC{ngc}"
        
        # Skip if already exists (e.g., M-objects)
        cur = conn.execute("SELECT id FROM objects WHERE catalog_id = ?", (catalog_id,))
        if cur.fetchone():
            continue
        
        try:
            insert_object(
                name=name,
                catalog_id=catalog_id,
                object_type=obj_type,
                ra_hours=ra_h,
                ra_minutes=ra_m,
                ra_seconds=ra_s,
                dec_degrees=dec_d,
                dec_minutes=dec_m,
                dec_seconds=dec_s,
                magnitude=mag,
                size_arcmin=size,
                constellation=const,
                description=f"NGC {ngc}: {name}"
            )
            count += 1
        except Exception as e:
            print(f"Error importing {catalog_id}: {e}")
    
    with conn:
        conn.execute(
            "INSERT INTO catalog_imports (catalog_name, count_objects) VALUES (?, ?)",
            ("ngc_highlights", count)
        )
    
    print(f"Imported {count} NGC objects")
    return count


# ============================================================================
# CALDWELL KATALOG (Bright Objects for Small Telescopes)
# ============================================================================

CALDWELL_OBJECTS = [
    # Caldwell, Name, Typ, RA(h m s), DEC(d m s), Mag, Größe, Sternbild
    (14,  "Hantelnebel",           "planetary_nebula",  19, 59, 36,     22, 43, 16,    7.5,   8.0,   "Vulpecula"),
    (39,  "Eskimonebel",           "planetary_nebula",  7, 29, 10,     -20, 54, 0,     9.9,   1.0,   "Gemini"),
    (49,  "Rosettennebel",         "nebula",            6, 33, 45,       5, 0, 0,       9.0,   80.0,  "Monoceros"),
    (33,  "Nordamerikanebel",      "nebula",            20, 58, 47,       44, 20, 0,     4.0,   120.0, "Cygnus"),
    (27,  "Kresus-Nebel",          "planetary_nebula",  19, 21, 44,     -32, 27, 0,     10.1,  2.0,   "Corona Australis"),
    (41,  "Hyades",                "open_cluster",      4, 27, 0,         15, 52, 0,     0.5,   330.0, "Taurus"),
    (13,  "Kugelsternhaufen NGC4565", "globular_cluster", 12, 36, 15,    25, 55, 0,     10.4,  10.0,  "Coma Berenices"),
    (12,  "Feuerring-Galaxie",     "galaxy",            14, 5, 12,        54, 20, 0,     8.9,   15.0,  "Canes Venatici"),
    (25,  "Doppelhaufen",          "open_cluster",      2, 20, 0,         57, 8, 0,      4.3,   60.0,  "Perseus"),
    (43,  "Doppelhaufen",          "open_cluster",      2, 20, 0,         57, 8, 0,      4.4,   60.0,  "Perseus"),
]

def import_caldwell_catalog() -> int:
    """Import Caldwell catalog objects"""
    conn = get_conn()
    
    cur = conn.execute("SELECT * FROM catalog_imports WHERE catalog_name = 'caldwell'")
    if cur.fetchone():
        print("Caldwell catalog already imported, skipping...")
        return 0
    
    count = 0
    for obj in CALDWELL_OBJECTS:
        cal, name, obj_type, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, mag, size, const = obj
        catalog_id = f"C{cal}"
        
        try:
            insert_object(
                name=name,
                catalog_id=catalog_id,
                object_type=obj_type,
                ra_hours=ra_h,
                ra_minutes=ra_m,
                ra_seconds=ra_s,
                dec_degrees=dec_d,
                dec_minutes=dec_m,
                dec_seconds=dec_s,
                magnitude=mag,
                size_arcmin=size,
                constellation=const,
                description=f"Caldwell {cal}: {name}"
            )
            count += 1
        except Exception as e:
            print(f"Error importing {catalog_id}: {e}")
    
    with conn:
        conn.execute(
            "INSERT INTO catalog_imports (catalog_name, count_objects) VALUES (?, ?)",
            ("caldwell", count)
        )
    
    print(f"Imported {count} Caldwell objects")
    return count


# ============================================================================
# SOLAR SYSTEM OBJECTS
# ============================================================================

SOLAR_SYSTEM = [
    ("Sonne", "sun", None, None, None, None, None, None, -26.7, 1920.0, None),
    ("Mond", "moon", None, None, None, None, None, None, -12.7, 1920.0, None),
    ("Merkur", "planet", None, None, None, None, None, None, -2.0, 0.0, None),
    ("Venus", "planet", None, None, None, None, None, None, -4.5, 0.0, None),
    ("Mars", "planet", None, None, None, None, None, None, -2.9, 0.0, None),
    ("Jupiter", "planet", None, None, None, None, None, None, -2.9, 0.0, None),
    ("Saturn", "planet", None, None, None, None, None, None, 0.5, 0.0, None),
    ("Uranus", "planet", None, None, None, None, None, None, 5.7, 0.0, None),
    ("Neptun", "planet", None, None, None, None, None, None, 7.8, 0.0, None),
]

def import_solar_system() -> int:
    """Import solar system objects"""
    conn = get_conn()
    
    cur = conn.execute("SELECT * FROM catalog_imports WHERE catalog_name = 'solar_system'")
    if cur.fetchone():
        print("Solar system already imported, skipping...")
        return 0
    
    count = 0
    for obj in SOLAR_SYSTEM:
        name, obj_type, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, mag, size, const = obj
        
        try:
            insert_object(
                name=name,
                catalog_id=name,
                object_type=obj_type,
                ra_hours=ra_h,
                ra_minutes=ra_m,
                ra_seconds=ra_s,
                dec_degrees=dec_d,
                dec_minutes=dec_m,
                dec_seconds=dec_s,
                magnitude=mag,
                size_arcmin=size,
                constellation=const,
                description=f"{name} - Objekt des Sonnensystems"
            )
            count += 1
        except Exception as e:
            print(f"Error importing {name}: {e}")
    
    with conn:
        conn.execute(
            "INSERT INTO catalog_imports (catalog_name, count_objects) VALUES (?, ?)",
            ("solar_system", count)
        )
    
    print(f"Imported {count} solar system objects")
    return count


# ============================================================================
# MASTER IMPORT FUNCTION
# ============================================================================

def import_all_catalogs():
    """Import all catalogs at once"""
    print("=" * 50)
    print("CAT3 Catalog Import")
    print("=" * 50)
    
    total = 0
    total += import_messier_catalog()
    total += import_ngc_highlights()
    total += import_caldwell_catalog()
    total += import_solar_system()
    
    print("=" * 50)
    print(f"Total imported: {total} objects")
    print("=" * 50)


if __name__ == "__main__":
    import_all_catalogs()
