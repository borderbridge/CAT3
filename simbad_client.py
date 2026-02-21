"""
SIMBAD Client - Astronomical Data Query via astroquery
Clean implementation using CDS astroquery module
"""
from typing import Optional, List
from dataclasses import dataclass

try:
    from astroquery.simbad import Simbad
    from astropy.coordinates import SkyCoord
    ASTROQUERY_AVAILABLE = True
except ImportError:
    ASTROQUERY_AVAILABLE = False


@dataclass
class SimbadObject:
    """Represents an astronomical object from SIMBAD"""
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


def _map_object_type(otype: str) -> str:
    """Map SIMBAD object type to CAT3 types"""
    if not otype:
        return "unknown"
    
    st = str(otype).strip()
    
    # Direct mappings
    type_map = {
        'G': 'galaxy',
        'Galaxy': 'galaxy',
        'AGN': 'galaxy',
        'Seyfert': 'galaxy',
        'Seyfert_1': 'galaxy',
        'Seyfert_2': 'galaxy',
        'LINER': 'galaxy',
        'QSO': 'galaxy',
        'PN': 'planetary_nebula',
        'PlanetaryNeb': 'planetary_nebula',
        'SNR': 'supernova_remnant',
        'HII': 'nebula',
        'Neb': 'nebula',
        'GlC': 'globular_cluster',
        'GlobularCl': 'globular_cluster',
        'OpC': 'open_cluster',
        'OpenCl': 'open_cluster',
        'Cl*': 'open_cluster',
        '*': 'star',
        'Star': 'star',
        '**': 'double_star',
        'Planet': 'planet',
        'Comet': 'comet',
        'Asteroid': 'asteroid',
        'Moon': 'moon',
        'Sun': 'sun',
    }
    
    return type_map.get(st, "unknown")


def search_by_name(query: str, limit: int = 15) -> List[SimbadObject]:
    """Search SIMBAD by object name using astroquery"""
    if not ASTROQUERY_AVAILABLE:
        return []
    
    results = []
    found_ids = set()
    
    # Configure SIMBAD query
    simbad = Simbad()
    simbad.ROW_LIMIT = limit
    
    # Add votable fields we want
    simbad.add_votable_fields('otype')  # object type
    simbad.add_votable_fields('V')      # V magnitude
    simbad.add_votable_fields('dimensions')  # size dimensions
    simbad.add_votable_fields('galdim_majaxis')  # major axis for size
    
    try:
        # Query by object name
        table = simbad.query_object(query)
        
        if table is not None:
            for row in table:
                try:
                    main_id = row['MAIN_ID'] if 'MAIN_ID' in row.colnames else ""
                    if not main_id or main_id in found_ids:
                        continue
                    found_ids.add(main_id)
                    
                    ra = float(row['RA']) if 'RA' in row.colnames else None
                    dec = float(row['DEC']) if 'DEC' in row.colnames else None
                    
                    if ra is None or dec is None:
                        continue
                    
                    ra_h, ra_m, ra_s = _ra_to_hms(ra)
                    dec_d, dec_m, dec_s = _dec_to_dms(dec)
                    
                    # Get magnitude V
                    mag_v = None
                    if 'FLUX_V' in row.colnames and row['FLUX_V']:
                        try:
                            mag_v = float(row['FLUX_V'])
                        except:
                            pass
                    
                    # Get size
                    size = None
                    if 'GALDIM_MAJAXIS' in row.colnames and row['GALDIM_MAJAXIS']:
                        try:
                            size = float(row['GALDIM_MAJAXIS']) * 60  # deg to arcmin
                        except:
                            pass
                    
                    # Get type
                    otype = row['OTYPE'] if 'OTYPE' in row.colnames else ""
                    
                    obj = SimbadObject(
                        main_id=str(main_id),
                        name=str(main_id),
                        ra_hours=ra_h, ra_minutes=ra_m, ra_seconds=ra_s,
                        dec_degrees=dec_d, dec_minutes=dec_m, dec_seconds=dec_s,
                        object_type=_map_object_type(otype),
                        magnitude_v=mag_v,
                        size_arcmin=size,
                        morphology=str(otype) if otype else None
                    )
                    results.append(obj)
                    
                except Exception as e:
                    continue
                    
    except Exception as e:
        print(f"SIMBAD query error: {e}")
        return []
    
    return results


def test_connection() -> bool:
    """Test if SIMBAD is reachable via astroquery"""
    if not ASTROQUERY_AVAILABLE:
        return False
    
    try:
        simbad = Simbad()
        simbad.ROW_LIMIT = 1
        result = simbad.query_object('M 1')
        return result is not None
    except:
        return False


if __name__ == "__main__":
    if not ASTROQUERY_AVAILABLE:
        print("ERROR: astroquery not installed")
        print("Run: pip install astroquery")
        exit(1)
    
    print("Testing SIMBAD client (astroquery)...")
    if test_connection():
        print("✓ Connected to SIMBAD")
        print("\nSearching M31:")
        for r in search_by_name("M 31", limit=3):
            print(f"  {r.main_id}: {r.ra_display} / {r.dec_display}")
            print(f"    Type: {r.object_type}, Mag V: {r.magnitude_v}, Size: {r.size_arcmin}")
    else:
        print("✗ Connection failed")