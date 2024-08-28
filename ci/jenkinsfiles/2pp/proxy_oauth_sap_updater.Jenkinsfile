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
        proxy_oauth_sap_tag = "${env.VERSION}"
    }

    stages {
        stage('Prepare') {
            steps {
                deleteDir()
                script {
                    ci_pipeline_init.clone_repos() // Clones 2pp projects-function
                    artifactID = env.REPO.tokenize('/').last()
                    currentBuild.displayName = currentBuild.displayName + " / ${artifactID} "
                }
            }
        }
        stage('Generate CR for Proxy Oauth SAP') {
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
                                if (yamlContent.contains('eric-sec-authorization-proxy-oauth2-sap')) {
                                    def lines = yamlContent.readLines()
                                    // Flag to identify if 'tag' should be updated
                                    def updateTag = false
                                    // Iterate over each line
                                    lines.eachWithIndex { line, index ->
                                        // Check if the line contains 'eric-sec-authorization-proxy-oauth2-sap'
                                        if (line.contains('eric-sec-authorization-proxy-oauth2-sap')) {
                                            // Set the flag to update 'tag' after finding 'proxy oauth sap variable'
                                            updateTag = true
                                        }
                                        // Update 'tag' value if the flag is set and the line contains 'tag'
                                        if (updateTag && line.contains('tag:')) {
                                            // Replace the 'tag' variable value
                                            def sapTag = env.proxy_oauth_sap_tag.replaceAll("\\n|\\r", "")
                                            lines[index] = line.replaceAll(/tag: .*/, "tag: \"${sapTag}\"")
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
                                        git commit -m "NO-JIRA: Automatic 2pp version uplift for proxy-auth-sap to ''' + proxy_oauth_sap_tag + '''"
                                        git push origin HEAD:refs/for/master
                                   '''
                                } else {
                                    echo "Variable 'eric-sec-authorization-proxy-oauth2-sap' not found in YAML file '${yamlFile.path}'. Skipping Gerrit patch creation."
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
            mail to: "${env.EMAIL}", //CR generation notifcation to teams
                 from: "jenkins-ossadmin-no-reply@ericsson.com",
                 subject: "2pp uplift for proxy-auth to ${env.proxy_oauth_sap_tag} for the '${artifactID}'",
                 body: "Hi Team,<br><br>" +
                       "Code review has been created for automated prox-auth-sap uplift to the latest version :  ${env.proxy_oauth_sap_tag}." +
                       "<br><br>Please review the below commit<br>" +
                       "https://gerrit-gamma.gic.ericsson.se/#/q/project:${env.REPO}<br><br>" +
                       "<brThis mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>" +
                       "<br>Information about the 2pp uplifts at https://eteamspace.internal.ericsson.com/x/a5PFfw  " +
                       "<br>BR, The Hummingbirds" +
                       "<br>PDLAEONICC@pdl.internal.ericsson.com<br>",
            mimeType: 'text/html'
        }
        failure {
            mail to: "b32734be.ericsson.onmicrosoft.com@emea.teams.ms", //sending failure notification to HB
                from: "jenkins-ossadmin-no-reply@ericsson.com",
                subject: "2pp version uplift failed for the proxy-auth-sap for '${artifactID}'",
                body: "Hi Team,<br><br>" +
                       "The automatic 2pp version uplift for 'proxy-oauth-sap' has failed for the repository" +
                       "<br>'Proxy-oauth-sap' image not used in eric-product-info.yaml for the repository ${env.REPO}." +
                       "<br>This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>" +
                       "<br>BR, The Hummingbirds" +
                       "<br>PDLAEONICC@pdl.internal.ericsson.com<br>",
            mimeType: 'text/html'
        }
    }
}
