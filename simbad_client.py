"""
SIMBAD Client - Astronomical Data Query via TAP Service
Minimal, stable version using only urllib
"""
import urllib.request
import urllib.parse
import json
from typing import Optional, List, Dict
from dataclasses import dataclass

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
    
    @property
    def ra_display(self) -> str:
        return f"{self.ra_hours:02d}:{self.ra_minutes:02d}:{self.ra_seconds:05.2f}"
    
    @property
    def dec_display(self) -> str:
        sign = "+" if self.dec_degrees >= 0 else "-"
        return f"{sign}{abs(self.dec_degrees):02d}:{self.dec_minutes:02d}:{self.dec_seconds:05.2f}"


def _ra_to_hms(ra_deg: float) -> tuple:
    ra_h = ra_deg / 15.0
    h = int(ra_h)
    m = int((ra_h - h) * 60)
    s = ((ra_h - h) * 60 - m) * 60
    return h, m, s


def _dec_to_dms(dec_deg: float) -> tuple:
    sign = 1 if dec_deg >= 0 else -1
    d_abs = abs(dec_deg)
    d = int(d_abs) * sign
    m = int((d_abs - int(d_abs)) * 60)
    s = ((d_abs - int(d_abs)) * 60 - m) * 60
    return d, m, s


def _execute_query(adql: str) -> List[Dict]:
    """Execute ADQL query, return raw data rows"""
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


def search_by_name(query: str, limit: int = 15) -> List[SimbadObject]:
    """Search SIMBAD for objects matching query"""
    safe_query = query.replace("'", "''")
    results = []
    found_ids = set()
    
    # Search 1: Try exact match first
    adql = f"SELECT TOP {limit} main_id, ra, dec FROM basic WHERE main_id = '{safe_query}'"
    rows = _execute_query(adql)
    for row in rows:
        if row.get('main_id') and row.get('ra') is not None and row.get('dec') is not None:
            if row['main_id'] not in found_ids:
                found_ids.add(row['main_id'])
                ra_h, ra_m, ra_s = _ra_to_hms(row['ra'])
                dec_d, dec_m, dec_s = _dec_to_dms(row['dec'])
                results.append(SimbadObject(
                    main_id=row['main_id'],
                    name=row['main_id'],
                    ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                    dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s
                ))
    
    # Search 2: Normalized format (M  31, etc.)
    if len(results) < 5:
        normalized = _normalize_query(query)
        if normalized != query:
            safe_norm = normalized.replace("'", "''")
            adql = f"SELECT TOP {limit} main_id, ra, dec FROM basic WHERE main_id LIKE '%{safe_norm}%'"
            rows = _execute_query(adql)
            for row in rows:
                if row.get('main_id') and row.get('ra') is not None and row.get('dec') is not None:
                    if row['main_id'] not in found_ids:
                        found_ids.add(row['main_id'])
                        ra_h, ra_m, ra_s = _ra_to_hms(row['ra'])
                        dec_d, dec_m, dec_s = _dec_to_dms(row['dec'])
                        results.append(SimbadObject(
                            main_id=row['main_id'],
                            name=row['main_id'],
                            ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                            dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s
                        ))
    
    # Search 3: Alternative identifiers
    if len(results) < 5:
        adql = f"""SELECT TOP {limit} b.main_id, b.ra, b.dec 
                   FROM basic b 
                   JOIN ident i ON b.oid = i.oidref 
                   WHERE i.id LIKE '%{safe_query}%'"""
        rows = _execute_query(adql)
        for row in rows:
            if row.get('main_id') and row.get('ra') is not None and row.get('dec') is not None:
                if row['main_id'] not in found_ids:
                    found_ids.add(row['main_id'])
                    ra_h, ra_m, ra_s = _ra_to_hms(row['ra'])
                    dec_d, dec_m, dec_s = _dec_to_dms(row['dec'])
                    results.append(SimbadObject(
                        main_id=row['main_id'],
                        name=row['main_id'],
                        ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                        dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s
                    ))
    
    return results[:limit]


def get_object_details(main_id: str) -> Dict:
    """Get additional details for a specific object by main_id"""
    safe_id = main_id.replace("'", "''")
    details = {'magnitude_v': None, 'size_arcmin': None, 'constellation': None, 'otype': None}
    
    # Get magnitude V
    adql = f"""SELECT flux FROM flux 
               WHERE oidref=(SELECT oid FROM basic WHERE main_id='{safe_id}') 
               AND filter='V' LIMIT 1"""
    rows = _execute_query(adql)
    if rows and rows[0].get('flux'):
        try:
            details['magnitude_v'] = float(rows[0]['flux'])
        except:
            pass
    
    # Get size (major axis in degrees, convert to arcmin)
    adql = f"""SELECT galdim_majaxis FROM basic WHERE main_id='{safe_id}'"""
    rows = _execute_query(adql)
    if rows and rows[0].get('galdim_majaxis'):
        try:
            details['size_arcmin'] = float(rows[0]['galdim_majaxis']) * 60
        except:
            pass
    
    # Get constellation
    adql = f"""SELECT constellation FROM basic WHERE main_id='{safe_id}'"""
    rows = _execute_query(adql)
    if rows and rows[0].get('constellation'):
        details['constellation'] = rows[0]['constellation']
    
    # Get object type
    adql = f"""SELECT otype FROM basic WHERE main_id='{safe_id}'"""
    rows = _execute_query(adql)
    if rows and rows[0].get('otype'):
        details['otype'] = rows[0]['otype']
    
    return details


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
    print("Testing SIMBAD client...")
    if test_connection():
        print("✓ Connected to SIMBAD")
        print("\nTesting M31 search:")
        for r in search_by_name("M31", limit=3):
            print(f"  {r.main_id}: {r.ra_display} / {r.dec_display}")
    else:
        print("✗ Connection failed")