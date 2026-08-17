pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
        disableConcurrentBuilds(abortPrevious: true)
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
    }

    parameters {
        choice(
            name: 'TEST_SUITE',
            choices: ['smoke', 'regression', 'mobile'],
            description: 'pytest marker to execute'
        )
        choice(
            name: 'EXECUTION_TARGET',
            choices: ['local', 'lambdatest'],
            description: 'Run on the Jenkins agent or the cloud Grid'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox'],
            description: 'Browser requested by the test suite'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run local browsers without a visible window'
        )
        choice(
            name: 'WORKERS',
            choices: ['1', '2', '4'],
            description: 'Parallel pytest workers'
        )
    }

    environment {
        VENV_DIR = "${WORKSPACE}/.venv"
        REPORT_DIR = "${WORKSPACE}/reports"
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
        PYTHONDONTWRITEBYTECODE = '1'
    }

    stages {
        stage('Validate parameters') {
            steps {
                script {
                    if (params.TEST_SUITE == 'mobile' && params.BROWSER != 'chrome') {
                        error('The mobile profile uses Chrome emulation; choose the Chrome browser.')
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build environment') {
            steps {
                sh label: 'Create Python environment', script: '''
                    python3 -m venv "$VENV_DIR"
                    "$VENV_DIR/bin/python" -m pip install --upgrade pip
                    "$VENV_DIR/bin/python" -m pip install -e ".[test]"
                    mkdir -p "$REPORT_DIR"
                '''
            }
        }

        stage('Static analysis') {
            steps {
                sh label: 'Run Ruff', script: '''
                    "$VENV_DIR/bin/ruff" check .
                    "$VENV_DIR/bin/ruff" format --check .
                '''
            }
        }

        stage('Framework tests') {
            steps {
                sh label: 'Run unit tests', script: '''
                    "$VENV_DIR/bin/pytest" -m unit \
                        --junitxml="$REPORT_DIR/framework.xml"
                '''
            }
        }

        stage('Browser acceptance') {
            steps {
                script {
                    def headedFlag = params.HEADLESS ? '' : '--headed'
                    withEnv([
                        "PYTEST_MARKER=${params.TEST_SUITE}",
                        "TEST_TARGET=${params.EXECUTION_TARGET}",
                        "TEST_BROWSER=${params.BROWSER}",
                        "TEST_HEADED_FLAG=${headedFlag}",
                        "TEST_WORKERS=${params.WORKERS}",
                        "TEST_BUILD=Jenkins ${env.JOB_NAME} #${env.BUILD_NUMBER}"
                    ]) {
                        def runAcceptance = {
                            sh label: 'Run browser acceptance tests', script: '''
                                "$VENV_DIR/bin/pytest" \
                                    -m "$PYTEST_MARKER" \
                                    --target="$TEST_TARGET" \
                                    --browser="$TEST_BROWSER" \
                                    --build-name="$TEST_BUILD" \
                                    $TEST_HEADED_FLAG \
                                    -n "$TEST_WORKERS" \
                                    --junitxml="$REPORT_DIR/acceptance.xml" \
                                    --html="$REPORT_DIR/report.html" \
                                    --self-contained-html
                            '''
                        }

                        if (params.EXECUTION_TARGET == 'lambdatest') {
                            withCredentials([usernamePassword(
                                credentialsId: 'lambdatest-credentials',
                                usernameVariable: 'LT_USERNAME',
                                passwordVariable: 'LT_ACCESS_KEY'
                            )]) {
                                runAcceptance()
                            }
                        } else {
                            runAcceptance()
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            publishHTML target: [
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'pytest acceptance report'
            ]
            archiveArtifacts allowEmptyArchive: true,
                artifacts: 'reports/**/*',
                fingerprint: true
            cleanWs deleteDirs: true, notFailBuild: true
        }
    }
}
