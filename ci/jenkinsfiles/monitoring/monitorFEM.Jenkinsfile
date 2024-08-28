#!/usr/bin/env groovy

def defaultBobImage = 'armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob.2.0:1.7.0-55'
def monitoring = ''
def message = ''
def unsuccessfulEmail = 'jenkins-fem-warning-email.html'

def bob = new BobCommand()
    .bobImage(defaultBobImage)
    .envVars([
        HOME:'${HOME}'
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
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '20'))
    }

    environment {
        RULESET_LOCATION = "ci/rulesets/monitoring/common-oss-artifactory-ruleset.yaml"
        KEEP_FOREVER_SCRIPT_PATH = "ci/scripts/monitoring/listCountKeepForever.py"
    }

    stages {
        stage('Prepare') {
            steps {
                sh "${bob} clean -r ${env.RULESET_LOCATION}"
		script{
		    monitoring = load "ci/scripts/monitoring/JenkinsMonitoring.groovy"
                    writeFile file: 'FEMUsageReport.txt', text: 'FEM Usage Report'

                }

            }
        }

        stage('FEM Information') {
            steps {
                script {
                    generateReport(monitoring.sessions())
                    generateReport(monitoring.systemLoadAverage())
                    generateReport(monitoring.startDate())
                }
            }
        }
        stage('Java Memory Usage') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.javaMemory())
                    }
                }
            }
        }
        stage('Metaspace Usage') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.metaSpaceSize())
                    }
                }
            }
        }

        stage('Physical Memory Usage') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.physicalMemorySize())
                    }
                }
            }
        }
        stage('Swap Space Usage') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.swapSpaceSize())
                    }
                }
            }
        }
        stage('CPU Usage') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.cpuUsage())
                    }
                }
            }
        }
        stage('Threads Test') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.threads())
                    }
                }
            }
        }
        stage('Execution and Queue Times Test') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.buildTimeAverage())
                        generateReport(monitoring.queueTimeAverage())
                        generateReport(monitoring.recommendedNumberOfExecutors())
                    }
                }
            }
        }

        stage('Job Info') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        generateReport(monitoring.disabledJobs())
                        generateReport(monitoring.enabledJobs())
                        generateReport(monitoring.allJobs())
                    }
                }
            }
        }

        stage('Keep Forever List & Count') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'GERRIT_PASSWORD', usernameVariable: 'GERRIT_USERNAME', passwordVariable: 'GERRIT_PASSWORD')]) {
                            sh "python ${env.KEEP_FOREVER_SCRIPT_PATH}"
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'FEMUsageReport.txt'
        }
        unsuccessful {
            echo 'Sending warning email to distribution list:'
            createEmail()
	    sendEmail(unsuccessfulEmail)
        }
    }
}
def createEmail(){
    sh '''#!/bin/bash

    report=FEMUsageReport.txt
    email=jenkins-fem-warning-email.html
    {
    echo "<html>"
    echo "<body>"
    echo "<div style='text-align:center; background-color:#0082f0; color:white;'><br>"
    echo "<h2>FEM1s11 performance issue(s) detected </h2><br>"
    echo "</div>"
    echo "<div style='text-align:center;'><br>"
    while read line; do
    if  echo "${line}" | grep -q "WARNING!"; then echo "<h3>${line}</h3>"; fi
    done < ${report}
    echo "<br>"
    echo "<p><i>This mail was sent automatically from Jenkins job <a href="${env.BUILD_URL}">${env.JOB_NAME}</a></i><br>"
    echo $(date '+%Y-%m-%d %H:%M:%S')
    echo "</div>"
    echo "</body>"
    echo "</html>"
    }  >> ${email}
    '''
}
def generateReport(monitoringFunction) {
    message = monitoringFunction
    sh "echo '$message' >> FEMUsageReport.txt"
    if(message.contains("WARNING!")==true){
        sh 'exit 1'
    }
}

def sendEmail(emailFile) {
    echo "Sending an email to distribution list: ${env.DISTRIBUTION_LIST}"
    try {
        def emailHtmlFile = readFile(file: emailFile)
        mail to: "${env.DISTRIBUTION_LIST}",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "${env.DISTRIBUTION_LIST_CC}",
            subject: "[${env.JOB_NAME}] FEM Usage Report Generated",
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
