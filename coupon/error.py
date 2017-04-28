class Error(Exception):
    pass


class UserFacingError(Error):
    """Error which faces end user."""

    def to_dict(self):
        return {'name': self.__class__.__name__, 'args': self.args}

    @property
    def http_status(self):
        return 500

    @property
    def template_name(self):
        return 'error.html'

    @property
    def message(self):
        return 'An error has occurred.'


class BadRequestError(UserFacingError):
    @property
    def http_status(self):
        return 400


class ForbiddenError(UserFacingError):
    @property
    def http_status(self):
        return 403


class NotFoundError(UserFacingError):
    @property
    def http_status(self):
        return 404

    @property
    def message(self):
        return 'Path {0} not found.'


class ValidationError(ForbiddenError):
    @property
    def message(self):
        if len(self.args) == 1:
            return 'Field {0} validation failed.'
        elif len(self.args) == 2:
            return 'Field {0} or {1} validation failed.'


class UnknownArgumentError(BadRequestError):
    @property
    def message(self):
        return 'Argument {0} if unknown.'


class CouponNotFoundError(NotFoundError):
    @property
    def message(self):
        return 'Coupon {0} not found.'


class FileTypeNotAllowedError(ValidationError):
    @property
    def message(self):
        return 'This type of files are not allowed to be uploaded.'
