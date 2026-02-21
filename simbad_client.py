"""
SIMBAD Client - Astronomical Data Query
Hybrid: TAP for search (flexible), astroquery for details (magnitude, type)
"""
import urllib.request
import urllib.parse
import json
import warnings
from typing import Optional, List, Dict
from dataclasses import dataclass

try:
    from astroquery.simbad import Simbad
    ASTROQUERY_AVAILABLE = True
except ImportError:
    ASTROQUERY_AVAILABLE = False

SIMBAD_TAP_URL = "https://simbad.cds.unistra.fr/simbad/sim-tap/sync"


@dataclass
class SimbadObject:
    main_id: str
    name: str
    ra_hours: int
    ra_minutes: int
    ra_seconds: float
    dec_degrees: int
    dec_minutes: int
    dec_seconds: float
    object_type: str = "unknown"
    magnitude_v: Optional[float] = None
    magnitude_b: Optional[float] = None
    size_arcmin: Optional[float] = None
    constellation: Optional[str] = None
    morphology: Optional[str] = None
    
    @property
    def ra_display(self) -> str:
        return f"{self.ra_hours:02d}:{self.ra_minutes:02d}:{self.ra_seconds:05.2f}"
    
    @property
    def dec_display(self) -> str:
        sign = "+" if self.dec_degrees >= 0 else "-"
        return f"{sign}{abs(self.dec_degrees):02d}:{self.dec_minutes:02d}:{self.dec_seconds:05.2f}"


def _ra_to_hms(ra_deg: float) -> tuple:
    """Convert RA in degrees to hours, minutes, seconds"""
    ra_h = ra_deg / 15.0
    h = int(ra_h)
    m = int((ra_h - h) * 60)
    s = ((ra_h - h) * 60 - m) * 60
    return h, m, s


def _dec_to_dms(dec_deg: float) -> tuple:
    """Convert Dec in degrees to degrees, minutes, seconds"""
    sign = 1 if dec_deg >= 0 else -1
    d_abs = abs(dec_deg)
    d = int(d_abs) * sign
    m = int((d_abs - int(d_abs)) * 60)
    s = ((d_abs - int(d_abs)) * 60 - m) * 60
    return d, m, s


def _execute_tap_query(adql: str) -> List[Dict]:
    """Execute TAP query, return raw data rows"""
    params = {
        'request': 'doQuery',
        'lang': 'adql',
        'format': 'json',
        'query': adql
    }
    
    try:
        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(
            SIMBAD_TAP_URL,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'data' not in result or 'metadata' not in result:
            return []
        
        cols = {col['name']: i for i, col in enumerate(result['metadata'])}
        return [{name: row[i] for name, i in cols.items()} for row in result['data']]
        
    except Exception as e:
        return []


def _get_astroquery_details(main_id: str) -> Dict:
    """Get details (magnitude, type, size) via astroquery. Single query, suppress warnings."""
    if not ASTROQUERY_AVAILABLE:
        return {}
    
    details = {'magnitude_v': None, 'object_type': 'unknown', 
               'size_arcmin': None, 'morphology': None}
    
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            simbad = Simbad()
            simbad.ROW_LIMIT = 1
            simbad.add_votable_fields('V', 'otype', 'galdim_majaxis')
            
            table = simbad.query_object(main_id)
            
            if table is not None and len(table) > 0:
                row = table[0]
                
                if 'V' in row.colnames and row['V']:
                    try:
                        details['magnitude_v'] = float(row['V'])
                    except:
                        pass
                
                if 'otype' in row.colnames and row['otype']:
                    details['object_type'] = _map_object_type(str(row['otype']))
                    details['morphology'] = str(row['otype'])
                
                if 'galdim_majaxis' in row.colnames and row['galdim_majaxis']:
                    try:
                        # Already in arcmin from SIMBAD
                        details['size_arcmin'] = float(row['galdim_majaxis'])
                    except:
                        pass
                    
    except Exception as e:
        pass
    
    return details


def _map_object_type(otype: str) -> str:
    """Map SIMBAD object type to CAT3"""
    if not otype:
        return "unknown"
    
    st = str(otype).strip()
    type_map = {
        'G': 'galaxy', 'Galaxy': 'galaxy', 'AGN': 'galaxy',
        'Seyfert': 'galaxy', 'Seyfert_1': 'galaxy', 'Seyfert_2': 'galaxy',
        'LINER': 'galaxy', 'QSO': 'galaxy',
        'PN': 'planetary_nebula', 'PlanetaryNeb': 'planetary_nebula',
        'SNR': 'supernova_remnant',
        'HII': 'nebula', 'Neb': 'nebula',
        'GlC': 'globular_cluster', 'GlobularCl': 'globular_cluster',
        'OpC': 'open_cluster', 'OpenCl': 'open_cluster', 'Cl': 'open_cluster',
        '*': 'star', 'Star': 'star', '**': 'double_star',
        'Planet': 'planet', 'Comet': 'comet', 'Asteroid': 'asteroid',
        'Moon': 'moon', 'Sun': 'sun',
    }
    return type_map.get(st, "unknown")


def search_by_name(query: str, limit: int = 15) -> List[SimbadObject]:
    """Search SIMBAD by object name using TAP (flexible LIKE queries)"""
    safe_query = query.replace("'", "''")
    results = []
    found_ids = set()
    
    # Search 1: LIKE on main_id
    adql = f"SELECT TOP {limit} main_id, ra, dec FROM basic WHERE main_id LIKE '%{safe_query}%'"
    rows = _execute_tap_query(adql)
    
    for row in rows:
        mid = row.get('main_id')
        ra = row.get('ra')
        dec = row.get('dec')
        if mid and ra is not None and dec is not None and mid not in found_ids:
            found_ids.add(mid)
            ra_h, ra_m, ra_s = _ra_to_hms(ra)
            dec_d, dec_m, dec_s = _dec_to_dms(dec)
            results.append(SimbadObject(
                main_id=mid, name=mid,
                ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s
            ))
    
    # Search 2: Alternative identifiers
    if len(results) < 5:
        adql = f"""SELECT TOP {limit} b.main_id, b.ra, b.dec 
                   FROM basic b JOIN ident i ON b.oid = i.oidref 
                   WHERE i.id LIKE '%{safe_query}%'"""
        rows = _execute_tap_query(adql)
        for row in rows:
            mid = row.get('main_id')
            ra = row.get('ra')
            dec = row.get('dec')
            if mid and ra is not None and dec is not None and mid not in found_ids:
                found_ids.add(mid)
                ra_h, ra_m, ra_s = _ra_to_hms(ra)
                dec_d, dec_m, dec_s = _dec_to_dms(dec)
                results.append(SimbadObject(
                    main_id=mid, name=mid,
                    ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                    dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s
                ))
    
    # Note: Details (magnitude, type, size) fetched only when object is SELECTED
    # This prevents spamming SIMBAD with 15+ queries per search
    
    return results[:limit]


def test_connection() -> bool:
    """Test if SIMBAD is reachable"""
    try:
        req = urllib.request.Request(
            "https://simbad.cds.unistra.fr/simbad/sim-tap",
            method='HEAD'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except:
        return False


if __name__ == "__main__":
    print("Testing SIMBAD hybrid client...")
    if test_connection():
        print(f"✓ Connected (astroquery: {ASTROQUERY_AVAILABLE})")
        print("\nSearching M31:")
        for r in search_by_name("M31", limit=3):
            print(f"  {r.main_id}: {r.ra_display} / {r.dec_display}")
            # Note: magnitude/type only fetched on selection
    else:
        print("✗ Connection failed")