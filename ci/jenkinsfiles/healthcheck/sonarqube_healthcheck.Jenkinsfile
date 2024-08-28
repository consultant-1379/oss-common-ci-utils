#!/usr/bin/env groovy

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 05, unit: "MINUTES")
        buildDiscarder(logRotator(numToKeepStr: "15", artifactNumToKeepStr: "15"))
    }

    stages {
        stage("SonarQube") {
            steps {
                echo "Triggering https://fem3s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/SonarQube_Child_Job/"
                build job: 'SonarQube_Child_Job'
            }
        }
    }
    post {
        unsuccessful {
            echo "Sending email to ${env.EMAIL}"
            sendEmail()
        }
    }
}

def sendEmail() {
    try {
        mail to: "${env.EMAIL}",
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