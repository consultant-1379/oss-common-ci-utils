#!/usr/bin/env groovy

def defaultBobImage = 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob.2.0:1.7.0-55'
def bob = new BobCommand()
    .bobImage(defaultBobImage)
    .envVars([
        HOME:'${HOME}',
        RELEASE:'${RELEASE}',
        GERRIT_REFSPEC:'${GERRIT_REFSPEC}',
        SELI_ARTIFACTORY_REPO_USER:'${CREDENTIALS_SELI_ARTIFACTORY_USR}',
        SELI_ARTIFACTORY_REPO_PASS:'${CREDENTIALS_SELI_ARTIFACTORY_PSW}',
        MAVEN_CLI_OPTS: '${MAVEN_CLI_OPTS}',
        BRANCH: '${BRANCH}'
    ])
    .needDockerSocket(true)
    .toString()

pipeline {
    agent {
        node {
            label NODE_LABEL
        }
    }

    options {
        timestamps()
        timeout(time: 5, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '100', artifactNumToKeepStr: '100'))
    }

    environment {
        CREDENTIALS_SELI_ARTIFACTORY = credentials("SELI_ARTIFACTORY")
        RULESET_LOCATION = "ci/rulesets/monitoring/common-oss-artifactory-ruleset.yaml"
        JENKINSFILE_LOCATION = "ci/jenkinsfiles/monitoring/artifactoryRepoUsage.Jenkinsfile"
        EMAIL_LOCATION = "ci/html/monitoring/artifactory-repo-usage-report-email.html"
    }

    stages {
        stage('Clean') {
            steps {
                archiveArtifacts allowEmptyArchive: true, artifacts: "${env.RULESET_LOCATION}, ${env.JENKINSFILE_LOCATION}"
                sh "${bob} clean -r ${env.RULESET_LOCATION}"
            }
        }

        stage('Init') {
            steps {
                sh "${bob} init:setup-temp-dirs -r ${env.RULESET_LOCATION}"
            }
        }

        stage('Generate') {
            steps {
                sh "${bob} artifactory-usage-report -r ${env.RULESET_LOCATION}"
            }
            post {
                success {
                    archiveArtifacts artifacts: '.tmp/.usage-report/artifactory-repo-usage-report.json'
                    archiveArtifacts allowEmptyArchive: true, artifacts: ".tmp/.usage-report/*.htm"
                    publishHTML (target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: false,
                        keepAll: true,
                        reportDir: ".tmp/.usage-report/",
                        reportFiles: 'final_usage.htm',
                        reportName: 'Artifactory Latest Repo Usage'
                    ])
                }
            }
        }

        stage('Publish') {
            when {
                expression { env.PUBLISH == "true" }
            }
            steps {
                sh "${bob} artifactory-usage-report-publish -r ${env.RULESET_LOCATION}"
            }
        }

        stage('Email') {
            when {
                expression { env.EMAIL == "true" }
            }
            steps {
                script {
                    sendEmail()
                }
            }
        }
    }
}

def sendEmail() {
    echo "Sending an email to distribution list: ${env.DISTRIBUTION_LIST}, and CC to: ${env.DISTRIBUTION_LIST_CC}"
    try {
        def emailHtmlFile = readFile(file: EMAIL_LOCATION)
        mail to: "${env.DISTRIBUTION_LIST}",
                from: "jenkins-ossadmin-no-reply@ericsson.com",
                cc: "${env.DISTRIBUTION_LIST_CC}",
                subject: "[${env.JOB_NAME}] Usage Report Available for Analysis",
                body: emailHtmlFile,
                mimeType: 'text/html'
    } catch(Exception e) {
        echo "Email notification was not sent."
        print e
    }
}

// More about @Builder: http://mrhaki.blogspot.com/2014/05/groovy-goodness-use-builder-ast.html
import groovy.transform.builder.Builder
import groovy.transform.builder.SimpleStrategy

@Builder(builderStrategy = SimpleStrategy, prefix = '')
class BobCommand {
    def bobImage = 'bob.2.0:latest'
    def envVars = [:]
    def needDockerSocket = false

    String toString() {
        def env = envVars
                .collect({ entry -> "-e ${entry.key}=\"${entry.value}\"" })
                .join(' ')

        def cmd = """\
            |docker run
            |--init
            |--rm
            |--workdir \${PWD}
            |--user \$(id -u):\$(id -g)
            |-v \${PWD}:\${PWD}
            |-v /etc/group:/etc/group:ro
            |-v /etc/passwd:/etc/passwd:ro
            |-v \${HOME}:\${HOME}
            |${needDockerSocket ? '-v /var/run/docker.sock:/var/run/docker.sock' : ''}
            |${env}
            |\$(for group in \$(id -G); do printf ' --group-add %s' "\$group"; done)
            |--group-add \$(stat -c '%g' /var/run/docker.sock)
            |${bobImage}
            |"""
        return cmd
                .stripMargin()           // remove indentation
                .replace('\n', ' ')      // join lines
                .replaceAll(/[ ]+/, ' ') // replace multiple spaces by one
    }
}