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


def _normalize_query(query: str) -> str:
    """Convert user input to SIMBAD format"""
    q = query.strip().upper()
    
    # Common names -> SIMBAD main_id
    name_map = {
        'ANDROMEDA': 'M  31',
        'ANDROMEDAGALAXY': 'M  31',
        'ORIONNEBEL': 'M  42',
        'ORIONNEBULA': 'M  42',
        'M42': 'M  42',
        'PLEJADEN': 'M  45',
        'PLEIADES': 'M  45',
        'KREBSNEBEL': 'M  1',
        'CRABNEBULA': 'M  1',
        'LAGUNENNEBEL': 'M  8',
        'LAGOONNEBULA': 'M  8',
        'ADLERNEBEL': 'M  16',
        'EAGLENEBULA': 'M  16',
        'RINGNEBEL': 'M  57',
        'RINGNEBULA': 'M  57',
        'HANTELNEBEL': 'M  27',
        'DUMBBELLNEBULA': 'M  27',
        'NORDAMERIKANEBEL': 'NGC 7000',
        'NORTHAMERICANEBULA': 'NGC 7000',
        'M31': 'M  31',
        'M1': 'M  1',
        'M2': 'M  2',
        'M3': 'M  3',
        'M4': 'M  4',
        'M5': 'M  5',
        'M6': 'M  6',
        'M7': 'M  7',
        'M8': 'M  8',
        'M9': 'M  9',
        'M10': 'M  10',
        'M11': 'M  11',
        'M12': 'M  12',
        'M13': 'M  13',
        'M14': 'M  14',
        'M15': 'M  15',
        'M31': 'M  31',
        'M42': 'M  42',
        'M45': 'M  45',
        'M51': 'M  51',
        'M57': 'M  57',
    }
    
    q_clean = q.replace(' ', '').replace('-', '').replace('_', '')
    if q_clean in name_map:
        return name_map[q_clean]
    if q in name_map:
        return name_map[q]
    
    # Messier: M31 -> M  31
    if q.startswith('M') and len(q) > 1 and q[1:].strip().isdigit():
        return f"M  {q[1:].strip()}"
    
    # NGC/IC: NGC7000 -> NGC 7000
    for prefix in ['NGC', 'IC', 'UGC']:
        if q.startswith(prefix) and len(q) > len(prefix):
            num = q[len(prefix):].strip()
            if num.isdigit():
                return f"{prefix} {num}"
    
    return query


def _get_astroquery_details(main_id: str) -> Dict:
    """Get details (magnitude, type, size) via astroquery"""
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
                        details['size_arcmin'] = float(row['galdim_majaxis'])
                    except:
                        pass
                    
    except Exception as e:
        pass
    
    return details


def search_by_name(query: str, limit: int = 15) -> List[SimbadObject]:
    """Search SIMBAD - prioritize exact matches, avoid substring pollution"""
    safe_query = query.replace("'", "''")
    results = []
    found_ids = set()
    
    # Step 0: Normalized exact match FIRST (M31 -> M  31)
    normalized = _normalize_query(query)
    if normalized != query:
        safe_norm = normalized.replace("'", "''")
        adql = f"SELECT TOP 1 main_id, ra, dec FROM basic WHERE main_id = '{safe_norm}'"
        rows = _execute_tap_query(adql)
        for row in rows:
            mid = row.get('main_id')
            ra = row.get('ra')
            dec = row.get('dec')
            if mid and ra is not None and dec is not None:
                found_ids.add(mid)
                ra_h, ra_m, ra_s = _ra_to_hms(ra)
                dec_d, dec_m, dec_s = _dec_to_dms(dec)
                results.append(SimbadObject(
                    main_id=mid, name=mid,
                    ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                    dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s
                ))
    
    # Step 1: Exact match on main_id
    adql = f"SELECT TOP {limit} main_id, ra, dec FROM basic WHERE main_id = '{safe_query}'"
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
    
    # Step 2: Start-of-word match (not substring)
    adql = f"""SELECT TOP {limit} main_id, ra, dec FROM basic 
               WHERE main_id LIKE '{safe_query}%' 
               OR main_id LIKE '% {safe_query}' 
               OR main_id LIKE '% {safe_query} %'"""
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
    
    # Step 3: Alternative identifiers
    if len(results) < 5:
        adql = f"""SELECT TOP {limit} b.main_id, b.ra, b.dec 
                   FROM basic b JOIN ident i ON b.oid = i.oidref 
                   WHERE i.id = '{safe_query}' OR i.id LIKE '{safe_query}%'"""
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
        for r in search_by_name("M31", limit=5):
            print(f"  {r.main_id}: {r.ra_display} / {r.dec_display}")
    else:
        print("✗ Connection failed")
