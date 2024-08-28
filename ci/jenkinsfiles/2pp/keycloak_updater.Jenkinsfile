#!/usr/bin/env groovy
def bob = "./bob/bob -r ci/common_ruleset2.0.yaml"
def repos_list = []
def artifactID = ""
@Library('oss-common-pipeline-lib@dVersion-2.0.0-hybrid') _ // Shared library from the OSS/com.ericsson.oss.ci/oss-common-ci-utils

pipeline {
    agent {
        label env.NODE_LABEL
    }

    environment {
        keycloak_tag = "${env.VERSION}"
    }

    stages {
        stage('Prepare') {
            steps {
                deleteDir()
                script {
                    ci_pipeline_init.clone_repos()
                    artifactID = env.REPO.tokenize('/').last()
                    currentBuild.displayName = currentBuild.displayName + " / ${artifactID} "
                }
            }
        }
        stage('Generate CR for Keycloak') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                    script {
                        def yamlFiles = findFiles(glob: '**/eric-product-info.yaml')
                        if (yamlFiles) {
                            yamlFiles.each { yamlFile ->
                                echo "Found YAML file: ${yamlFile.path}"
                                // Read the content of the YAML file
                                def yamlContent = readFile(yamlFile.path)
                                // Splitting content by lines
                                if (yamlContent.contains('keycloak-client')) {
                                    def lines = yamlContent.readLines()
                                    // Flag to identify if 'tag' should be updated
                                    def updateTag = false
                                    // Iterate over each line
                                    lines.eachWithIndex { line, index ->
                                        // Check if the line contains 'keycloak-client'
                                        if (line.contains('keycloak-client')) {
                                            // Set the flag to update 'tag' after finding 2pp
                                            updateTag = true
                                        }
                                        // Update 'tag' value if the flag is set and the line contains 'tag'
                                        if (updateTag && line.contains('tag:')) {
                                            // Replace the 'tag' variable value
                                            def keycloakTag = env.keycloak_tag.replaceAll("\\n|\\r", "")
                                            lines[index] = line.replaceAll(/tag: .*/, "tag: \"${keycloakTag}\"")
                                            // Reset the flag as 'tag' has been updated
                                            updateTag = false
                                        }
                                    }
                                    // Join the lines back into a single string
                                    yamlContent = lines.join('\n').trim()
                                    echo "Updated YAML content:\n${yamlContent}"
                                    // Write the updated content back to the file
                                    writeFile file: yamlFile.path, text: yamlContent
                                    // CR generation
                                    sh '''
                                        pwd
                                        artifactID=${REPO##*/}  #fetch the artifact id from repo
                                        cd $artifactID
                                        git remote set-url --push origin ${GERRIT_CENTRAL}/${REPO}
                                        git add .
                                        git commit -m "NO-JIRA: Automatic 2pp version uplift for keycloak-client to ''' + keycloak_tag + '''"
                                        git push origin HEAD:refs/for/master
                                    '''
                                } else {
                                    echo "Variable 'keycloak-client' not found in YAML file '${yamlFile.path}'. Skipping Gerrit patch creation."
                                }
                            }
                        } else {
                            error "YAML file 'eric-product-info.yaml' not found."
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            mail to: "${env.EMAIL}",// sending CR link and notification to teams
                 from: "jenkins-ossadmin-no-reply@ericsson.com",
                 subject: "2pp version uplift for keycloak-client to ${env.keycloak_tag} for the '${artifactID}'",
                 body: "Hi Team,<br><br>" +
                       "Code review has been created for automated Keycloak client version uplift to the latest version :  ${env.keycloak_tag}." +
                       "<br><br>Please review the commit<br>" +
                       "https://gerrit-gamma.gic.ericsson.se/#/q/project:${env.REPO}<br><br>" +
                       "<br>This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>" +
                       "<br>Information about the 2pp uplifts at https://eteamspace.internal.ericsson.com/x/a5PFfw" +
                       "<br>BR, The Hummingbirds" +
                       "<br>PDLAEONICC@pdl.internal.ericsson.com<br>",
            mimeType: 'text/html'
        }
        failure {
            mail to: "b32734be.ericsson.onmicrosoft.com@emea.teams.ms", //sending failure notification to HB
                 from: "jenkins-ossadmin-no-reply@ericsson.com",
                 subject: "2pp version uplift for keycloak-client failed for the '${artifactID}'",
                 body: "Hi Team,<br><br>" +
                       "The automatic 2pp version uplift for 'keycloak-client' has failed for the repository ${env.REPO}." +
                       "<br>'Keycloak-client' image not used in eric-product-info.yaml for ${artifactID}" +
                       "<br>This email has been created automatically by Admin_2pp_update_keycloak Jenkins job" +
                       "<br>BR, The Hummingbirds" +
                       "<br>PDLAEONICC@pdl.internal.ericsson.com<br>",
            mimeType: 'text/html'
        }
    }
}