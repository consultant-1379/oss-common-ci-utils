#!/usr/bin/env groovy

def defaultBobImage = 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob.2.0:1.7.0-55'

def bob = new BobCommand()
    .bobImage(defaultBobImage)
    .envVars([
        HOME:'${HOME}',
        GERRIT_REFSPEC:'${GERRIT_REFSPEC}'
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
        buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
    }
    environment {
        RULESET_LOCATION = "ci/rulesets/utils/ruleset2.0.yaml"
        JENKINSFILE_LOCATION = "ci/jenkinsfiles/utils/shellcheck.Jenkinsfile"
    }

    stages {
        stage('Testing Scripts') {
            steps {
                archiveArtifacts allowEmptyArchive: true, artifacts: 'ci/rulesets/utils/ruleset2.0.yaml, ci/jenkinsfiles/utils/shellcheck.Jenkinsfile'
                echo "Starting..."
                echo "Shell scripts which will be tested:"
                sh "${bob} shell-test:echo-scripts -r ${env.RULESET_LOCATION}"
                echo "Testing shell scripts..."
                sh "${bob} shell-test:test-scripts -r ${env.RULESET_LOCATION}"
                echo "Finished!"
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
