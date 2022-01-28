import pytest
from demo.models import Company
from demo.models import Customer


@pytest.fixture()
def company(db):
    return Company.objects.create(name="Company")


@pytest.fixture
def freddy(db, company):
    result = Customer.objects.create(name="Freddy", notes="note", company=company)
    print(f"freddy = {result!r} {result.pk!r}")
    return result
