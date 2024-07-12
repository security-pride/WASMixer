class ErrUnexpectedEnd(Exception):

    def __init__(self):
        super().__init__("unexpected end of section or function")

    def __str__(self):
        print("unexpected end of section or function")


class ErrIntTooLong(Exception):

    def __init__(self):
        super().__init__("integer representation too long")

    def __str__(self):
        print("integer representation too long")


class ErrIntTooLarge(Exception):

    def __init__(self):
        super().__init__("integer too large")

    def __str__(self):
        print("integer too large")
