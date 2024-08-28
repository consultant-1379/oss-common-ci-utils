#!/usr/bin / env groovy

def ruleset = "ci/rulesets/utils/helm_cleanup_ruleset.yaml"
def bob = "python3 bob/bob.py -r ${ruleset}"

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 15, unit: "MINUTES")
        buildDiscarder(logRotator(numToKeepStr: "15", artifactNumToKeepStr: "15"))
    }

    environment {
        KUBECONFIG = "${WORKSPACE}/.kube/config"
        K8S_CLUSTER_ID = "hahn186"
    }

    stages {
        stage("Prepare") {
            steps {
                configFileProvider([configFile(fileId: "${env.K8S_CLUSTER_ID}", targetLocation: "${env.KUBECONFIG}")]) {}
                sh "git submodule add ../../../adp-cicd/bob"
                sh "${bob} helm-prepare"
            }
        }

        stage("Helm cleanup") {
            steps {
                sh "${bob} helm-cleanup"
            }
        }

        stage("Helm update") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {
                        sh "${bob} helm-update"
                    }
                }
            }
        }
    }
    post {
        always {
            sh "${bob} helm-post-actions"
        }
        success {
            archiveArtifacts allowEmptyArchive: true, artifacts: 'build/**/*.*'
        }
        unsuccessful {
            sendEmail()
        }
    }
}

def sendEmail() {
    try {
        mail to: "${env.EMAIL}",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action required! Failure in ${env.JOB_NAME}",
            body: "The build <a href='${env.BUILD_URL}'>#${env.BUILD_NUMBER}</a> of ${env.JOB_NAME} has failed!<br>" +
            "Please have a look into this and take appropriate action!<br>" +
            "<br><b>Note</b>: This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: "text/html"
    } catch (Exception e) {
        echo "Email notification was not sent!"
        print e
    }
}