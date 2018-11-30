This project is an effort to cover all files contained within a [Facebook profile dump](https://www.facebook.com/help/1701730696756992) with appropriate schemas. It started as a side project of [plaso](https://github.com/log2timeline/plaso)'s Facebook plugin.

## Rationale

Art. 20 GDPR endows users with

> the right to receive the personal data concerning him or her, which he or she has provided to a controller, in a structured, commonly used and machine-readable format

While complying with this principle, Facebook does not provide a way to fully understand and interpret information contained in the profile dump any user can download, leaving those who want to perform automatic data scraping unable.

Hence this project aims at reconstructing the possible structure of such files, covering each one with an appropriate JSON schema.

## Contributing

Given the purpose of this project, the main contribution the community may bring is a better coverage of dump files. To achieve this, users can download their profile and inspect it with `reporter.py`, a tool created to spot and outline uncovered files and fields. The tool is compatible with both Python 2 and 3 and only requires the [jsonschema](https://github.com/Julian/jsonschema) library, found in [pypi](https://pypi.org/project/jsonschema/) or available as a [standalone package](https://packages.debian.org/python-jsonschema) in Debian and most derivatives.

Pull requests are welcome.
