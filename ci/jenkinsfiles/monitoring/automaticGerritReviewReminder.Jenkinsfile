pipeline {
    agent {
        node {
            label 'GridEngine'
        }
    }

    options {
        timestamps()
        timeout(time: 5, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
    }

    stages {
        stage('Fetch Gerrit Reviews') {
            steps {
                script {
                    sh "python ci/scripts/monitoring/automaticGerritReviewReminder.py"
                }
            }
        }
        stage('Send Email') {
            steps {
                sendEmail()
            }
        }
    }
}

def sendEmail() {
    try {
        sh('cat email.properties')
        def props = sh(script:'cat email.properties', returnStdout:true).trim()

        mail to: "${env.DISTRIBUTION_LIST}",
        from: "jenkins-ossadmin-no-reply@ericsson.com",
        subject: "The Hummingbirds - Open Code Reviews",
        body: "${props}" + "<br><br><b>Note:</b> This mail has been sent automatically as part of the Jenkins job <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
        mimeType: 'text/html'
    }
    catch(Exception e) {
        echo "Email notification was not sent."
        print e
    }
}