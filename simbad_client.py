"""
SIMBAD Client - Astronomical Data Query via TAP Service
Strasbourg Astronomical Data Center (CDS)
"""
import requests
import urllib.parse
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

SIMBAD_TAP_URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"


@dataclass
class SimbadObject:
    """Represents an astronomical object from SIMBAD"""
    main_id: str
    name: str
    object_type: str
    ra_hours: int
    ra_minutes: int
    ra_seconds: float
    dec_degrees: int
    dec_minutes: int
    dec_seconds: float
    magnitude_v: Optional[float] = None
    magnitude_b: Optional[float] = None
    size_arcmin: Optional[float] = None
    constellation: Optional[str] = None
    morphology: Optional[str] = None
    
    @property
    def ra_display(self) -> str:
        """RA as display string"""
        return f"{self.ra_hours:02d}:{self.ra_minutes:02d}:{self.ra_seconds:05.2f}"
    
    @property
    def dec_display(self) -> str:
        """Dec as display string"""
        sign = "+" if self.dec_degrees >= 0 else "-"
        return f"{sign}{abs(self.dec_degrees):02d}:{self.dec_minutes:02d}:{self.dec_seconds:05.2f}"


def _ra_to_hms(ra_degrees: float) -> tuple:
    """Convert RA in degrees to hours, minutes, seconds"""
    ra_hours_total = ra_degrees / 15.0
    hours = int(ra_hours_total)
    minutes_total = (ra_hours_total - hours) * 60
    minutes = int(minutes_total)
    seconds = (minutes_total - minutes) * 60
    return hours, minutes, seconds


def _dec_to_dms(dec_degrees: float) -> tuple:
    """Convert Dec in degrees to degrees, minutes, seconds"""
    sign = 1 if dec_degrees >= 0 else -1
    dec_abs = abs(dec_degrees)
    degrees = int(dec_abs) * sign
    minutes_total = (dec_abs - int(dec_abs)) * 60
    minutes = int(minutes_total)
    seconds = (minutes_total - minutes) * 60
    return degrees, minutes, seconds


def search_by_name(query: str, limit: int = 20) -> List[SimbadObject]:
    """
    Search SIMBAD by object name/identifier
    Returns list of matching objects
    """
    adql = f"""
    SELECT DISTINCT TOP {limit}
        b.main_id,
        b.ra,
        b.dec,
        b.otype as object_type,
        b.galdim_majaxis as size_major,
        b.galdim_minaxis as size_minor,
        b.vartype as morphology,
        i.id as alt_name,
        f_flux.flux as mag_v,
        f_b.flux as mag_b
    FROM basic b
    LEFT JOIN ident i ON b.oid = i.oidref
    LEFT JOIN flux f_flux ON b.oid = f_flux.oidref AND f_flux.filter = 'V'
    LEFT JOIN flux f_b ON b.oid = f_b.oidref AND f_b.filter = 'B'
    WHERE b.main_id LIKE '%{query}%'
       OR i.id LIKE '%{query}%'
    ORDER BY b.main_id
    """
    
    return _execute_query(adql)


def get_object_by_id(object_id: str) -> Optional[SimbadObject]:
    """
    Get specific object by its main ID (exact match)
    """
    adql = f"""
    SELECT TOP 1
        b.main_id,
        b.ra,
        b.dec,
        b.otype as object_type,
        b.galdim_majaxis as size_major,
        b.galdim_minaxis as size_minor,
        b.vartype as morphology,
        f_flux.flux as mag_v,
        f_b.flux as mag_b
    FROM basic b
    LEFT JOIN flux f_flux ON b.oid = f_flux.oidref AND f_flux.filter = 'V'
    LEFT JOIN flux f_b ON b.oid = f_b.oidref AND f_b.filter = 'B'
    WHERE b.main_id = '{object_id}'
    """
    
    results = _execute_query(adql)
    return results[0] if results else None


def _execute_query(adql: str) -> List[SimbadObject]:
    """Execute TAP query and parse results"""
    params = {
        'request': 'doQuery',
        'lang': 'adql',
        'format': 'json',
        'query': adql.strip()
    }
    
    try:
        response = requests.post(
            SIMBAD_TAP_URL,
            data=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        return _parse_results(data)
        
    except requests.exceptions.Timeout:
        print("SIMBAD query timeout")
        return []
    except requests.exceptions.RequestException as e:
        print(f"SIMBAD query error: {e}")
        return []
    except Exception as e:
        print(f"SIMBAD parse error: {e}")
        return []


def _parse_results(data: Dict) -> List[SimbadObject]:
    """Parse SIMBAD TAP JSON response"""
    results = []
    
    # JSON response format from TAP
    if 'data' not in data:
        return results
    
    # Column indices (may vary, need to check metadata)
    columns = {col['name']: i for i, col in enumerate(data.get('metadata', []))}
    
    for row in data['data']:
        try:
            # Extract RA/Dec from degrees
            ra_deg = row[columns.get('ra', 1)] if 'ra' in columns else None
            dec_deg = row[columns.get('dec', 2)] if 'dec' in columns else None
            
            if ra_deg is None or dec_deg is None:
                continue
                
            ra_h, ra_m, ra_s = _ra_to_hms(float(ra_deg))
            dec_d, dec_m, dec_s = _dec_to_dms(float(dec_deg))
            
            # Object type mapping
            obj_type = row[columns.get('object_type', 3)] if 'object_type' in columns else "unknown"
            obj_type = _map_object_type(obj_type)
            
            # Size calculation
            size_major = row[columns.get('size_major', 4)] if 'size_major' in columns else None
            size_minor = row[columns.get('size_minor', 5)] if 'size_minor' in columns else None
            if size_major:
                size_major_arcmin = float(size_major) * 60  # degrees to arcmin
            else:
                size_major_arcmin = None
            
            obj = SimbadObject(
                main_id=row[columns.get('main_id', 0)] if 'main_id' in columns else "",
                name=row[columns.get('main_id', 0)] if 'main_id' in columns else "",
                object_type=obj_type,
                ra_hours=ra_h,
                ra_minutes=ra_m,
                ra_seconds=ra_s,
                dec_degrees=dec_d,
                dec_minutes=dec_m,
                dec_seconds=dec_s,
                magnitude_v=float(row[columns.get('mag_v', 7)]) if 'mag_v' in columns and row[columns.get('mag_v', 7)] else None,
                magnitude_b=float(row[columns.get('mag_b', 8)]) if 'mag_b' in columns and row[columns.get('mag_b', 8)] else None,
                size_arcmin=size_major_arcmin,
                morphology=row[columns.get('morphology', 6)] if 'morphology' in columns else None
            )
            results.append(obj)
            
        except Exception as e:
            print(f"Error parsing row: {e}")
            continue
    
    return results


def _map_object_type(simbad_type: str) -> str:
    """Map SIMBAD object type to CAT3 types"""
    type_mapping = {
        'Galaxy': 'galaxy',
        'G': 'galaxy',
        'AGN': 'galaxy',
        'Seyfert': 'galaxy',
        
        'Neb': 'nebula',
        'PN': 'planetary_nebula',
        'SNR': 'supernova_remnant',
        'HII': 'nebula',
        'RfN': 'nebula',
        'GlC': 'globular_cluster',
        'OpC': 'open_cluster',
        'Cl*': 'open_cluster',
        
        'Star': 'star',
        '*': 'star',
        '**': 'double_star',
        
        'Planet': 'planet',
        'Comet': 'comet',
        'Asteroid': 'asteroid',
        'Moon': 'moon',
        'Sun': 'sun',
    }
    
    # Check for exact match or partial match
    for simbad_key, cat3_type in type_mapping.items():
        if simbad_key in simbad_type or simbad_type == simbad_key:
            return cat3_type
    
    return "unknown"


def test_connection() -> bool:
    """Test if SIMBAD is reachable"""
    try:
        response = requests.get(
            "https://simbad.cds.unistra.fr/simbad/sim-tap",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    # Test
    print("Testing SIMBAD connection...")
    if test_connection():
        print("Connected!")
        print("\nSearching for 'M31':")
        results = search_by_name("M31", limit=5)
        for r in results:
            print(f"  {r.main_id}: RA={r.ra_display}, Dec={r.dec_display}, MagV={r.magnitude_v}")
    else:
        print("Connection failed")