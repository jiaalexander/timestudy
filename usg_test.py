import pytest

from usg import *

def test_url_to_hostname():
    assert url_to_hostname("http://www.nist.gov/") == 'www.nist.gov'
    assert url_to_hostname("http://www.nist.gov:99/") == 'www.nist.gov'
    assert url_to_hostname("https://www.nist.gov/") == 'www.nist.gov'

def test_usg_from_analytics():
    ret = usg_from_analytics()
    assert type(ret)==list
    assert "18f.gsa.gov" in ret

