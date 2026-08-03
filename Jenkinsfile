pipeline {

    agent any

    environment {

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        // Docker Images
        MEDICAL_IMAGE = "medical-chatbot:latest"
        ARR_IMAGE     = "arrhythmia:latest"

        // Container Names
        MEDICAL_CONTAINER = "medical-chatbot"
        ARR_CONTAINER     = "arrhythmia"

        // Ports
        MEDICAL_PORT = "5000"
        ARR_PORT     = "5010"
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
                echo "=================================="
                echo "Workspace Information"
                echo "=================================="

                pwd

                echo ""
                ls -la

                echo ""
                echo "Projects:"
                find . -maxdepth 2 -type d
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
                        -Dsonar.sourceEncoding=UTF-8 \
                        -Dsonar.python.version=3.12
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Medical Chatbot Image') {
            steps {

                dir('medical-chatbot') {

                    sh '''
                    echo "Building Medical Chatbot Docker Image..."

                    docker build -t ${MEDICAL_IMAGE} .

                    docker images | grep medical-chatbot
                    '''
                }
            }
        }

        stage('Build Arrhythmia Image') {
            steps {

                dir('Classification of Arrhythmia [ECG DATA]') {

                    sh '''
                    echo "Building Arrhythmia Docker Image..."

                    docker build -t ${ARR_IMAGE} .

                    docker images | grep arrhythmia
                    '''
                }
            }
        }

        stage('Stop Existing Containers') {
            steps {
                sh '''
                docker stop ${MEDICAL_CONTAINER} || true
                docker stop ${ARR_CONTAINER} || true
                '''
            }
        }

        stage('Remove Existing Containers') {
            steps {
                sh '''
                docker rm ${MEDICAL_CONTAINER} || true
                docker rm ${ARR_CONTAINER} || true
                '''
            }
        }

        stage('Run Medical Chatbot Container') {
            steps {
                sh '''
                echo "Starting Medical Chatbot..."

                docker run -d \
                --name ${MEDICAL_CONTAINER} \
                -p ${MEDICAL_PORT}:${MEDICAL_PORT} \
                ${MEDICAL_IMAGE}
                '''
            }
        }

        stage('Run Arrhythmia Container') {
            steps {
                sh '''
                echo "Starting Arrhythmia Application..."

                docker run -d \
                --name ${ARR_CONTAINER} \
                -p ${ARR_PORT}:${ARR_PORT} \
                ${ARR_IMAGE}
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                echo "Waiting for containers..."
                sleep 20

                echo ""
                echo "Running Containers:"
                docker ps

                echo ""
                echo "Medical Chatbot Check"
                curl http://localhost:${MEDICAL_PORT} || true

                echo ""
                echo "Arrhythmia Check"
                curl http://localhost:${ARR_PORT} || true
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
            echo "======================================="
            echo "Pipeline Completed Successfully"
            echo "Medical Chatbot : http://<VM-IP>:5000"
            echo "Arrhythmia      : http://<VM-IP>:5010"
            echo "======================================="
        }

        failure {
            echo "======================================="
            echo "Pipeline Failed"
            echo "======================================="
        }

        always {
            cleanWs()
        }
    }
}
