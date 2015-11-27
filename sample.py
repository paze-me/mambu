import mambuapi
import datetime
import json
import logging
logging.basicConfig(level=logging.DEBUG)

config = mambuapi.Config()
config.domain = 'pazeme.sandbox.mambu.com'
config.username = 'apiuser'
config.password = '11ApiUserPassword11'

api = mambuapi.API(config)
try:
    cl = api.Clients.get(None, api.Clients.GetClientParams(fullDetails = True))
    print cl

    val = api.Loans.get(None)
    print val

    val = api.LoanTransactions.get(val[0]['encodedKey'])
    print val
    
    val = api.Savings.get()
    print val
    
    val = api.SavingsTransactions.get(val[0]['encodedKey'])
    print val
    
    val = api.Attachments.getForClient(cl[0]['encodedKey'])
    print val
    
    val = api.CustomFields.get_sets('CLIENT_INFO')
    print val
    
except mambuapi.MambuAPIException as e:
    print e.message + ", http code: " + str(e.code) + ", mambu code: " + str(e.return_code) + " " + e.return_status
    