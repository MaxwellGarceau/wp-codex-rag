class CustomException(Exception):
    code = 400
    error_code = "BAD_GATEWAY"

    def __init__(self, message=None):
        if message is None:
            self.message = "BAD GATEWAY"
        elif message == "":
            self.message = ""  # Preserve empty string
        elif message is False:
            self.message = False  # Preserve False
        elif not message:  # Other falsy values (0, [], etc.)
            self.message = "BAD GATEWAY"
        else:
            self.message = message
        super().__init__(self.message)
