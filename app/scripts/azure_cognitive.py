from requests import Session


class _CognitiveService(Session):
    """
    Provide single interface for working with Azure Cognitive services.
    :param subscription_key: Azure Subscription key for accessing services.
    :param service_url_suffix: Suffix to the base path for accessing specific service.
    :param region_code: URL prefix specifying the region to make calls to.
    """

    def __init__(self, subscription_key, region_code='eastus'):

        # ensure not clobbering parent init
        super().__init__()

        # set a few variables
        self._region_code = region_code
        self._url_suffix = ''

        # set the session header to include the subscription key
        self.headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
            'Content-Type': 'application/json'
        }

    @property
    def url(self):
        return 'https://{}.api.cognitive.microsoft.com{}'.format(self._region_code, self._url_suffix)


class ComputerVision(_CognitiveService):
    """
    Provide interface for working with Azure Computer Vision.
    :param subscription_key: Azure Subscription key for accessing services.
    :param service_url_suffix: Suffix to the base path for accessing specific service.
    :param region_code: URL prefix specifying the region to make calls to.
    """

    def __init__(self, *args):

        # ensure not clobbering parent init
        super().__init__(*args)

        # set the url suffix for this resource
        self._url_suffix = '/vision/v2.0/analyze'

    def submit(self, image):
        """
        Submit an image for evaluation.
        :param image: Path, either local or url, to the image to be evaluated.
        :return: JSON response.
        """
        # add parameters to use as part of the request
        params = {'visualFeatures': 'Categories,Description,Color'}

        # check to see if the image is a remote or local resource
        if image.startswith('http'):

            # place the image url in the payload
            data = {'url': image}

            # make the request to the
            response = self.post(self.url, params=params, json=data)

        else:
            # open the image before uploading
            image_data = open(image, "rb").read()

            # add the header to be able to upload the image
            self.headers['Content-Type'] = 'application/octet-stream'

            # post the request to Azure Cognitive Vision service
            response = self.post(self.url, params=params, data=image_data)

        return response.json()
