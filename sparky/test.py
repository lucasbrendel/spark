from sparky.base.core import Interface, SparkyError


class TestFailure(SparkyError):
    __test__ = False
    title = "Test Failure"


class TestError(SparkyError):
    __test__ = False
    title = "Test Setup Error"


class TestAbort(SparkyError):
    __test__ = False
    title = "Test Abort"


class SkipTest(Exception):
    pass


class ExpectedFailure(Exception):
    pass


class UnexpectedPass(Exception):
    pass


class ITest(Interface):

    def pre(self):
        pass

    def run(self):
        pass

    def post(self):
        pass


class ITestSetup(Interface):

    def pre(self):
        pass

    def post(self):
        pass


class ITestWatcher(Interface):

    def test_pre(self, name: str):
        pass

    def test_pass(self, name: str):
        pass

    def test_fail(self, name: str):
        pass

    def test_error(self, name: str):
        pass

    def test_skip(self, name: str):
        pass


class ITestFinder(Interface):

    def find(self):
        pass
