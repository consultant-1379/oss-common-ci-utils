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
        key_management_tag = "${env.VERSION}"
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

        stage('Generate CR for KeyManagement') {
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
                                if (yamlContent.contains('eric-oss-key-management-agent')) {
                                    def lines = yamlContent.readLines()
                                    // Flag to identify if 'tag' should be updated
                                    def updateTag = false
                                    // Iterate over each line
                                    lines.eachWithIndex { line, index ->
                                        // Check if the line contains the 2pp image
                                        if (line.contains('eric-oss-key-management-agent')) {
                                            // Set the flag to update 'tag' after finding 2pp
                                            updateTag = true
                                        }
                                        // Update 'tag' value if the flag is set and the line contains 'tag'
                                        if (updateTag && line.contains('tag:')) {
                                            // Replace the 'tag' variable value
                                            def keyTag = env.key_management_tag.replaceAll("\\n|\\r", "")
                                            lines[index] = line.replaceAll(/tag: .*/, "tag: \"${keyTag}\"")
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
                                        git commit -m "NO-JIRA: Automatic 2pp version uplift for key-management to ''' + key_management_tag + '''"
                                        git push origin HEAD:refs/for/master
                                    '''
                                } else {
                                    echo "Variable 'eric-oss-key-management-agent' not found in YAML file '${yamlFile.path}'. Skipping Gerrit patch creation."
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
            mail to: "${env.EMAIL}",
            from: "jenkins-ossadmin-no-reply@ericsson.com", //CR generation notification
            subject: "2pp version uplift for key-management to ${env.key_management_tag} for the '${artifactID}'",
            body: "Hi Team,<br><br>" +
                "Code review has been created for automated Keymanagement version uplift to the latest version :  ${env.key_management_tag}." +
                "<br><br>Please review the below commit <br>" +
                "https://gerrit-gamma.gic.ericsson.se/#/q/project:${env.REPO}<br><br>" +
                "<br>This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>" +
                "<br>Information about the 2pp uplifts at https://eteamspace.internal.ericsson.com/x/a5PFfw  " +
                "<br>BR, The Hummingbirds" +
                "<br>PDLAEONICC@pdl.internal.ericsson.com<br>",
            mimeType: 'text/html'
        }
        failure {
            mail to: "b32734be.ericsson.onmicrosoft.com@emea.teams.ms", //sending failure notification to HB
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            subject: "Key Management version uplift- failed for the '${artifactID}'",
            body: "Hi Team,<br><br>" +
                "The automatic 2pp version uplift for 'Key-management' has failed for the repository" +
                "<br>'Key-management' image not used in eric-product-info.yaml for the repository ${env.REPO}." +
                "<br>This email has been created automatically by Admin_2pp_update_key_management Jenkins job" +
                "<br>BR, The Hummingbirds" +
                "<br>PDLAEONICC@pdl.internal.ericsson.com<br>",
            mimeType: 'text/html'
        }
    }
}