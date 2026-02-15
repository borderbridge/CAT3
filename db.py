"""
CAT3 Database Module - Erweiterte Version für Astronomical Catalog
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

DB_PATH = Path(__file__).parent / "Database" / "cat3.db"

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def get_conn():
    """Get database connection with all tables initialized"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    _migrate_database(conn)  # Add missing columns without losing data
    return conn

def _migrate_database(conn: sqlite3.Connection):
    """Migrate database schema without losing existing data"""
    cursor = conn.execute("PRAGMA table_info(observations)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'camera' not in columns:
        print("Migrating: Adding 'camera' column...")
        conn.execute("ALTER TABLE observations ADD COLUMN camera TEXT")
        conn.commit()
        print("  - camera column added")
    
    if 'data_path' not in columns:
        print("Migrating: Adding 'data_path' column...")
        conn.execute("ALTER TABLE observations ADD COLUMN data_path TEXT")
        conn.commit()
        print("  - data_path column added")
        
    if 'camera' in columns and 'data_path' in columns:
        print("Database schema up to date.")

def _init_tables(conn: sqlite3.Connection):
    """Initialize all database tables"""
    
    # Haupttabelle: Astronomische Objekte
    conn.execute("""
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            catalog_id TEXT,                    -- z.B. M42, NGC7000, IC434
            object_type TEXT,                   -- galaxy, nebula, star_cluster, planet, comet, asteroid
            
            -- Koordinaten (J2000)
            ra_hours INTEGER,
            ra_minutes INTEGER,
            ra_seconds REAL,
            dec_degrees INTEGER,
            dec_minutes INTEGER,
            dec_seconds REAL,
            
            -- Physikalische Eigenschaften
            magnitude REAL,                     -- Scheinbare Helligkeit
            size_arcmin REAL,                   -- Größe in Bogenminuten
            constellation TEXT,                 -- Sternbild
            
            -- Beschreibung
            description TEXT,
            notes TEXT,                         -- Persönliche Notizen zum Objekt
            
            -- Daten-Verzeichnis
            data_directory TEXT,                -- Pfad zu Beobachtungsdaten/Fotos
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Beobachtungssessions
    conn.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,                 -- Beobachtungsdatum
            start_time TIME,                    -- Startzeit
            end_time TIME,                      -- Endzeit
            
            -- Ort & Bedingungen
            location_name TEXT,                 -- Name des Beobachtungsorts
            location_lat REAL,                  -- Breitengrad
            location_lon REAL,                  -- Längengrad
            
            -- Seeing & Wetter
            seeing TEXT,                        -- seeing_scale: excellent/good/fair/poor/terrible
            transparency TEXT,                  -- transparency: excellent/good/fair/poor
            temperature REAL,                   -- Temperatur in Celsius
            humidity INTEGER,                   -- Luftfeuchtigkeit in %
            
            -- Equipment
            telescope TEXT,                   -- Welches Teleskop?
            camera TEXT,                      -- Kamera (z.B. ASI294MC)
            eyepiece TEXT,                      -- Okular
            filter TEXT,                        -- Filter verwendet?
            
            -- Notizen
            general_notes TEXT,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Verknüpfung: Welche Objekte wurden bei welcher Session beobachtet
    conn.execute("""
        CREATE TABLE IF NOT EXISTS observation_objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            observation_id INTEGER NOT NULL,
            object_id INTEGER NOT NULL,
            
            -- Beobachtungsspezifische Details
            visibility TEXT,                    -- visibility: easy/moderate/difficult/very_difficult/not_seen
            observation_notes TEXT,             -- Notizen zu diesem spezifischen Objekt in dieser Session
            
            FOREIGN KEY (observation_id) REFERENCES observations(id) ON DELETE CASCADE,
            FOREIGN KEY (object_id) REFERENCES objects(id) ON DELETE CASCADE,
            UNIQUE(observation_id, object_id)   -- Ein Objekt nur einmal pro Session
        )
    """)
    
    # Bilder zu Objekten und/oder Beobachtungen
    conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_id INTEGER,                  -- Kann NULL sein wenn nur zu Observation gehört
            observation_id INTEGER,             -- Kann NULL sein wenn nur zu Objekt gehört
            
            file_path TEXT NOT NULL,
            thumbnail_path TEXT,
            
            -- Bild-Metadaten
            capture_date TIMESTAMP,
            exposure_time REAL,                 -- Sekunden
            iso INTEGER,
            aperture REAL,                    -- z.B. 5.6
            focal_length INTEGER,               -- mm
            
            -- Beschreibung
            title TEXT,
            description TEXT,
            is_primary BOOLEAN DEFAULT 0,       -- Hauptbild für das Objekt?
            
            FOREIGN KEY (object_id) REFERENCES objects(id) ON DELETE CASCADE,
            FOREIGN KEY (observation_id) REFERENCES observations(id) ON DELETE CASCADE
        )
    """)
    
    # Katalog-Import-Tracking (damit wir nicht doppelt importieren)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS catalog_imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            catalog_name TEXT NOT NULL,         -- z.B. "messier", "ngc", "caldwell"
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            count_objects INTEGER
        )
    """)
    
    conn.commit()


# ============================================================================
# OBJECT CRUD OPERATIONS
# ============================================================================

def insert_object(
    name: str,
    catalog_id: Optional[str] = None,
    object_type: Optional[str] = None,
    ra_hours: Optional[int] = None,
    ra_minutes: Optional[int] = None,
    ra_seconds: Optional[float] = None,
    dec_degrees: Optional[int] = None,
    dec_minutes: Optional[int] = None,
    dec_seconds: Optional[float] = None,
    magnitude: Optional[float] = None,
    size_arcmin: Optional[float] = None,
    constellation: Optional[str] = None,
    description: Optional[str] = None,
    notes: Optional[str] = None,
    data_directory: Optional[str] = None
) -> int:
    """Insert new astronomical object, returns the new ID"""
    conn = get_conn()
    with conn:
        cursor = conn.execute("""
            INSERT INTO objects (
                name, catalog_id, object_type,
                ra_hours, ra_minutes, ra_seconds,
                dec_degrees, dec_minutes, dec_seconds,
                magnitude, size_arcmin, constellation,
                description, notes, data_directory
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, catalog_id, object_type,
            ra_hours, ra_minutes, ra_seconds,
            dec_degrees, dec_minutes, dec_seconds,
            magnitude, size_arcmin, constellation,
            description, notes, data_directory
        ))
        return cursor.lastrowid

def update_object(obj_id: int, **kwargs) -> bool:
    """Update object fields. kwargs can be any column name."""
    allowed_fields = {
        'name', 'catalog_id', 'object_type',
        'ra_hours', 'ra_minutes', 'ra_seconds',
        'dec_degrees', 'dec_minutes', 'dec_seconds',
        'magnitude', 'size_arcmin', 'constellation',
        'description', 'notes', 'data_directory'
    }
    
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if not updates:
        return False
    
    conn = get_conn()
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [obj_id]
    
    with conn:
        conn.execute(f"""
            UPDATE objects 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, values)
    return True

def fetch_objects(filter_text: str = "", object_type: str = None, constellation: str = None, search_all_fields: bool = True) -> List[Tuple[int, str, str, str]]:
    """
    Fetch objects with optional filters.
    Returns: List of (id, name, catalog_id, object_type)
    If search_all_fields is True, searches in name, catalog_id, description, notes, constellation, data_directory
    """
    conn = get_conn()
    
    conditions = []
    params = []
    
    if filter_text.strip():
        if search_all_fields:
            # Search in ALL text fields
            conditions.append("""(name LIKE ? OR catalog_id LIKE ? OR description LIKE ? 
                OR notes LIKE ? OR constellation LIKE ? OR object_type LIKE ? 
                OR data_directory LIKE ?)""")
            like = f"%{filter_text.strip()}%"
            params.extend([like, like, like, like, like, like, like])
        else:
            # Original limited search
            conditions.append("(name LIKE ? OR catalog_id LIKE ? OR description LIKE ?)")
            like = f"%{filter_text.strip()}%"
            params.extend([like, like, like])
    
    if object_type:
        conditions.append("object_type = ?")
        params.append(object_type)
    
    if constellation:
        conditions.append("constellation = ?")
        params.append(constellation)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    cur = conn.execute(f"""
        SELECT id, name, catalog_id, object_type 
        FROM objects 
        {where_clause}
        ORDER BY 
            CASE WHEN catalog_id IS NOT NULL THEN 0 ELSE 1 END,
            catalog_id,
            name
    """, params)
    
    return [(row['id'], row['name'], row['catalog_id'] or '', row['object_type'] or '') for row in cur.fetchall()]

def fetch_object_by_id(obj_id: int) -> Optional[Dict[str, Any]]:
    """Fetch complete object data by ID"""
    conn = get_conn()
    cur = conn.execute("SELECT * FROM objects WHERE id = ?", (obj_id,))
    row = cur.fetchone()
    return dict(row) if row else None

def delete_object(obj_id: int) -> bool:
    """Delete object and all related data (cascade handled by FK)"""
    conn = get_conn()
    with conn:
        cur = conn.execute("DELETE FROM objects WHERE id = ?", (obj_id,))
        return cur.rowcount > 0


# ============================================================================
# OBSERVATION CRUD OPERATIONS
# ============================================================================

def insert_observation(
    date: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    location_name: Optional[str] = None,
    location_lat: Optional[float] = None,
    location_lon: Optional[float] = None,
    seeing: Optional[str] = None,
    transparency: Optional[str] = None,
    temperature: Optional[float] = None,
    humidity: Optional[int] = None,
    telescope: Optional[str] = None,
    camera: Optional[str] = None,
    eyepiece: Optional[str] = None,
    filter_used: Optional[str] = None,
    data_path: Optional[str] = None,
    general_notes: Optional[str] = None
) -> int:
    """Insert new observation session"""
    conn = get_conn()
    with conn:
        cursor = conn.execute("""
            INSERT INTO observations (
                date, start_time, end_time,
                location_name, location_lat, location_lon,
                seeing, transparency, temperature, humidity,
                telescope, camera, eyepiece, filter,
                data_path, general_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date, start_time, end_time,
            location_name, location_lat, location_lon,
            seeing, transparency, temperature, humidity,
            telescope, camera, eyepiece, filter_used,
            data_path,
            general_notes
        ))
        return cursor.lastrowid

def fetch_observations(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch all observation sessions, newest first"""
    conn = get_conn()
    cur = conn.execute("""
        SELECT * FROM observations 
        ORDER BY date DESC, start_time DESC 
        LIMIT ?
    """, (limit,))
    return [dict(row) for row in cur.fetchall()]

def fetch_observation_by_id(obs_id: int) -> Optional[Dict[str, Any]]:
    """Fetch single observation with all observed objects"""
    conn = get_conn()
    cur = conn.execute("SELECT * FROM observations WHERE id = ?", (obs_id,))
    obs = cur.fetchone()
    if not obs:
        return None
    
    result = dict(obs)
    
    # Fetch observed objects
    cur = conn.execute("""
        SELECT oo.*, o.name, o.catalog_id, o.object_type
        FROM observation_objects oo
        JOIN objects o ON oo.object_id = o.id
        WHERE oo.observation_id = ?
    """, (obs_id,))
    result['objects'] = [dict(row) for row in cur.fetchall()]
    
    return result

def add_object_to_observation(
    observation_id: int,
    object_id: int,
    visibility: Optional[str] = None,
    observation_notes: Optional[str] = None
) -> bool:
    """Link an object to an observation session"""
    conn = get_conn()
    try:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO observation_objects 
                (observation_id, object_id, visibility, observation_notes)
                VALUES (?, ?, ?, ?)
            """, (observation_id, object_id, visibility, observation_notes))
        return True
    except sqlite3.IntegrityError:
        return False

def fetch_observations_for_object(obj_id: int) -> List[Dict[str, Any]]:
    """Fetch all observations for a specific object"""
    conn = get_conn()
    cur = conn.execute("""
        SELECT 
            o.id, o.date, o.start_time, o.end_time,
            o.location_name, o.telescope, o.camera, o.eyepiece, o.filter,
            o.data_path, o.seeing, o.transparency, o.general_notes,
            oo.visibility as obj_visibility,
            oo.observation_notes as obj_notes
        FROM observations o
        JOIN observation_objects oo ON o.id = oo.observation_id
        WHERE oo.object_id = ?
        ORDER BY o.date DESC, o.start_time DESC
    """, (obj_id,))
    return [dict(row) for row in cur.fetchall()]


# ============================================================================
# IMAGE OPERATIONS
# ============================================================================

def insert_image(
    file_path: str,
    object_id: Optional[int] = None,
    observation_id: Optional[int] = None,
    thumbnail_path: Optional[str] = None,
    capture_date: Optional[str] = None,
    exposure_time: Optional[float] = None,
    iso: Optional[int] = None,
    aperture: Optional[float] = None,
    focal_length: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    is_primary: bool = False
) -> int:
    """Insert image record"""
    conn = get_conn()
    with conn:
        cursor = conn.execute("""
            INSERT INTO images (
                object_id, observation_id, file_path, thumbnail_path,
                capture_date, exposure_time, iso, aperture, focal_length,
                title, description, is_primary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            object_id, observation_id, file_path, thumbnail_path,
            capture_date, exposure_time, iso, aperture, focal_length,
            title, description, 1 if is_primary else 0
        ))
        return cursor.lastrowid

def fetch_images_for_object(obj_id: int, include_thumbnails: bool = True) -> List[Dict[str, Any]]:
    """Fetch all images for an object, primary first"""
    conn = get_conn()
    cur = conn.execute("""
        SELECT * FROM images 
        WHERE object_id = ?
        ORDER BY is_primary DESC, capture_date DESC
    """, (obj_id,))
    return [dict(row) for row in cur.fetchall()]

def fetch_primary_image(obj_id: int) -> Optional[Dict[str, Any]]:
    """Fetch primary image for an object"""
    conn = get_conn()
    cur = conn.execute("""
        SELECT * FROM images 
        WHERE object_id = ? AND is_primary = 1
        LIMIT 1
    """, (obj_id,))
    row = cur.fetchone()
    return dict(row) if row else None

def set_primary_image(obj_id: int, image_id: int):
    """Set an image as primary for an object (unset others)"""
    conn = get_conn()
    with conn:
        conn.execute("UPDATE images SET is_primary = 0 WHERE object_id = ?", (obj_id,))
        conn.execute("UPDATE images SET is_primary = 1 WHERE id = ? AND object_id = ?", (image_id, obj_id))


# ============================================================================
# STATISTICS & QUERIES
# ============================================================================

def get_statistics() -> Dict[str, Any]:
    """Get catalog statistics"""
    conn = get_conn()
    stats = {}
    
    cur = conn.execute("SELECT COUNT(*) FROM objects")
    stats['total_objects'] = cur.fetchone()[0]
    
    cur = conn.execute("SELECT COUNT(*) FROM observations")
    stats['total_observations'] = cur.fetchone()[0]
    
    cur = conn.execute("SELECT COUNT(*) FROM images")
    stats['total_images'] = cur.fetchone()[0]
    
    cur = conn.execute("""
        SELECT object_type, COUNT(*) as count 
        FROM objects 
        WHERE object_type IS NOT NULL
        GROUP BY object_type
    """)
    stats['objects_by_type'] = {row[0]: row[1] for row in cur.fetchall()}
    
    cur = conn.execute("""
        SELECT constellation, COUNT(*) as count 
        FROM objects 
        WHERE constellation IS NOT NULL
        GROUP BY constellation
        ORDER BY count DESC
    """)
    stats['objects_by_constellation'] = {row[0]: row[1] for row in cur.fetchall()}
    
    return stats

def get_observed_objects() -> List[Dict[str, Any]]:
    """Get all objects that have been observed at least once"""
    conn = get_conn()
    cur = conn.execute("""
        SELECT DISTINCT o.id, o.name, o.catalog_id, o.object_type,
               COUNT(oo.id) as observation_count,
               MAX(obs.date) as last_observed
        FROM objects o
        JOIN observation_objects oo ON o.id = oo.object_id
        JOIN observations obs ON oo.observation_id = obs.id
        GROUP BY o.id
        ORDER BY last_observed DESC
    """)
    return [dict(row) for row in cur.fetchall()]

def get_unobserved_objects(object_type: str = None, constellation: str = None) -> List[Dict[str, Any]]:
    """Get objects that have never been observed (wishlist candidates)"""
    conn = get_conn()
    
    conditions = ["o.id NOT IN (SELECT object_id FROM observation_objects)"]
    params = []
    
    if object_type:
        conditions.append("o.object_type = ?")
        params.append(object_type)
    
    if constellation:
        conditions.append("o.constellation = ?")
        params.append(constellation)
    
    where_clause = "WHERE " + " AND ".join(conditions)
    
    cur = conn.execute(f"""
        SELECT o.* FROM objects o
        {where_clause}
        ORDER BY o.magnitude ASC NULLS LAST
    """, params)
    
    return [dict(row) for row in cur.fetchall()]


# ============================================================================
# BACKWARDS COMPATIBILITY (alte Funktionen beibehalten)
# ============================================================================

def insert_object_legacy(name: str) -> int:
    """Legacy: Insert object with just a name (for backwards compatibility)"""
    return insert_object(name=name)
