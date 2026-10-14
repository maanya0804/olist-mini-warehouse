import duckdb
import pytest
from checks import CHECKS


@pytest.mark.parametrize("name", list(CHECKS))
def test_quality_check(name):
    con = duckdb.connect("warehouse.duckdb", read_only=True)
    bad_rows = con.execute(CHECKS[name]).fetchone()[0]
    con.close()
    assert bad_rows == 0, f"{name} found {bad_rows} bad rows"