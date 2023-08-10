# CHANGELOG.md

## 0.3.4 (2023-08-09)

Fix types (missing from package?)

## 0.3.3 (2023-08-09)

QuiltPlus fixes, Part 3

- len(changes)
- volume.post()

## 0.3.2 (2023-08-03)

QuiltPlus fixes, Part 2

- pass/use explicit 'hash=' to namespace.get()
- support partial hashes

## 0.3.1 (2023-08-01)

QuiltPlus fixes, Part 1

- Namespace.pkg_name() returns the package name
- Load Manifests lazily
- Allow getting not-yet-existing Namespaces from a Registry

## 0.3.0 (2023-07-27)

- quiltspec
- push new packages

## 0.2.1 (2023-07-12)

- urlencode physical keys
- rename "child" methods to "_child"

## 0.2.0 (2023-07-06)

- rename schema to quilt3
- replace Blob with Entry
- include local registry example
- add Changes, Volume
- put Manifest into Volume

## 0.1.2 (2023-06-29)

- remove prefix from Core classes
- rename config to quiltcore.yaml

## 0.1.1 (2023-06-28)

- create and test Core classes
- update and use config.yaml
- implement get, put, and verify

## 0.1.0 (2023-06-16)

- create poetry project
- test arrow reading S3 registry
- stub config and registry
- pass tests
