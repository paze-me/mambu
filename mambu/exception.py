class MambuAPIException(Exception):
    def __init__(self, message, code, status):
        self.return_code = status.get('returnCode', '')
        self.return_status = status.get('returnStatus', '')
        self.code = code

        msg = '{}, code: {}, return code: {}, return status: {}'.format(
            message, self.code, self.return_code, self.return_status,
        )
        if 'errorSource' in status:
            msg += ', source: ' + str(status['errorSource'])
            self.error_source = status['errorSource']

        super(MambuAPIException, self).__init__(msg)
