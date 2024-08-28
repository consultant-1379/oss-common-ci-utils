#!/usr/bin / env groovy

pipeline {
    agent {
        label env.NODE_LABEL
    }

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '15'))
    }

    environment {
        OUTPUT_DIRECTORY = "Reports"
        CSV_REPORT = "${WORKSPACE}/${env.OUTPUT_DIRECTORY}/File_name.csv"
        EMAIL_REPORT = "${WORKSPACE}/${env.OUTPUT_DIRECTORY}/Email_Content.html"
        SETTINGS_FILES = "${WORKSPACE}/${env.OUTPUT_DIRECTORY}/Settings_file.txt"
        CONSOLIDATED_CSV = "${WORKSPACE}/${env.OUTPUT_DIRECTORY}/_Consolidated_Jenkins_Jobs_List.csv"
        CONSOLIDATED_HTML = "${WORKSPACE}/${env.OUTPUT_DIRECTORY}/_Consolidated_Jenkins_Jobs_List.html"
    }

    stages {

        stage('Prepare') {
            steps {
                script {
                    sh "rm -rf ${env.OUTPUT_DIRECTORY} && mkdir -p ${env.OUTPUT_DIRECTORY}"
                    authorName = sh(returnStdout: true, script: 'git show -s --pretty=%an')
                    currentBuild.displayName = currentBuild.displayName + ' / ' + authorName
                }
            }
        }

        stage('Compile') {
            steps {
                script {
                    compileJekinsJobsList()
                }
            }
        }

        stage('Email') {
            steps {
                script {
                    sendEmail()
                }
            }
        }

    }
    post {
        success {
            archiveArtifacts allowEmptyArchive: true, artifacts: "${env.OUTPUT_DIRECTORY}/*"
            publishHTML(target: [
                allowMissing: false,
                alwaysLinkToLastBuild: false,
                keepAll: true,
                reportDir: "${env.OUTPUT_DIRECTORY}/",
                reportFiles: "_Consolidated_Jenkins_Jobs_List.html",
                reportName: "Consolidated_Jenkins_Jobs_List"
            ])
        }
        unsuccessful {
            sendErrorEmail()
        }
        always {
            script {
                sh "rm ${env.EMAIL_REPORT}"
                sh "rm ${env.SETTINGS_FILES}"
            }
        }
    }
}

import hudson.model.*;
import jenkins.model.Jenkins;
import org.jenkinsci.plugins.workflow.job.WorkflowJob;

def compileJekinsJobsList() {

    // Job Identifiers
    def descr_admin = "Admin Project"
    def descr_blank = "Other request"
    def descr_chassis = "Microservice Chassis Project"
    def descr_cpp = "C++ microservice project"
    def descr_go = "Golang microservice project"
    def descr_java = "Java microservice project"
    def descr_javascript = "JavaScript microservice project"
    def descr_python = "Python microservice project"
    def descr_refapp = "Microservice Ref App Project"
    def descr_sdk = "SDK project"
    def descr_test = "Test Project"
    def descr_unknown = "Unknown Project"
    def descr_user_utils = "User Utility Project"

    // Job Count
    int count_admin = 0
    int count_blank = 0
    int count_chassis = 0
    int count_cpp = 0
    int count_go = 0
    int count_java = 0
    int count_javascript = 0
    int count_python = 0
    int count_refapp = 0
    int count_sdk = 0
    int count_test = 0
    int count_unknown = 0
    int count_user_utils = 0
    int count_disabled = 0
    int count_custom_node_label = 0

    // Job Data
    def data_admin = []
    def data_blank = []
    def data_chassis = []
    def data_cpp = []
    def data_go = []
    def data_java = []
    def data_javascript = []
    def data_python = []
    def data_refapp = []
    def data_sdk = []
    def data_test = []
    def data_unknown = []
    def data_user_utils = []
    def data_consolidated = []
    def data_settings_file = []
    def temp_settings_file = []

    def jenkins_url = "https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"
    def csv_header = "S.No,Job Name,Category,Hybrid,Node Label,Settings File,Gerrit Project,Status,Max # Builds,Job Url"
    def consolidated_csv_header = "Description,Job Name,Category,Hybrid,Node Label,Settings File,Gerrit Project,Status,Max # Builds,Job Url"
    def settings_file_header = "Settings File Name,Count"

    // CSV Initialization
    data_admin.add("${csv_header}")
    data_blank.add("${csv_header}")
    data_chassis.add("${csv_header}")
    data_cpp.add("${csv_header}")
    data_go.add("${csv_header}")
    data_java.add("${csv_header}")
    data_javascript.add("${csv_header}")
    data_python.add("${csv_header}")
    data_refapp.add("${csv_header}")
    data_sdk.add("${csv_header}")
    data_test.add("${csv_header}")
    data_unknown.add("${csv_header}")
    data_user_utils.add("${csv_header}")
    data_settings_file.add("${settings_file_header}")

    // Categorize Jobs
    for (item in Hudson.instance.items) {

        // CSV parameters
        def job_name = ""
        def job_description = ""
        def job_category = ""
        def job_type = ""
        def job_node_label = ""
        def job_settings_file = ""
        def job_gerrit_project = ""
        def job_status = ""
        def job_url = ""
        def job_builds_to_keep = 0

        // Job name and url
        job_name = item.name
        job_description = item.description
        if (!job_description) {
            job_description = "No Description"
        }
        job_url = jenkins_url + job_name

        // Category
        if (job_name.contains('PreCodeReview')) {
            job_category = "PCR"
        } else if (job_name.contains('Publish')) {
            job_category = "Publish"
        }

        // Type
        if (job_name.contains('Hybrid')) {
            job_type = "Yes"
        } else {
            job_type = "No"
        }

        // Node label and Settings file
        def prop = item.getProperty(ParametersDefinitionProperty.class)
        if (prop) {
            for (param in prop.getParameterDefinitions()) {
                if (param.name == "NODE_LABEL") {
                    job_node_label = "${param.defaultValue}"
                    if (job_node_label != "GridEngine" && job_node_label != "GridEngine_PCR" && job_node_label != "GridEngine_CPP") {
                        count_custom_node_label++
                    }
                }
                if (param.name == "SETTINGS_CONFIG_FILE_NAME") {
                    job_settings_file = "${param.defaultValue}"
                    temp_settings_file.add("\n${job_settings_file}")
                }
            }
        }

        // Status
        def status = Jenkins.instance.getItem(job_name).isBuildable();
        if (status) {
            job_status = "Enabled"
        } else {
            job_status = "Disabled"
            count_disabled++
        }

        // Gerrit project
        if (item instanceof WorkflowJob) {
            def triggers = item.getTriggers()
            triggers.each {
                key,
                value ->
                if (value instanceof com.sonyericsson.hudson.plugins.gerrit.trigger.hudsontrigger.GerritTrigger) {
                    job_gerrit_project = value.getGerritProjects()[0].getPattern()
                } else if (value instanceof hudson.triggers.TimerTrigger) {
                    job_gerrit_project = "Timer Trigger - " + value.getSpec()
                }
            }
        }

        // Max. # of builds to keep
        def build_prop = item.getProperty(BuildDiscarderProperty.class)
        if (build_prop) {
            def strategy = build_prop.getStrategy()
            if (strategy) {
                job_builds_to_keep = strategy.numToKeep
            }
        }

        // Categorize Jenkins Jobs
        if (job_description) {
            if (job_description.contains(descr_admin)) {
                count_admin++
                data_admin.add("\n${count_admin},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_admin},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_blank)) {
                count_blank++
                data_blank.add("\n${count_blank},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_blank},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_chassis)) {
                count_chassis++
                data_chassis.add("\n${count_chassis},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_chassis},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_cpp)) {
                count_cpp++
                data_cpp.add("\n${count_cpp},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_cpp},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_go)) {
                count_go++
                data_go.add("\n${count_go},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_go},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_java)) {
                count_java++
                data_java.add("\n${count_java},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_java},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_javascript)) {
                count_javascript++
                data_javascript.add("\n${count_javascript},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_javascript},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_python)) {
                count_python++
                data_python.add("\n${count_python},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_python},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_refapp)) {
                count_refapp++
                data_refapp.add("\n${count_refapp},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_refapp},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_sdk)) {
                count_sdk++
                data_sdk.add("\n${count_sdk},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_sdk},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_test) || job_name.contains("IDUN")) {
                count_test++
                data_test.add("\n${count_test},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_test},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else if (job_description.contains(descr_user_utils)) {
                count_user_utils++
                data_user_utils.add("\n${count_user_utils},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_user_utils},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            } else {
                count_unknown++
                data_unknown.add("\n${count_unknown},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
                data_consolidated.add("\n${descr_unknown},${job_name},${job_category},${job_type},${job_node_label},${job_settings_file},${job_gerrit_project},${job_status},${job_builds_to_keep},${job_url}")
            }
        }
    }

    //Setting.xml Summary
    String[] data_settings_file_unique = temp_settings_file.unique(false)
    for (String file in data_settings_file_unique) {
        def count = 0
        for (String temp_file in temp_settings_file) {
            if (file == temp_file) {
                count++
            }
        }
        data_settings_file.add("${file},${count}")
    }

    // Fetch Settings files that are used in less than 5 jobs
    def row_count = 1
    for (String data in data_settings_file) {
        def file_name = ""
        def file_count = 0
        if (row_count > 1) { //To skip header
            file_name = data.split(',')[0].replace("\n", "")
            file_count = data.split(',')[1].toInteger()
            if (file_count < 5) {
                output_file = new File("${env.SETTINGS_FILES}")
                output_file.append(file_name + ",")
            }
        }
        row_count++
    }

    // Create CSV Report
    def file_name = ""
    def output_file = ""
    file_name = "${env.CSV_REPORT}".replace("File_name", descr_admin)
    output_file = new File(file_name)
    data_admin.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_blank)
    output_file = new File(file_name)
    data_blank.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_chassis)
    output_file = new File(file_name)
    data_chassis.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_cpp)
    output_file = new File(file_name)
    data_cpp.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_go)
    output_file = new File(file_name)
    data_go.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_java)
    output_file = new File(file_name)
    data_java.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_javascript)
    output_file = new File(file_name)
    data_javascript.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_python)
    output_file = new File(file_name)
    data_python.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_refapp)
    output_file = new File(file_name)
    data_refapp.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_sdk)
    output_file = new File(file_name)
    data_sdk.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_test)
    output_file = new File(file_name)
    data_test.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_unknown)
    output_file = new File(file_name)
    data_unknown.each {
        item -> output_file.append("${item}")
    }

    file_name = "${env.CSV_REPORT}".replace("File_name", descr_user_utils)
    output_file = new File(file_name)
    data_user_utils.each {
        item -> output_file.append("${item}")
    }

    // Consolidated CSV
    output_file = new File("${env.CONSOLIDATED_CSV}")
    data_consolidated.sort()
    output_file.append("${consolidated_csv_header}")
    data_consolidated.each {
        item -> output_file.append("${item}")
    }

    // Settings file data
    def descr_settings_file = "Settings File Summary"
    file_name = "${env.CSV_REPORT}".replace("File_name", descr_settings_file)
    output_file = new File(file_name)
    data_settings_file.each {
        item -> output_file.append("${item}")
    }

    // Create HTML Report
    def html_file = new File("${env.CONSOLIDATED_HTML}")
    def header = "<html><head><style> table, th, td { border: 1px solid rgb(255, 255, 255); border-collapse: collapse; font-size:14px;} th { background: #000; color: #eee; font-weight: bold; padding: 5px; text-align:left;} td { background: #aaa; font-weight: normal; overflow: hidden; padding: 5px; text-overflow: ellipsis; white-space: nowrap; } body { background: #e1e2e3; font-family: sans-serif; font-size:14px;} </style></head><body><b>Fem1s11 - Consolidated Jenkins Jobs Report</b>"
    def date = String.format('%tF %<tH:%<tM', java.time.LocalDateTime.now())
    html_file.append("${header}")
    html_file.append("<p><b>Report generated on</b>: ${date}</p><br>")

    // Project and Settings file Summary
    html_file.append("<p><b>Project Summary</b></p>")
    html_file.append("<table><tr><th>Project Type</th><th>Job Count</th></tr>")
    html_file.append("<tr><td>${descr_admin}</td><td>${count_admin}</td></tr>")
    html_file.append("<tr><td>${descr_chassis}</td><td>${count_chassis}</td></tr>")
    html_file.append("<tr><td>${descr_refapp}</td><td>${count_refapp}</td></tr>")
    html_file.append("<tr><td>${descr_java}</td><td>${count_java}</td></tr>")
    html_file.append("<tr><td>${descr_python}</td><td>${count_python}</td></tr>")
    html_file.append("<tr><td>${descr_cpp}</td><td>${count_cpp}</td></tr>")
    html_file.append("<tr><td>${descr_go}</td><td>${count_go}</td></tr>")
    html_file.append("<tr><td>${descr_sdk}</td><td>${count_sdk}</td></tr>")
    html_file.append("<tr><td>${descr_javascript}</td><td>${count_javascript}</td></tr>")
    html_file.append("<tr><td>${descr_blank}</td><td>${count_blank}</td></tr>")
    html_file.append("<tr><td>${descr_user_utils}</td><td>${count_user_utils}</td></tr>")
    def total_job_count = (count_admin + count_blank + count_chassis + count_cpp + count_go + count_java + count_javascript + count_python + count_refapp + count_sdk + count_test + count_unknown + count_user_utils)
    html_file.append("<tr><td><b>Total Projects</b></td><td><b>${total_job_count}</b></td></tr></table><br><br>")
    createHTMLTable(descr_settings_file)

    // Issues Detected
    html_file.append("<p><b>Issues Detected</b></p>")
    html_file.append("<table><tr><th>Project Type</th><th>Job Count</th></tr>")
    html_file.append("<tr><td>${descr_test}</td><td>${count_test}</td></tr>")
    html_file.append("<tr><td>${descr_unknown}</td><td>${count_unknown}</td></tr>")
    html_file.append("<tr><td>Disabled Jobs</td><td>${count_disabled}</td></tr>")
    html_file.append("<tr><td>Jobs with custom NODE_LABEL</td><td>${count_custom_node_label}</td></tr></table><br><br>")

    // Email content
    def email_content = new File("${env.EMAIL_REPORT}")
    def report_url = "https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/Admin_Utility_Fetch_Jenkins_Jobs_List/Consolidated_5fJenkins_5fJobs_5fList/"
    email_content.append("${header}")
    email_content.append("<br><p><b>Please find the details below.</b><ul><li>Report: <a href='${report_url}'>Consolidated Jenkins Jobs Report</a></li>")
    email_content.append("<li>Generated on: ${date}</li></ul></p><br>")
    email_content.append("<p><b>Issues Detected</b>:</p>")
    email_content.append("<table><tr><th>Project Type</th><th>Job Count</th></tr>")
    email_content.append("<tr><td>${descr_test}s</td><td>${count_test}</td></tr>")
    email_content.append("<tr><td>${descr_unknown}s</td><td>${count_unknown}</td></tr>")
    email_content.append("<tr><td>Disabled Jobs</td><td>${count_disabled}</td></tr>")
    email_content.append("<tr><td>Jobs with custom NODE_LABEL</td><td>${count_custom_node_label}</td></tr></table><br><br>")

    // Output data
    createHTMLTable(descr_admin)
    createHTMLTable(descr_chassis)
    createHTMLTable(descr_refapp)
    createHTMLTable(descr_java)
    createHTMLTable(descr_python)
    createHTMLTable(descr_cpp)
    createHTMLTable(descr_go)
    createHTMLTable(descr_sdk)
    createHTMLTable(descr_javascript)
    createHTMLTable(descr_blank)
    createHTMLTable(descr_test)
    createHTMLTable(descr_unknown)
    createHTMLTable(descr_user_utils)

}

// Create HTML Table from CSV
def createHTMLTable(String descr) {

    def htmlString = "<br><b>${descr}</b><br><br><table>"
    def tableHeader = "<th>header</th>"
    def tableData = "<td>data</td>"
    def tableDataRed = '<td style="color:red">data</td>'
    def tableDataLink = "<td><a href='data'>data</a></td>"
    def jenkins_url = "https://fem1s11-eiffel216.eiffel.gic.ericsson.se:8443/jenkins/job/"

    String[] settings_file = new File("${env.SETTINGS_FILES}").text.split(',')
    def output_file = new File("${env.CONSOLIDATED_HTML}")
    def input_file = "${env.CSV_REPORT}".replace("File_name", descr)
    String input_data = new File(input_file).text
    String[] lines = input_data.split('\n')
    int count = 1

    for (String line in lines) {
        // Table Header
        if (count == 1) {
            htmlString = htmlString + "<tr>"
            for (String data in line.split(",")) {
                temp = tableHeader.replace("header", data)
                htmlString = htmlString + temp
            }
            htmlString = htmlString + "</tr>"
        } else {
            // Table Data
            htmlString = htmlString + "<tr>"
            for (String data in line.split(",")) {
                if (data.contains(jenkins_url)) {
                    temp = tableDataLink.replace("data", data)
                } else {
                    if (data.contains("RHEL7_GE_Docker_") || data.contains("Disabled")) {
                        // Conditional Formatting
                        temp = tableDataRed.replace("data", data)
                    } else {
                        temp = tableData.replace("data", data)
                    }
                }
                htmlString = htmlString + temp
            }
            htmlString = htmlString + "</tr>"
        }
        count = count + 1
    }
    htmlString = htmlString + "</table><br><br><br>"
    // Conditional Formatting
    for(String tmp in settings_file) {
        def search_string = "<td>${tmp}"
        def replace_string = "<td style='color:red'>${tmp}"
        htmlString = htmlString.replace(search_string,replace_string)
    }
    output_file.append("${htmlString}")
}

// Send Warning Email
def sendEmail() {

    String email_text = new File("${env.EMAIL_REPORT}").text
    try {
        mail to: "${env.DISTRIBUTION_LIST}",
            from: "jenkins-ossadmin-no-reply@ericsson.com",
            cc: "",
            subject: "Action Required! Fem1s11 - Consolidated Jenkins Jobs Report",
            body: "${email_text}" +
            "<b>Please review the above report and perform the following actions</b>.<br><ul>" +
            "<li>Please copy the test jobs to fem3s11 and delete them from the production fem.</li>" +
            "<li>Should the situation arise, update the job description of your test job to 'Test Project' when you create one and please delete it after use.</li>" +
            "<li>Please add appropriate job descriptions to the unknown projects.</li>" +
            "<li>Please check if the disabled jobs are required and delete them from the fem.</li>" +
            "<li>Please configure the jobs with custom node labels to run on one of the default node labels.</li>" +
            "<li>Please make sure the job names of PCR and Publish jobs adhere to the pattern '_PreCodeReview' and '_Publish'.</li>" +
            "<li>Please verify that the hybrid pipelines follow the pattern '_Hybrid'.</li></ul>" +
            "<b>Note:</b> This mail has been sent automatically by <a href='${env.BUILD_URL}'>${env.JOB_NAME}</a>",
            mimeType: 'text/html'
    } catch (Exception e) {
        echo "Email notification was not sent."
        print e
    }
}

// Send Email when the job fails
def sendErrorEmail() {
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
        echo "Email notification was not sent."
        print e
    }
}