from util import *


class LoanProductsAPI(AbstractAPI):
    url = 'loanproducts'

    def get(self, loan_product_id=None):
        """

        Parameters
        ----------
        loan_product_id: str
            id or encodedKey for loan product in mambu

        Returns
        -------
        dict
        """
        return self._request('get', self._loan_products_url(loan_product_id))

    def _loan_products_url(self, loan_product_id=None):
        """Construct the url for the api from the loan_product_id
        i.e. return /api/loanproducts/{loan_product_id}

        Parameters
        ----------
        loan_product_id: str
            id or encodedKey for loan product in mambu

        Returns
        -------
        str
        """
        url_ = self.url
        if loan_product_id is not None:
            url_ += '/' + loan_product_id
        return url_

    def get_encoded_key(self, loan_product_id):
        """Returns the encodedKey for the loan product associated with
        loan_product_id

        Parameters
        ----------
        loan_product_id: str
            id or encodedKey for the loan product in mambu

        Returns
        -------
        str
        """
        loan_product = self.get(loan_product_id)
        return loan_product['encodedKey']
