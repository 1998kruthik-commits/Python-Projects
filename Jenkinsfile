pipeline {

    agent any

    environment {

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        MEDICAL_IMAGE = "kruthikchethu/medical-chatbot:v1"
        ARR_IMAGE     = "kruthikchethu/arrhythmia:v1"

        DOCKER_CREDS = credentials('dockerhub')
    }

    stages {

        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                    url: "${GIT_URL}"
            }
        }

        stage('Workspace Information') {
            steps {
                sh '''
                echo "Current Directory:"
                pwd

                echo ""
                echo "Repository Contents:"
                ls -la

                echo ""
                echo "Available Projects:"
                find . -maxdepth 1 -type d
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {

                script {

                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('sonarqube') {

                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=PythonProjects \
                        -Dsonar.projectName=PythonProjects \
                        -Dsonar.sources=. \
                        -Dsonar.sourceEncoding=UTF-8
                        """

                    }

                }

            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Medical Chatbot Image') {
            steps {

                dir('medical-chatbot') {

                    sh '''
                    echo "Building Medical Chatbot Image..."

                    docker build -t ${MEDICAL_IMAGE} .
                    '''

                }

            }
        }

        stage('Build Arrhythmia Image') {
            steps {

                dir('Classification of Arrhythmia [ECG DATA]') {

                    sh '''
                    echo "Building Arrhythmia Image..."

                    docker build -t ${ARR_IMAGE} .
                    '''

                }

            }
        }

        stage('Docker Login') {

            steps {

                sh '''
                echo ${DOCKER_CREDS_PSW} | docker login \
                -u ${DOCKER_CREDS_USR} \
                --password-stdin
                '''

            }

        }

        stage('Push Docker Images') {

            steps {

                sh '''
                docker push ${MEDICAL_IMAGE}

                docker push ${ARR_IMAGE}
                '''

            }

        }

        stage('Docker Logout') {

            steps {

                sh '''
                docker logout
                '''

            }

        }

        stage('Cleanup') {

            steps {

                sh '''
                docker image prune -f
                '''

            }

        }

    }

    post {

        success {

            echo "========================================="
            echo "Pipeline Completed Successfully"
            echo "========================================="

        }

        failure {

            echo "========================================="
            echo "Pipeline Failed"
            echo "========================================="

        }

        always {

            cleanWs()

        }

    }

}
