from sqlobject import events

from sqlobject import *
from sqlobject.tests.dbtest import *

########################################
## Transaction test
########################################

class TestSOTrans(SQLObject):
    #_cacheValues = False
    class sqlmeta:
        defaultOrder = 'name'
    name = StringCol(length=10, alternateID=True, dbName='name_col')


def make_watcher():
    log = []
    def watch(*args):
        log.append(args)
    watch.log = log
    return watch


def make_listen(signal):
    watcher = make_watcher()
    events.listen(watcher, sqlmeta, signal)
    return watcher


def test_transaction():
    watcher = make_listen(events.CommitSignal)
    if not supports('transactions'):
        return
    setupClass(TestSOTrans)
    TestSOTrans(name='bob')
    TestSOTrans(name='tim')
    trans = TestSOTrans._connection.transaction()
    try:
        TestSOTrans._connection.autoCommit = 'exception'
        TestSOTrans(name='joe', connection=trans)
        trans.rollback()
        trans.begin()
        assert ([n.name for n in TestSOTrans.select(connection=trans)]
                == ['bob', 'tim'])
        b = TestSOTrans.byName('bob', connection=trans)
        b.name = 'robert'
        trans.commit()

        assert len(watcher.log) == 1
        assert watcher.log[0][0][0][0] == 'TestSOTrans'
        assert watcher.log[0][0][0][1] == [1, 2]

        assert b.name == 'robert'
        b.name = 'bob'
        trans.rollback()
        trans.begin()
        assert b.name == 'robert'
    finally:
        TestSOTrans._connection.autoCommit = True


def test_transaction_commit_sync():
    if not supports('transactions'):
        return
    setupClass(TestSOTrans)
    trans = TestSOTrans._connection.transaction()
    try:
        TestSOTrans(name='bob')
        bOut = TestSOTrans.byName('bob')
        bIn = TestSOTrans.byName('bob', connection=trans)
        bIn.name = 'robert'
        assert bOut.name == 'bob'
        trans.commit()
        assert bOut.name == 'robert'
    finally:
        TestSOTrans._connection.autoCommit = True


def test_transaction_delete(close=False):
    if not supports('transactions'):
        return
    setupClass(TestSOTrans)
    trans = TestSOTrans._connection.transaction()
    try:
        TestSOTrans(name='bob')
        bIn = TestSOTrans.byName('bob', connection=trans)
        bIn.destroySelf()
        bOut = TestSOTrans.select(TestSOTrans.q.name=='bob')
        assert bOut.count() == 1
        bOutInst = bOut[0]
        bOutID = bOutInst.id
        trans.commit(close=close)
        assert bOut.count() == 0
        raises(SQLObjectNotFound, "TestSOTrans.get(bOutID)")
        raises(SQLObjectNotFound, "bOutInst.name")
    finally:
        trans.rollback()
        TestSOTrans._connection.autoCommit = True


def test_transaction_delete_with_close():
    test_transaction_delete(close=True)
