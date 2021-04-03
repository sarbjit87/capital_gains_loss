import pytest
from capital_gains_loss import create_app
from capital_gains_loss.config import TestConfig
import os
import multiprocessing

multiprocessing.set_start_method("fork")

@pytest.fixture(scope="session")
def app(request):
    app = create_app(TestConfig)
    return app
