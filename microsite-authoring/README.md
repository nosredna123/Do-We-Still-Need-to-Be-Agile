# Non-published snapshot authoring archive

**Never deploy this directory. Copy only `../microsite/` to the web server.**
These files contain internal source mappings and fingerprints and are not covered
by public whole-directory anonymity approval.

T023 preserved the original preparation contract, planning history, operational
history ([original README](original-README.md)), and source-specific tools here
before sanitizing public documentation and tooling. The archived contract retains
its originally approved SHA-256:
`5cb0534f36bcee75eb08d56fda403f6ef443c826400ca790c727223972e52c68`.
It must not be substituted with the source-free public documentation for approval
validation. No approval records, identifier registry, observations, or lineage
files have been copied into this archive.

Run source-preparation synthetic regressions from the repository root:

```sh
python3 -B -m unittest discover -s microsite-authoring/tools -p 'test_*.py'
```

The archived [preparation utility](tools/prepare_snapshot.py) retains its explicit
source root, approval, registry, omission-decision, output and private-lineage
arguments. See the [original procedure](original-README.md#snapshot-authoring-t006).
Always prepare in a new candidate directory; never overwrite public files or
silently replace pinned fingerprints. Reconcile changed inputs and obtain renewed
human field/value approval before regenerating data.

The public browser application, catalog generator, release generator, and tests
remain self-contained in `../microsite/`. Private source reproduction must compare
all candidate JSON/CSV bytes and embedded definitions to those public artifacts.
Final directory and actual-host approval remain separate gates.
