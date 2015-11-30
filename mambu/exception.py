class MambuAPIException(Exception):
    def __init__(self, message, code, status):
        msg = '{}, code: {}, return code: {}, return status: {}'.format(
            message, code, status.get('returnCode', ''),
            status.get('returnStatus', ''))
        if 'errorSource' in status:
            msg += ', source: ' + str(status['errorSource'])
            self.error_source = status['errorSource']
            
        super(MambuAPIException, self).__init__(msg)
        self.code = code
        self.return_code = status['returnCode']
        self.return_status = status['returnStatus']
