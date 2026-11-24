import pytest

import beziervis as bv

BACKENDS = ["numpy"] + (["numba"] if bv.numba_available() else [])


@pytest.fixture(params=BACKENDS)
def backend(request):
    """Run the test once per installed backend, restoring the original after."""
    previous = bv.get_backend()
    bv.set_backend(request.param)
    yield request.param
    bv.set_backend(previous)
