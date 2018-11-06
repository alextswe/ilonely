# iLonely
A webapp to connect lonely people with other lonely people.

## Current Sprint Goals:
 + Feed
 + Messaging
 + Discover Nearby

## Sprint 1 Goals:
 + Registration
   + Users must input a unique **username** and **email** to register.
   + User must also input **first name**, **last name**, and **age**
   + Password must be at least 8 characters and cannot be entirely numeric
   + Emails users upon successful registration
 + Secure Login
 + Change/Update Profile

## Visual Studio Virtual Environment Setup
 1. Open the project in Visual Studio by clicking on the `.sln` file.
 2. In the **Solution Explorer Window**, right click on **Python Environments**.
 3. Select **Add Virtual Environment**. Make sure the location is `env/`.
 4. Click **Create** and wait for the packages to install.
 5. Make sure to activate your environement by right clicking on `env` and selecting **Activate Environment**.

A virtual environment should be generated according to the `requirements.txt` file. Make sure to update the `requirements.txt` by right clicking on env and selecting **Generate requirements.txt**.

For those not using Visual Studio use the command `pip install -r requirements.txt` to set up your virtual environment and `pip freeze > requirements.txt` to generate the requirements file.
