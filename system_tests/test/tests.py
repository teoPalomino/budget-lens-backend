from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import subprocess
from django.test import LiveServerTestCase

class SystemTests(LiveServerTestCase):
    """Basic system test to see if the deployed website is running or not"""
    def setUp(self):
        self.is_webapp_deployed = False
        self.browser = webdriver.Chrome(ChromeDriverManager().install())
        self.browser.implicitly_wait(0.5)

    def tearDown(self):
        self.browser.quit()

    def test_deployed_site_running(self):
        """Check if the site is available when it has been deployed"""
        if self.is_webapp_deployed:
            self.browser.get('http://budgetlens.tech/')
            self.assertEqual('BudgetLensBackend', self.browser.title)
        else:
            print("Skipping over system test since the website is not currently deployed on the VPS")

    def test_check_requirements(self):
        """Check if all the requirements have been met"""
        # Record the expected requirements by reading the requirements.xt
        with open("./requirements.txt") as file:
            expected_requirements_packages = file.read()

        # Record the actual requirements by running the subprocess command pip freeze
        sub_process = subprocess.Popen(["pip", "freeze"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        actual_reqirements_packages, error = sub_process.communicate()

        # Remove unesecarry characters and decode the strings to work with the same string types
        expected_requirements_packages = expected_requirements_packages.replace("\r", "").replace("\n", "")
        actual_reqirements_packages = actual_reqirements_packages.decode().replace("\r", "").replace("\n", "")

        self.assertEqual(expected_requirements_packages, actual_reqirements_packages)
        self.assertEqual(error, b'')


