# Template — sfdx Project Manifest (sfdx-project.json + package.xml for 2GP)

Source-tracked project layout for a second-generation package. See `knowledge/packaging-and-deployment.md` and `skills/salesforce-release-pipeline`.

## `sfdx-project.json`

```json
{
  "packageDirectories": [
    {
      "path": "force-app",
      "default": true,
      "package": "MyApp",
      "versionName": "ver 0.1",
      "versionNumber": "0.1.0.NEXT",
      "dependencies": []
    }
  ],
  "namespace": "",
  "sfdcLoginUrl": "https://login.salesforce.com",
  "sourceApiVersion": "63.0"
}
```

> `sourceApiVersion` `[verify-at-build]` against the current release. `dependencies` lists upstream package versions so installs happen in order.

## `package.xml` (deploy manifest — order by dependency)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
  <!-- Objects/fields first -->
  <types>
    <members>*</members>
    <name>CustomObject</name>
  </types>
  <!-- Permission sets after objects -->
  <types>
    <members>*</members>
    <name>PermissionSet</name>
  </types>
  <!-- Code/Flows after referenced types -->
  <types>
    <members>*</members>
    <name>ApexClass</name>
  </types>
  <types>
    <members>*</members>
    <name>ApexTrigger</name>
  </types>
  <types>
    <members>*</members>
    <name>Flow</name>
  </types>
  <version>63.0</version>
</Package>
```

## Create the package version

```bash
sf package version create --package MyApp --installation-key-bypass --wait 20 --code-coverage
```

Notes: unlocked package for internal modular dev, managed for ISV; validate (check-only) before a real deploy; never click-deploy to prod.
