
from typing import Optional


class SparkyError(Exception):

    def __init__(self, message: Optional[str] = None, title: Optional[str] = None, show_traceback=False):
        super().__init__(self, message)
        self._message = message
        self.title = title or self.title
        self.show_traceback = show_traceback

    message = property(lambda self: self._message,
                       lambda self, v: setattr(self, '_message', v))
