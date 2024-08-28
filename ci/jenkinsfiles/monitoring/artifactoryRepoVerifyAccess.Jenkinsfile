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
        JENKINSFILE_LOCATION = "ci/jenkinsfiles/monitoring/artifactoryRepoVerifyAccess.Jenkinsfile"
        EMAIL_LOCATION = "ci/html/monitoring/artifactory-verify-access-email.html"
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
                sh "${bob} init -r ${env.RULESET_LOCATION}"
            }
        }

        stage('Publishing Artifacts') {
            when {
                expression { env.VERIFY_PUBLISHING == "true" }
            }
            stages {
                stage('Docker Registry Publish') {
                    steps {
                        sh "${bob} image-publish -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Helm Repository Publish') {
                    steps {
                        sh "${bob} helm-publish -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Maven Repository Publish') {
                    steps {
                        sh "${bob} maven-publish -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Generic Repository Publish') {
                    steps {
                        sh "${bob} generic-publish -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Thirdparty Repository Publish'){
                    steps {
                        sh "${bob} thirdparty-publish -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('NPM Repository Publish'){
                    steps {
                        sh "${bob} npm-publish -r ${env.RULESET_LOCATION}"
                    }
                }
            }
        }

        stage('Pulling Artifacts') {
            when {
                expression { env.VERIFY_PULLING == "true" }
            }
            stages {
                stage('Docker Registry Pull') {
                    steps {
                        sh "${bob} image-pull -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Helm Repository Pull') {
                    steps {
                        sh "${bob} helm-pull -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Maven Repository Pull') {
                    steps {
                        sh "${bob} maven-pull -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Generic Repository Pull') {
                    steps {
                        sh "${bob} generic-pull -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('Thirdparty Repository Pull'){
                    steps {
                        sh "${bob} thirdparty-pull -r ${env.RULESET_LOCATION}"
                    }
                }
                stage('NPM Repository Pull'){
                    steps {
                        sh "${bob} npm-pull -r ${env.RULESET_LOCATION}"
                    }
                }
            }
        }
    }
    post {
        unsuccessful {
            script {
                sendEmail()
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
            subject: "[${env.JOB_NAME}] job has been unsuccessful!",
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