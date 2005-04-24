from sqlobject import *
from sqlobject.sqlbuilder import *
from sqlobject.tests.dbtest import *

########################################
## Subqueries (subselects)
########################################

class TestIn1(SQLObject):
    col1 = StringCol()

class TestIn2(SQLObject):
    col2 = StringCol()

def setup():
    setupClass(TestIn1)
    setupClass(TestIn2)

def insert():
    setup()
    TestIn1(col1=None)
    TestIn1(col1='')
    TestIn1(col1="test")
    TestIn2(col2=None)
    TestIn2(col2='')
    TestIn2(col2="test")

def test_1syntax_in():
    setup()
    select = TestIn1.select(IN(TestIn1.q.col1, Select(TestIn2.q.col2)))
    assert str(select) == \
        "SELECT test_in1.id, test_in1.col1 FROM test_in1 WHERE test_in1.col1 IN (SELECT test_in2.col2 FROM test_in2)"

def test_2perform_in():
    insert()
    select = TestIn1.select(IN(TestIn1.q.col1, Select(TestIn2.q.col2)))
    assert select.count() == 2

def test_3syntax_exists():
    setup()
    select = TestIn1.select(NOTEXISTS(Select(TestIn2.q.col2, where=(Outer(TestIn1).q.col1 == TestIn2.q.col2))))
    assert str(select) == \
        "SELECT test_in1.id, test_in1.col1 FROM test_in1 WHERE NOT EXISTS (SELECT test_in2.col2 FROM test_in2 WHERE (test_in1.col1 = test_in2.col2))"

def test_4perform_exists():
    insert()
    select = TestIn1.select(EXISTS(Select(TestIn2.q.col2, where=(Outer(TestIn1).q.col1 == TestIn2.q.col2))))
    assert len(list(select)) == 2
