class MambuAPIException(Exception):
    def __init__(self, message, code, status):
        msg = message + ', code: ' + str(code) + ', return code: ' + str(status['returnCode']) + ', return status: ' + str(status['returnStatus'])
        if 'errorSource' in status:
            msg += ', source: ' + str(status['errorSource'])
            self.error_source = status['errorSource']
            
        super(MambuAPIException, self).__init__(msg)
        self.code = code
        self.return_code = status['returnCode']
        self.return_status = status['returnStatus']
