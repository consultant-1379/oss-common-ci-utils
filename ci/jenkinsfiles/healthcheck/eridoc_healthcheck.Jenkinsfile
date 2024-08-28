#!/usr/bin/env groovy

def bob = 'python3 bob/bob.py'
def eriDocInstance = "https://eridoc.internal.ericsson.com/eridoc/"
pipeline {
    agent {
        node {
            label NODE_LABEL
        }
    }

    options {
        timestamps()
        timeout(time: 5, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment {
        SCRIPT = 'ci/scripts/healthchecks/eridoc_healthcheck.py'
        RULESET_LOCATION = "ci/rulesets/monitoring/healthcheck-ruleset.yaml"
        CREDENTIALS_ERIDOC = credentials('eridoc-user')
    }

    stages {
        stage('Prepare') {
            steps {
               sh 'git submodule add ../../../adp-cicd/bob'
            }
        }

        stage('EriDocPortal') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'eridoc-user', usernameVariable: 'ERIDOC_USERNAME', passwordVariable: 'ERIDOC_PASSWORD')]) {
                            sh "${bob} eridoc-upload:doc-to-pdf -r ${env.RULESET_LOCATION}"
                            def eridocuploadstatus = sh(returnStatus: true, script: "${bob} eridoc-upload:eridoc-upload-dryrun -r ${env.RULESET_LOCATION}")
                            if (eridocuploadstatus != 0) {
                                echo "Error: Command exited with status ${eridocuploadstatus}"
                                // def readContent = readFile 'healthcheck_file.txt'
                                // writeFile file: 'healthcheck_file.txt', text: readContent+"ERIDOC: " + eriDocInstance + " - Connection_Unsuccessful"
                                writeFile file: 'healthcheck_file.txt', text: "ERIDOC: " + eriDocInstance + " - Connection_UnSuccessful"
                            } else {
                                echo "Command executed successfully"
                                // def readContent = readFile 'healthcheck_file.txt'
                                // writeFile file: 'healthcheck_file.txt', text: readContent+"ERIDOC: " + eriDocInstance + " - Connection_Successful"
                                writeFile file: 'healthcheck_file.txt', text: "ERIDOC: " + eriDocInstance + " - Connection_Successful"
                            }
                        }
                    }
                }
            }
        }

        stage('Email') {
            steps {
                sh "python ${env.SCRIPT} Email"
            }
        }
    }
    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: "healthcheck_file.txt"
        }
        unsuccessful {
            sendEmail()
        }
    }
}

def sendEmail() {
    try {
        mail to: "${env.DISTRIBUTION_LIST}",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action Required! Failure in ${env.JOB_NAME}",
            body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
            "Please have a look into this and take appropriate action!<br>" +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: 'text/html'
    } catch (Exception e) {
        echo "Email notification was not sent!"
        print e
    }
}