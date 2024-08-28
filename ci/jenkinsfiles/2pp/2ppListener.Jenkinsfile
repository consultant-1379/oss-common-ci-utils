#!/usr/bin/env groovy

failed_repos_list = []
repos_map = [:]

new_tag_key_management=false
new_tag_api_gateway=false
new_tag_proxy_oauth=false
new_tag_proxy_oauth_sap=false
new_tag_jmx_exporter=false
new_tag_api_manager=false
new_tag_keycloak=false
new_tag_log_shipper_sidecar=false
new_tag_smart_helm_hooks=false

@Library('oss-common-pipeline-lib@dVersion-2.0.0-hybrid') _ // Shared library from the OSS/com.ericsson.oss.ci/oss-common-ci-utils

pipeline {
    agent { label env.NODE_LABEL }
    options { timestamps () }
    // environment for tracebility
    environment {
        img_tag_url="https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/monitoring/2pp"
        keymanagement_image_tag="keymanagement_latest_tag"
        proxy_oauth="proxy_oauth_latest_tag"
        proxy_oauth_sap="proxy_oauth_sap_latest_tag"
        jmx_exporter="jmx_exporter_latest_tag"
        api_gateway="api_gateway_latest_tag"
        api_manager="api_manager_latest_tag"
        keycloak="keycloak_client_latest_tag"
        log_shipper_sidecar_image_tag="log_shipper_sidecar_latest_tag"
        smart_helm_hooks_image_tag="smart_helm_hooks_latest_tag"
    }
    stages {
        stage('Prepare') {
            steps {
                deleteDir()
                script {
                    //Cloning dVersion-hybrid branch
                    sh '''
                        git clone ${GERRIT_MIRROR}/OSS/com.ericsson.oss.ci/oss-common-ci-utils
                        cd oss-common-ci-utils
                        git checkout dVersion-2.0.0-hybrid
                    '''
                }
            }
        }
        // Cloning repos and checking for 2pps
        stage('Get Repos and Determine Needed 2pps') {
            steps {
                script {
                    getRepos()
                }
            }
        }
        // Fetching latest image versions
        stage('Get Key_Management Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "key_mananagement_agent"
                            def repo = "proj-eric-oss-drop-docker-global"
                            def path_to_image = "proj-eric-oss-drop/eric-oss-key-management-agent/"

                            // Fetching Release tag
                            ( release_tag_key_management, release_tag_version_key_management ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.key_management_tag = release_tag_version_key_management

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_key_management_tag_present = compareReferenceTagWithReleaseTag(image_name, keymanagement_image_tag, release_tag_key_management)
                            new_tag_key_management = is_new_key_management_tag_present
                        }
                    }
                }
            }
        }
        stage('Get api-gateway Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "api_gateway_client"
                            def repo = "proj-eric-oss-drop-docker-global"
                            def path_to_image = "proj-eric-oss-drop/eric-api-gateway-client/"

                            // Fetching Release tag
                            ( release_tag_api_gateway_client, release_tag_version_api_gateway_client ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.api_gateway_tag = release_tag_version_api_gateway_client

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_api_gateway_tag_present = compareReferenceTagWithReleaseTag(image_name, api_gateway, release_tag_api_gateway_client)
                            new_tag_api_gateway = is_new_api_gateway_tag_present
                        }
                    }
                }
            }
        }
        stage('Get proxy-oauth Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "proxy_oauth"
                            def repo = "proj-common-assets-cd-released-docker-global"
                            def path_to_image = "proj-common-assets-cd-released/security/eric-sec-authorization-proxy-oauth2/"

                            // Fetching Release tag
                            ( release_tag_proxy_oauth, release_tag_version_proxy_oauth ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.proxy_oauth_tag = release_tag_version_proxy_oauth

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_proxy_oauth_present = compareReferenceTagWithReleaseTag(image_name, proxy_oauth, release_tag_proxy_oauth)
                            new_tag_proxy_oauth = is_new_proxy_oauth_present
                        }
                    }
                }
            }
        }
        stage('Get proxy-oauth2-sap Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "proxy_oauth_sap"
                            def repo = "proj-common-assets-cd-released-docker-global"
                            def path_to_image = "proj-common-assets-cd-released/security/eric-sec-authorization-proxy-oauth2-sap/"

                            // Fetching Release tag
                            ( release_tag_proxy_oauth_sap, release_tag_version_proxy_oauth_sap ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.proxy_oauth_sap_tag = release_tag_version_proxy_oauth_sap

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_proxy_oauth_sap_tag_present = compareReferenceTagWithReleaseTag(image_name, proxy_oauth_sap, release_tag_proxy_oauth_sap)
                            new_tag_proxy_oauth_sap = is_new_proxy_oauth_sap_tag_present
                        }
                    }
                }
            }
        }
        stage('Get jmx-exporter Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "jmx_exporter"
                            def repo = "proj-adp-message-bus-kf-drop-docker-global"
                            def path_to_image = "proj-adp-message-bus-kf-drop/eric-data-message-bus-kf-jmx-exporter/"

                            // Fetching Release tag
                            ( release_tag_jmx_exporter, release_tag_version_jmx_exporter ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.jmx_exporter_tag = release_tag_version_jmx_exporter

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_jmx_exporter_tag_present = compareReferenceTagWithReleaseTag(image_name, jmx_exporter, release_tag_jmx_exporter)
                            new_tag_jmx_exporter = is_new_jmx_exporter_tag_present
                        }
                    }
                }
            }
        }
        stage('Get api-manager Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "api_manager"
                            def repo = "proj-adp-rs-sef-released-docker-global"
                            def path_to_image = "proj-adp-rs-sef-released/eric-sef-exposure-api-manager-client/"

                            // Fetching Release tag
                            ( release_tag_api_manager, release_tag_version_api_manager ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.api_manager_tag = release_tag_version_api_manager

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_api_manager_tag_present = compareReferenceTagWithReleaseTag(image_name, api_manager, release_tag_api_manager)
                            new_tag_api_manager = is_new_api_manager_tag_present
                        }
                    }
                }
            }
        }
        stage('Get keycloak Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "keycloak_client"
                            def repo = "proj-eric-oss-drop-docker-global"
                            def path_to_image = "proj-eric-oss-drop/keycloak-client/"

                            // Fetching Release tag
                            ( release_tag_keycloak_client, release_tag_version_keycloak_client ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.keycloak_tag = release_tag_version_keycloak_client

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_keycloak_client_tag_present = compareReferenceTagWithReleaseTag(image_name, keycloak, release_tag_keycloak_client)
                            new_tag_keycloak = is_new_keycloak_client_tag_present
                        }
                    }
                }
            }
        }
        stage('Get Log Shipper Sidecar Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "log_shipper_sidecar"
                            def repo = "proj-adp-log-released-docker-global"
                            def path_to_image = "proj-adp-log-released/eric-log-shipper-sidecar/"

                            // Fetching Release tag
                            ( release_tag_log_shipper_sidecar, release_tag_version_log_shipper_sidecar ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.log_shipper_sidecar_tag = release_tag_version_log_shipper_sidecar

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_log_shipper_sidecar_tag_present = compareReferenceTagWithReleaseTag(image_name, log_shipper_sidecar_image_tag, release_tag_log_shipper_sidecar)
                            new_tag_log_shipper_sidecar = is_new_log_shipper_sidecar_tag_present
                        }
                    }
                }
            }
        }
        stage('Get Smart Helm Hooks Version') {
            steps {
                catchError(stageResult: 'FAILURE') {
                    script {
                        withCredentials([usernamePassword(credentialsId: 'SELI_ARTIFACTORY', usernameVariable: 'SELI_ARTIFACTORY_REPO_USER', passwordVariable: 'SELI_ARTIFACTORY_REPO_PASS')]) {

                            def image_name = "smart_helm_hooks"
                            def repo = "proj-adp-shh-released-docker-global"
                            def path_to_image = "proj-adp-shh-released/eric-lcm-smart-helm-hooks-hooklauncher/"

                            // Fetching Release tag
                            ( release_tag_smart_helm_hooks, release_tag_version_smart_helm_hooks ) = fetchLatest2ppVersion(image_name, repo, path_to_image)
                            env.smart_helm_hooks_tag = release_tag_version_smart_helm_hooks

                            // Compare the reference tag with the release tag. If new version exists, upload new version and return true.
                            is_new_smart_helm_hooks_tag_present = compareReferenceTagWithReleaseTag(image_name, smart_helm_hooks_image_tag, release_tag_smart_helm_hooks)
                            new_tag_smart_helm_hooks = is_new_smart_helm_hooks_tag_present
                        }
                    }
                }
            }
        }
        stage('Run Update Jobs In Parallel') {
            steps {
                script {

                    def jobs = [:] // Map to store job definitions

                    repos_map.each { repo, details ->
                        def needed_2pps = details.needed_2pps
                        def email = details.email

                        needed_2pps.each { needed_2pp ->
                            if (needed_2pp == 'eric-oss-key-management-agent' && new_tag_key_management) {
                                jobs["Key Management Agent update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_key_management', repo, email, env.key_management_tag)
                            }
                            else if (needed_2pp == 'api-gateway-client' && new_tag_api_gateway) {
                                jobs["API Gateway Client update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_api_gateway', repo, email, env.api_gateway_tag)
                            }
                            else if (needed_2pp == 'eric-sec-authorization-proxy-oauth2' && new_tag_proxy_oauth) {
                                jobs["Proxy Oauth update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_proxy_oauth', repo, email, env.proxy_oauth_tag)
                            }
                            else if (needed_2pp == 'eric-sec-authorization-proxy-oauth2-sap' && new_tag_proxy_oauth_sap) {
                                jobs["Proxy Oauth SAP update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_proxy_oauth_sap', repo, email, env.proxy_oauth_sap_tag)
                            }
                            else if (needed_2pp == 'eric-data-message-bus-kf-jmx-exporter' && new_tag_jmx_exporter) {
                                jobs["JMX Exporter update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_jmx_exporter', repo, email, env.jmx_exporter_tag)
                            }
                            else if (needed_2pp == 'eric-sef-exposure-api-manager-client' && new_tag_api_manager) {
                                jobs["API Management Client update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_api_management', repo, email, env.api_manager_tag)
                            }
                            else if (needed_2pp == 'keycloak-client' && new_tag_keycloak) {
                                jobs["Keycloak Client update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_keycloak', repo, email, env.keycloak_tag)
                            }
                            else if (needed_2pp == 'eric-log-shipper-sidecar' && new_tag_log_shipper_sidecar) {
                                jobs["Log Shipper Sidecar update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_log_shipper_sidecar', repo, email, env.log_shipper_sidecar_tag)
                            }
                            else if (needed_2pp == 'eric-lcm-smart-helm-hooks-hooklauncher' && new_tag_smart_helm_hooks) {
                                jobs["Smart Helm Hooks update job for ${repo}"] = triggerDownstreamJob('Admin_2pp_update_smart_helm_hooks', repo, email, env.smart_helm_hooks_tag)
                            }
                        }
                    }

                    echo "Jobs to be run in parallel:\n${jobs.keySet().join('\n')}"
                    parallel jobs
                }
            }
        }
    }
    post {
        success {
            mail to: "PDLAEONICC@pdl.internal.ericsson.com", //sending failure notification to HB
            from: "${env.JOB_NAME}-job@ericsson.com",
            subject: "Pipeline '${env.JOB_NAME}' completed successfully for 2pp uplift",
            body: "Following pipeline has completed successfully: ${env.BUILD_URL}. ",
            mimeType: 'text/html'
        }
        failure {
            mail to: "PDLAEONICC@pdl.internal.ericsson.com", //sending failure notification to HB
            from: "${env.JOB_NAME}-job@ericsson.com",
            subject: "Failed Pipeline '${env.JOB_NAME} for 2pp uplift'",
            body: "Failure in build number: ${env.BUILD_NUMBER}. " +
                "<br>2pp Listener failed for below projects: " +
                "<br><br>${failed_repos_list.join( "<br>" )}" +
                "<br><br>Please verify the error in the downstream build " +
                "<br><i>This is an auto-generated email from ${env.BUILD_URL}.</i> ",
            mimeType: 'text/html'
        }
    }
}

def triggerDownstreamJob(jobName, repo, email, tag) {
    return {
        try {
            build job: jobName, propagate: true, wait: true, parameters: [
                string(name: 'REPO', value: repo),
                string(name: 'EMAIL', value: email.join(',')),
                string(name: 'VERSION', value: tag)
            ]
        } catch (exc) {
            failed_repos_list.add("${jobName} failed for ${repo}.")
            throw exc
        }
    }
}

def getRepos() {

    def input_data = readFile(file: 'oss-common-ci-utils/dsl/projects_list_2pp')

    // Split file by new line
    input_data.split('\n').each { line ->

        // Split each line by comma
        def project_details = line.tokenize(",")

        // Get repo details
        def repo = project_details[0].replaceAll("\\s", "")

        // Get email details
        def emailAttribute = project_details.find { it.startsWith('EMAIL=') }
        def email = emailAttribute ? emailAttribute.split('=')[1].split(' ') : []

        // Search for 2pps in the repo
        def found_2pps = searchFor2pps(repo)

        // If 2pps were found, add repo + email & needed 2pps to map
        if (found_2pps) {
            repos_map[repo] = [email: email, needed_2pps: found_2pps]
        }
    }
}

def searchFor2pps(repo) {
    // List of 2pps to search for in eric-product-info.yaml file
    def tags_to_search = [
        'keycloak-client',
        'eric-sec-authorization-proxy-oauth2-sap',
        'eric-sec-authorization-proxy-oauth2',
        'eric-data-message-bus-kf-jmx-exporter',
        'api-gateway-client',
        'eric-oss-key-management-agent',
        'eric-sef-exposure-api-manager-client',
        'eric-log-shipper-sidecar',
        'eric-lcm-smart-helm-hooks-hooklauncher'
    ]
    def artifact_id = repo.split('/').last()
    def product_info_file = "eric-product-info.yaml"
    def found_2pps = []

    // Clone Gerrit Repo
    sh "git clone ${GERRIT_MIRROR}/${repo}"

    // Search for eric-product-info.yaml file
    def files = sh(script: "find ${WORKSPACE}/${artifact_id} -type f -name ${product_info_file}", returnStdout: true).trim().split('\n')

    // Search through file for each 2pp tag
    files.each { file ->
        if (fileExists(file)) {
            def fileContent = readFile(file)
            tags_to_search.each { tag ->
                if (fileContent.contains(tag)) {
                    found_2pps.add(tag)
                }
            }
        }
    }

    // Remove repo directory from workspace
    sh "rm -rf ${WORKSPACE}/${artifact_id}"

    return found_2pps
}

def fetchLatest2ppVersion(image_name, repo, path) {

    String release_tag_version
    def release_tag = "release_tag_" + image_name

    // Fetch latest image version
    sh """
        curl -u \$SELI_ARTIFACTORY_REPO_USER:\$SELI_ARTIFACTORY_REPO_PASS -X POST \
        -H 'content-type: text/plain'  https://arm.epk.ericsson.se/artifactory/api/search/aql \
        -d 'items.find({ "repo": {"\$eq":"${repo}"}, "path": {"\$match" : "${path}*-*"}}).sort({"\$desc": ["created"]}).limit(1)' 2>/dev/null \
        | grep path \
        | sed -e 's_.*\\/\\(.*\\)".*_\\1_' \
        > ${release_tag}
    """

    // validate that version is valid if file exists
    if (fileExists(release_tag)) {
        release_tag_version = readFile(file: release_tag).trim() // read file and remove empty spaces
        echo "Latest " + image_name + " image version: ${release_tag_version}"

        (versionFormatValid, errorMessage) = ci_pipeline_init.isVersionValid(release_tag_version)
        if (!versionFormatValid) {
            failed_repos_list.add(errorMessage) // display failure reason in email
            error errorMessage
        }
    }

    return [ release_tag, release_tag_version ]

}

def compareReferenceTagWithReleaseTag(image_name, latest_tag, release_tag) {

    def ref_tag = "ref_tag_" + image_name
    def is_new_tag_present = false

    // Fetch reference tag from monitoring repo
    def referenceTagInRepo = sh(returnStdout: true, script: "curl -v -u \$SELI_ARTIFACTORY_REPO_USER:\$SELI_ARTIFACTORY_REPO_PASS '${img_tag_url}/${latest_tag}' 2>/dev/null | tee ${ref_tag}")
    print "Reference image version for ${image_name} from monitoring repo is: ${referenceTagInRepo}"

    // Compare reference tag and release tag
    def doVersionsMatchExitCode = sh(returnStdout: true, script: "cmp ${release_tag} ${ref_tag}", returnStatus: true)

    // If versions do not match, update reference tag with new version and set "is_new_tag_present" to true.
    if (doVersionsMatchExitCode == 1) {
        echo "Versions are different, updating reference tag in monitoring repo."
        is_new_tag_present = true
        uploadNewVersionResponseCode = sh(returnStdout: true, script: "curl -i -w '%{http_code}' -u \$SELI_ARTIFACTORY_REPO_USER:\$SELI_ARTIFACTORY_REPO_PASS -X PUT -T ${release_tag} -o ${image_name}_response.txt  ${img_tag_url}/${latest_tag}")

        // Check if update was successful by checking response code
        if(uploadNewVersionResponseCode == "201") {
            print "------------- Upload Success -------------"
        } else {
            def errorMessage = "Error uploading new ${image_name} version with response code ${uploadNewVersionResponseCode}. See ${image_name}_response.txt for more details!"
            failed_repos_list.add(errorMessage)
            error errorMessage
        }

    } else {
        print "No difference between ${image_name} versions"
    }

    return is_new_tag_present
}