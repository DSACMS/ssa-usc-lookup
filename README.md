# ssa-usc-lookup

Look up the full U.S. Code text for any Social Security Act section number. Static site, no install required, data refreshed weeklly.

## About the Project

**{project_statement}**


### Project Vision
**{project vision}** 


### Project Mission
**{project mission}** 


### Agency Mission
TODO: Good to include since this is an agency-led project 


### Team Mission
TODO: Good to include since this is an agency-led project 


## Core Team

A list of core team members responsible for the code and documentation in this repository can be found in [COMMUNITY.md](COMMUNITY.md).


## Repository Structure
<pre>
.
├── build.py
├── build.yml
├── COMMUNITY.md
├── data.json
├── index.html
├── LICENSE
├── README.md
├── repolinter.json
├── requirements.txt
└── statute2.py
</pre>


- **build.yml**: Runs build.py as a GitHub action
- **build.py**: Runs the script that scrapes the US Code (USC) and Social Security Act (SSA) locally and generates data.json and index.html files.
- **data.json**: Collection of USC and SSA text saved locally so it can be served on static pages or local machines without a db.
- **index.html**: barebones web UI for looking up sections of the Social Security Act (SSA) from data.json
- **statute2.py**: Library for linking USC and SSA texts.


## Local Development

 TODO - with example below:
This project is monorepo with several apps. Please see the [api](./api/README.md) and [frontend](./frontend/README.md) READMEs for information on spinning up those projects locally. Also see the project [documentation](./documentation) for more info.


<!--
## Coding Style and Linters

TODO - Add the repo's linting and code style guidelines

Each application has its own linting and testing guidelines. Lint and code tests are run on each commit, so linters and tests should be run locally before committing.
 -->

## Branching Model

This project follows [trunk-based development](https://trunkbaseddevelopment.com/), which means:

* Make small changes in [short-lived feature branches](https://trunkbaseddevelopment.com/short-lived-feature-branches/) and merge to `main` frequently.
* Be open to submitting multiple small pull requests for a single ticket (i.e. reference the same ticket across multiple pull requests).
* Treat each change you merge to `main` as immediately deployable to production. Do not merge changes that depend on subsequent changes you plan to make, even if you plan to make those changes shortly.
* Ticket any unfinished or partially finished work.
* Tests should be written for changes introduced, and adhere to the text percentage threshold determined by the project.

This project uses **continuous deployment** using [Github Actions](https://github.com/features/actions) which is configured in the [./github/workflows](.github/workflows) directory.

Pull-requests are merged to `main` and the changes are immediately deployed to the development environment. Releases are created to push changes to production.

## Policies

### Open Source Policy

We adhere to the [CMS Open Source Policy](https://github.com/CMSGov/cms-open-source-policy). If you have any questions, just [shoot us an email](mailto:opensource@cms.hhs.gov).

### Security and Responsible Disclosure Policy

_Submit a vulnerability:_ Vulnerability reports can be submitted through [Bugcrowd](https://bugcrowd.com/cms-vdp). Reports may be submitted anonymously. If you share contact information, we will acknowledge receipt of your report within 3 business days.

### Software Bill of Materials (SBOM)

A Software Bill of Materials (SBOM) is a formal record containing the details and supply chain relationships of various components used in building software.

In the spirit of [Executive Order 14028 - Improving the Nation's Cyber Security](https://www.gsa.gov/technology/it-contract-vehicles-and-purchasing-programs/information-technology-category/it-security/executive-order-14028), a SBOM for this repository is provided here: https://github.com/DSACMS/ssa-usc-lookup/network/dependencies.

For more information and resources about SBOMs, visit: https://www.cisa.gov/sbom.

## Public domain

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/) as indicated in [LICENSE](LICENSE).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request or issue, you are agreeing to comply with this waiver of copyright interest.
