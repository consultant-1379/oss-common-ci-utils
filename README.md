# OSS-COMMON_CI_UTILS REPOSITORY
In the oss-common-ci-utils repo's master branch, we store the monitoring, utility and JCasC scripts.
All of these files are stored to ensure retention and reusability.

# Where should I add my file?
When submitting files, please familiarise yourself with the agreed structure below and add them to the appropriate folder.
Please also ensure that the filename is meaningful and easy to understand.

# WARNING!!!
Please update the below directory structure when submitting a file!

```
oss-common-ci-utils (master)
|   .gitignore
|   README.md
|
+---ci
|   +---html
|   |   \---monitoring
|   |           artifactory-repo-usage-report-email.html
|   |           artifactory-verify-access-email.html
|   |
|   +---jenkinsfiles
|   |   +---monitoring
|   |   |       artifactoryRepoUsage.Jenkinsfile
|   |   |       artifactoryRepoVerifyAccess.Jenkinsfile
|   |   |       automaticGerritReviewReminder.Jenkinsfile
|   |   |       FunctionalUserAccessCheck.Jenkinsfile
|   |   |       FunctionalUserLdapIntegrityCheck.Jenkinsfile
|   |   |       monitorFEM.Jenkinsfile
|   |   |       monitorGE.Jenkinsfile
|   |   |
|   |   \---utils
|   |           fetchDesignRuleEnforcements.Jenkinsfile
|   |           jenkinsJobList.Jenkinsfile
|   |           retentionPolicy.Jenkinsfile
|   |           shellcheck.Jenkinsfile
|   |
|   +---rulesets
|   |   +---monitoring
|   |   |       common-oss-artifactory-ruleset.yaml
|   |   |
|   |   \---utils
|   |           retentionPolicyRuleset.yaml
|   |           ruleset2.0.yaml
|   |
|   \---scripts
|       +---monitoring
|       |       automaticGerritReviewReminder.py
|       |       consolidated.py
|       |       copyFile.sh
|       |       FunctionalUserAccessCheck.py
|       |       FunctionUserLdapIntegrityCheck.py
|       |       generateformattedcsv.py
|       |       generategraph.py
|       |       JenkinsMonitoring.groovy
|       |       monitoring_GE.py
|       |       munin_token_update.py
|       |
|       \---utils
|               fetchDesignRuleEnforcements.py
|
+---jenkins_config_as_code
|   |   JCasC.Jenkinsfile
|   |
|   +---configFiles
|   |       fem1s11_JCasC.yaml
|   |       fem2s11_JCasC.yaml
|   |       fem3s11_Admin_JCasC.yaml
|   |       fem4s11_JCasC.yaml
|   |       fem5s11_JCasC.yaml
|   |       fem6s11_JCasC.yaml
|   |       Template_JCasC_File.yaml
|   |
|   +---plugins
|   |       pluginFile
|   |       pluginFile_Ascending
|   |       pluginFile_Ascending.bak
|   |
|   \---scripts
|           generateConfigFile.sh
|           installPlugin.sh
|           jenkins-cli.jar
|           jobConfigBackup.sh
|           jobConfigRestore.sh
|           reload_JCaaC.sh
|           reload_JCaaC_ex.sh
|           restart.sh
|
\---scripts
    \---housekeeping_job_script
            DeleteProjectFromAgent.sh
            removeMavenLocalFile.sh
```