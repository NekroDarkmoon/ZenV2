# Contributing to Zen

A big welcome, and thank you for considering contributing to Zen!

Reading and following these guidelines will help us make the contribution process easy and effective for everyone involved. It also communicates that you agree to respect the time of the developers managing and developing this project. In return, we will reciprocate that respect by addressing your issue, assessing changes, and helping you finalize your pull requests.

## Quicklinks

- [Contributing to Zen](#contributing-to-Zen)
  - [Quicklinks](#quicklinks)
  - [Code of Conduct](#code-of-conduct)
  - [Getting Started](#getting-started)
    - [Issues](#issues)
    - [Commits](#commits)
    - [Pull Requests](#pull-requests)
  - [Code Quality](#code-quality)

## Code of Conduct

We take our open source community seriously and hold ourselves and other contributors to high standards of communication. By participating and contributing to this project, you agree to uphold our [Code of Conduct].

## Getting Started

Contributions are made to this repo via Issues and Merge Requests (MRs). A few general guidelines that cover both:

- Search for existing Issues and PRs before creating your own.
- We work hard to make sure issues are handled promptly but, depending on the impact, it could take a while to investigate the root cause. A friendly ping in the comment thread to the submitter or a contributor can help draw attention if your issue is blocking.

### Issues

Issues should be used to report problems with the library, request a new feature, or discuss potential changes before a PR is created. When you create a new Issue, a template will be loaded that will instruct you to select the appropriate template and guide you to fill out the required information.

If you find an Issue that addresses the problem you're having, please add your reproduction information to the existing issue rather than creating a new one. Adding a [reaction](https://docs.gitlab.com/ee/user/award_emojis.html) can also help be indicating to our maintainers that a particular problem is affecting more than just the reporter.

If you are starting work on an issue, please assign it to yourself and move it to the "In Progress" column on the [board](https://github.com/NekroDarkmoon/Zen/projects/1) or add the "In Progress" label manually. This is to avoid two people working on the same issue at the same time without knowing. This should be done even for a small task.

### Commits

We ask that commits be kept clean, avoid messages that only make sense to you, and follow good practices. Read this [blog post by Chris Beams](https://chris.beams.io/posts/git-commit/), and you'll be good to go!

Here is a TLDR:

- Separate subject from body with a blank line
- Limit the subject line to 50 characters
- Capitalize the subject line
- Do not end the subject line with a period
- Use the imperative mood in the subject line
- Wrap the body at 72 characters
- Use the body to explain what and why vs. how

### Pull Requests

MRs to the project are always welcome and can quickly get your fix or improvement slated for the next release. In general, MRs should:

- Only fix/add the functionality in question **OR** address wide-spread whitespace/style issues, not both.
- Add unit or integration tests for fixed or changed functionality (if a test suite already exists).
- Address a single concern in the least number of changed lines as possible.
- Be accompanied by a complete Merge Request template (must be selected when creating the Merge Request).

For changes that address core functionality or require breaking changes (e.g. a major release), it's best to open an Issue to discuss your proposal first. This is not required but can save time creating and reviewing changes.

In general, we follow the ["fork-and-pull" Git workflow](https://github.com/susam/gitpr)

1. Fork the repository to your own Github account
2. Clone the project to your machine
3. Create a branch locally with a succinct but descriptive name
4. Commit changes to the branch
5. Following any formatting and testing guidelines specific to this repo
6. Push changes to your fork
7. Open a MR in our repository and follow the MR template so that we can efficiently review the changes.

