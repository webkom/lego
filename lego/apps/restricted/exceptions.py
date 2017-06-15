class ParserException(Exception):
    """
    Base exception for the email parser.
    """
    pass


class ParseEmailException(ParserException):
    """
    Raised when the parser can't create a email.message.Message object of the raw string or bytes.
    """
    pass


class MessageIDNotExistException(ParserException):
    """
    Raised when a message not contain a message-id
    """
    pass


class DefectMessageException(ParserException):
    """
    Raised when the recieved message is defect.
    """
    pass
