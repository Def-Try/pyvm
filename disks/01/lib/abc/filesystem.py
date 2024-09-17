class FSException(Exception): pass
class AlreadyMounted(FSException): pass
class UsedByMounted(FSException): pass
class AlreadyExists(FSException): pass
class PathInvalid(FSException): pass
class NoSuchFileOrDirectory(FSException): pass
class IsNotADirectory(FSException): pass

