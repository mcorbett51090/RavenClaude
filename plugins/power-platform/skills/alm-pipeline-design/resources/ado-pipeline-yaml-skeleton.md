# Azure DevOps Multi-Stage YAML Skeleton — Power Platform

Working starting point for a multi-stage ADO pipeline that builds and promotes a Power Platform solution through DEV → BUILD → TEST → UAT → PROD. Adapt to your variable groups, agent pool, and target envs.

## Pre-requisites

- ADO project with **Power Platform Build Tools** extension installed.
- Service connection per target env (TEST, UAT, PROD), each backed by an SPN with App User added to the target Dataverse env with the **System Administrator** role (or a tightly scoped equivalent).
- Variable groups per env (`pp-test`, `pp-uat`, `pp-prod`) containing at minimum: `SolutionName`, `TargetEnvUrl`. Secrets resolve from Key Vault, not plaintext.
- `deploymentSettings-test.json`, `deploymentSettings-uat.json`, `deploymentSettings-prod.json` in the repo at `pipelines/settings/`.

## YAML skeleton

```yaml
name: $(Build.DefinitionName)_$(Date:yyyyMMdd)$(Rev:.r)

trigger:
  branches:
    include:
      - main
  paths:
    include:
      - solution/**

variables:
  - name: solutionName
    value: MyCustomerSolution
  - name: artifactName
    value: managed-solution

stages:
  # --------------------------------------------------------
  - stage: Lint
    displayName: Static check
    jobs:
      - job: PacCheck
        pool:
          vmImage: windows-latest
        steps:
          - task: PowerPlatformToolInstaller@2
          - task: PowerPlatformChecker@2
            inputs:
              authenticationType: PowerPlatformSPN
              PowerPlatformSPN: pp-build
              FilesToAnalyze: '$(Build.SourcesDirectory)\solution\**\*.zip'
              RuleSet: '0ad12346-e108-40b8-a956-9a8f95ea18c9' # Solution Checker
              ErrorLevel: HighIssueCount
              ErrorThreshold: 0

  # --------------------------------------------------------
  - stage: Build
    displayName: Pack + export managed
    dependsOn: Lint
    jobs:
      - job: PackImportExport
        pool:
          vmImage: windows-latest
        steps:
          - task: PowerPlatformToolInstaller@2

          - task: PowerPlatformPackSolution@2
            displayName: Pack unmanaged
            inputs:
              SolutionSourceFolder: '$(Build.SourcesDirectory)/solution/$(solutionName)'
              SolutionOutputFile: '$(Build.ArtifactStagingDirectory)/$(solutionName)_unmanaged.zip'
              SolutionType: Unmanaged

          - task: PowerPlatformImportSolution@2
            displayName: Import into BUILD env
            inputs:
              authenticationType: PowerPlatformSPN
              PowerPlatformSPN: pp-build
              SolutionInputFile: '$(Build.ArtifactStagingDirectory)/$(solutionName)_unmanaged.zip'
              AsyncOperation: true
              MaxAsyncWaitTime: 60

          - task: PowerPlatformPublishCustomizations@2
            inputs:
              authenticationType: PowerPlatformSPN
              PowerPlatformSPN: pp-build

          - task: PowerPlatformExportSolution@2
            displayName: Export managed
            inputs:
              authenticationType: PowerPlatformSPN
              PowerPlatformSPN: pp-build
              SolutionName: $(solutionName)
              SolutionOutputFile: '$(Build.ArtifactStagingDirectory)/$(solutionName)_managed.zip'
              Managed: true

          - publish: $(Build.ArtifactStagingDirectory)
            artifact: $(artifactName)

  # --------------------------------------------------------
  - stage: DeployTest
    displayName: Deploy to TEST
    dependsOn: Build
    variables:
      - group: pp-test
    jobs:
      - deployment: ImportTest
        environment: power-platform-test
        pool:
          vmImage: windows-latest
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerPlatformToolInstaller@2
                - task: PowerPlatformImportSolution@2
                  inputs:
                    authenticationType: PowerPlatformSPN
                    PowerPlatformSPN: pp-test
                    SolutionInputFile: '$(Pipeline.Workspace)/$(artifactName)/$(solutionName)_managed.zip'
                    UseDeploymentSettingsFile: true
                    DeploymentSettingsFile: '$(Build.SourcesDirectory)/pipelines/settings/deploymentSettings-test.json'
                    AsyncOperation: true
                    MaxAsyncWaitTime: 60
                    PublishWorkflows: true
                    OverwriteUnmanagedCustomizations: false

  # --------------------------------------------------------
  - stage: DeployUat
    displayName: Deploy to UAT
    dependsOn: DeployTest
    variables:
      - group: pp-uat
    jobs:
      - deployment: ImportUat
        environment: power-platform-uat
        pool:
          vmImage: windows-latest
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerPlatformToolInstaller@2
                - task: PowerPlatformImportSolution@2
                  inputs:
                    authenticationType: PowerPlatformSPN
                    PowerPlatformSPN: pp-uat
                    SolutionInputFile: '$(Pipeline.Workspace)/$(artifactName)/$(solutionName)_managed.zip'
                    UseDeploymentSettingsFile: true
                    DeploymentSettingsFile: '$(Build.SourcesDirectory)/pipelines/settings/deploymentSettings-uat.json'

  # --------------------------------------------------------
  - stage: DeployProd
    displayName: Deploy to PROD
    dependsOn: DeployUat
    variables:
      - group: pp-prod
    jobs:
      - deployment: ImportProd
        environment: power-platform-prod  # gated by approval in ADO Environments
        pool:
          vmImage: windows-latest
        strategy:
          runOnce:
            deploy:
              steps:
                - task: PowerPlatformToolInstaller@2
                - task: PowerPlatformImportSolution@2
                  inputs:
                    authenticationType: PowerPlatformSPN
                    PowerPlatformSPN: pp-prod
                    SolutionInputFile: '$(Pipeline.Workspace)/$(artifactName)/$(solutionName)_managed.zip'
                    UseDeploymentSettingsFile: true
                    DeploymentSettingsFile: '$(Build.SourcesDirectory)/pipelines/settings/deploymentSettings-prod.json'
                    HoldingSolution: false
                    OverwriteUnmanagedCustomizations: false
```

## Gotchas

- `OverwriteUnmanagedCustomizations: false` in TEST/UAT/PROD is intentional — if there are unmanaged customizations in those envs, you want the import to **fail loudly**, not silently overwrite them. If it fails there, somebody made an out-of-band change and that needs investigation, not papering over.
- `PublishWorkflows: true` activates flows on import. Without it, flows land in PROD as "off" and don't fire. Easy 2am incident.
- Approval gates live on the ADO `Environment` object (Pipelines → Environments → `power-platform-prod` → Approvals & checks), not in the YAML. Keep them there so PMs can edit approvers without touching pipeline code.
- The BUILD env is throwaway — never share it across solutions, never let humans customize in it. Treat it like CI.
