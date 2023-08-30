from quiltcore import Codec, Domain, Factory, Node, Scheme, quilt

from .conftest import LOCAL_VOL

def test_node():
    codec = Codec()
    node = Node(codec, 'test', None)
    assert node

def test_node_factory():
    assert quilt
    assert isinstance(quilt, Factory)
    assert quilt.name == 'quilt'

def test_node_scheme():
    s3 = quilt['s3']
    assert s3
    assert isinstance(s3, Scheme)
    assert s3.name == 's3'
    assert quilt['file']

def test_node_domain():
    f = quilt['file']
    dom = f[LOCAL_VOL]
    assert dom
    assert isinstance(dom, Domain)

    uri = 'file://' + LOCAL_VOL
    dom2 = Domain.FromURI(uri)
    assert dom2 == dom
