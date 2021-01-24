# IgnitionSwagger
This is an implementation of Version 2 of the Open API Specification Standard (aka Swagger) using only Ignition WebDev and Scripting resources.

## Status
This is a work in progress. It is currently in a **early Alpha** state.

## Compatibility
This project is compatible with **Ignition 8.1**.

---

# Installation


## Installing Ignition
The use of this project, as is evident in the name, requires an installation of Ignition. The Ignition software is industrial automation software provided by Inductive Automation. However, it has a variety of other potential uses, and this project is an example of using it as a REST API Service provider.

To install Ignition, visit the [Ignition Downloads page](https://inductiveautomation.com/downloads/) to download an Ignition installer.

Installation instructions can be found on the [Inductive Automation Docs](https://docs.inductiveautomation.com/display/DOC81/Installing+and+Upgrading+Ignition]).

If you are installing the _Maker Edition_ version of Ignition, you will need a Maker License, which can be generated for free using your [IA Account](https://account.inductiveautomation.com/manage-licenses/). More information about _Maker Edition_ can be found on the [Inductive Automation Docs](https://docs.inductiveautomation.com/display/DOC81/Maker+Edition).

#### Required Ignition Modules
This project only requires the **WebDev Module**.

---

## Installing the `IgnitionSwagger` Project
Once Ignition is installed, you will need to manually install the Ignition Project files on your gateway.

#### Step 1. Create Project Directory
On your Ignition Gateway, navigate to your `projects` directory.
- Mac: `/usr/local/ignition/data/projects`
- Windows: `C:\Program Files\Inductive Automation\Ignition\data\projects`
- Linux: `/var/lib/ignition/data/projects`

Create a new directory. This will be the name of your project.

#### Step 2. Import Project Resources
This Github Repository contains the resources of an Ignition Project. Simply copy all of the files present into your new Project Directory.

After copying the files into the directory, the Ignition Gateway should automatically become aware of the new projects.

#### Step 3. Update Project Meta information
_This step is OPTIONAL._

The `project.json` file in the repository contains meta information about the project. By default, the `title` and `description` will contain the values present in this template.

These properties can be updated directly in the file or by using the Gateway Browser Console.

---

# Postman Requests for Testing
[Postman](https://www.postman.com/) is a fantastic tool for API development and testing.

Use the Postman Exports found in `___` to easily test this project on a locally installed version of Ignition.

To adjust the Postman Request resources to work with an externally-hosted Ignition Gateway that has this project installed, simply edit the Environment Variable `URL` to be the base of your Ignition Gateway's API service.

---

## Remaining Work To Do
- [x] ~~Flesh out `README` at repository root level, explaining how to safely set up an Ignition project with these resources.~~
- [ ] Fully implement mock `Pet Store` endpoints.
- [ ] Document how to call the `test` endpoints.
- [ ] Provide export of Postman requests for easier testing.
- [ ] Flesh out `README` Script Resource in Ignition, explaining how to create new endpoints.
- [ ] Document where to find "Project Variables" that can be changed, and what they can be safely changed to.
