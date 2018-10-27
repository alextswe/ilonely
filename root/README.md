# iLonely
A webapp to connect lonely people with other lonely people.

## Current Sprint Goals:
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

### VS Notes
If you are get this error
```
Severity Code Description Project File Line Suppression State Error The reference assemblies for framework ".NETFramework,Version=v4.0" were not found. To resolve this, install the SDK or Targeting Pack for this framework version or retarget your application to a version of the framework for which you have the SDK or Targeting Pack installed. Note that assemblies will be resolved from the Global Assembly Cache (GAC) and will be used in place of reference assemblies. Therefore your assembly may not be correctly targeted for the framework you intend. DjangoWebProject1 C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\Microsoft.Common.CurrentVersion.targets 1179
```
Boot up your **Visual Studio Installer**. Select **Modify** for whatever version of Visual Studio you are using. Got to the **Individual components** tab and check **.NET Framework 4 targeting pack**. Click **Modify** in the lower right corner and you should be good to go.
