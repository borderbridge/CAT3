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
    
    # M31 -> M  31 (SIMBAD format)
    if q.startswith('M') and len(q) > 1 and q[1:].strip().isdigit():
        return f"M  {q[1:].strip()}"
    
    # NGC7000 -> NGC 7000
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