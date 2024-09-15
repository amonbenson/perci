"""
This module provides a class to track changes in the data model.
"""

# class ChangeHandler:
#     """
#     A handler for changes in the data model.

#     :param path: The path to watch for changes.
#     :param callback: The callback to invoke when a change occurs.
#     """

#     def __init__(self, path: list[str], callback: callable):
#         self.path = path
#         self.callback = callback


class ChangeTracker:
    """
    A class to track changes in the data model.
    """

    def __init__(self):
        self._changes: list[dict] = []
        # self._handlers: list[ChangeHandler] = []

    def register(self, change_type: str, path: list[str], **kwargs):
        """
        Register a change in the data model.
        """

        change = {"type": change_type, "path": path, **kwargs}

        # store the change
        self._changes.append(change)

        # # remove a handler if its corresponding node is removed (e. g. the handler's path or any of its parents are removed)
        # if change_type == "remove":
        #     for handler in self._handlers:
        #         if self._is_subpath(handler.path, path) or handler.path == path:
        #             self._handlers.remove(handler)

        # # invoke a handler if any change occurs on its path or any of its children
        # for handler in self._handlers:
        #     if self._is_subpath(path, handler.path) or handler.path == path:
        #         handler.callback(change)

    # def _is_subpath(self, p1: list[str], p2: list[str]) -> bool:
    #     """
    #     Return True if p1 is a subpath of p2
    #     """

    #     return (len(p2) > len(p1)) and (all(p1[i] == p2[i] for i in range(len(p1))))

    # def add_handler(self, path: list[str], handler: callable):
    #     """
    #     Add a handler to invoke when a change occurs on the given path.
    #     """

    #     self._handlers.append(ChangeHandler(path, handler))

    def clear(self):
        """
        Clear all changes.
        """

        self._changes.clear()

    def get_changes(self):
        """
        Get all changes.
        """

        return self._changes
