## Steps to CI/CD

- Clone the CI/CD project to local.
- Ensure that the `openrc.sh` file of an admin user is handy.
- CI/CD project requires the installation of a few python modules (libraries) before it can be run.
  For that, run `pip install -r requirements.txt` from inside the CI/CD project.
  If the error `command not found` pops up, install `python-pip` and `python-dev` via apt.
  Note: This is a one time step.
- Edit the **cicd.conf** file to refer to the correct paths.
  (Run `cicd/common.py` if this is a first time set up.)
- Source the `openrc.sh` file.
- Run `cicd.py`.
