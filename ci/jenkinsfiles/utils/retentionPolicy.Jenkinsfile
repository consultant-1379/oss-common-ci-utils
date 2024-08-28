#!/usr/bin/env groovy
def defaultBobImage = 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob.2.0:1.7.0-55'
def bob = new BobCommand()
    .bobImage(defaultBobImage)
    .envVars([
        HOME:'${HOME}',
        SELI_ARTIFACTORY_REPO_USER:'${CREDENTIALS_SELI_ARTIFACTORY_USR}',
        SELI_ARTIFACTORY_REPO_PASS:'${CREDENTIALS_SELI_ARTIFACTORY_PSW}',
        SERO_ARTIFACTORY_REPO_USER:'${CREDENTIALS_SERO_ARTIFACTORY_USR}',
        SERO_ARTIFACTORY_REPO_PASS:'${CREDENTIALS_SERO_ARTIFACTORY_PSW}',
        ARTIFACT_DAYS_OLD: '${ARTIFACT_DAYS_OLD}',
        HELM_ARTIFACT_DAYS_OLD: '${HELM_ARTIFACT_DAYS_OLD}'
    ])
    .needDockerSocket(true)
    .toString()

pipeline {
    agent {
        node {
            label NODE_LABEL
        }
    }

    environment {
        CREDENTIALS_SELI_ARTIFACTORY = credentials('SELI_ARTIFACTORY')
        CREDENTIALS_SERO_ARTIFACTORY = credentials('SERO_ARTIFACTORY')
        RULESET_LOCATION = "ci/rulesets/utils/retentionPolicyRuleset.yaml"
    }

    stages {
        stage('Search Proj-Eric-Oss-Dev ARM artifacts') {
            steps {
                sh "${bob} search-dev -r ${env.RULESET_LOCATION}"
                archiveArtifacts allowEmptyArchive: true, artifacts: 'spec.json'
            }
        }
        stage('Delete Proj-Eric-Oss-Dev ARM artifacts') {
            when {
                environment name: 'DELETE-DEV', value: 'true'
            }
            steps {
                sh "${bob} delete -r ${env.RULESET_LOCATION}"
            }
        }
        stage('Search Proj-Eric-Oss-Ci-Internal ARM artifacts') {
            steps {
                sh "${bob} search-ci-internal -r ${env.RULESET_LOCATION}"
                archiveArtifacts allowEmptyArchive: true, artifacts: 'spec.json'
            }
        }
        stage('Delete Proj-Eric-Oss-Ci-Internal ARM artifacts') {
            when {
                environment name: 'DELETE-CI-INTERNAL', value: 'true'
            }
            steps {
                sh "${bob} delete -r ${env.RULESET_LOCATION}"
            }
        }
        stage('Search Proj-Eric-Oss-Ci-Internal-Helm ARM artifacts') {
            steps {
                sh "${bob} search-ci-internal-helm -r ${env.RULESET_LOCATION}"
                archiveArtifacts allowEmptyArchive: true, artifacts: 'spec.json'
            }
        }
        stage('Delete Proj-Eric-Oss-Ci-Internal-Helm ARM artifacts') {
            when {
                environment name: 'DELETE-HELM-CI-INTERNAL', value: 'true'
            }
            steps {
                sh "${bob} delete -r ${env.RULESET_LOCATION}"
            }
        }
        stage('Search PCR build artifacts') {
            steps {
                sh "${bob} search-ci-internal-build-artifacts -r ${env.RULESET_LOCATION}"
                archiveArtifacts allowEmptyArchive: true, artifacts: 'spec.json'
            }
        }

        stage('Delete PCR build artifacts') {
            steps {
                sh "${bob} delete -r ${env.RULESET_LOCATION}"
            }
        }
        stage('Search Publish build artifacts') {
            steps {
                sh "${bob} search-oss-drop-build-artifacts -r ${env.RULESET_LOCATION}"
                archiveArtifacts allowEmptyArchive: true, artifacts: 'spec.json'
            }
        }

        stage('Delete Publish build artifacts') {
            steps {
                sh "${bob} delete -r ${env.RULESET_LOCATION}"
            }
        }
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
