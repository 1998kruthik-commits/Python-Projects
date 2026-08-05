pipeline {

    agent any

    environment {

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        MEDICAL_IMAGE = "medical-chatbot:latest"
        ARR_IMAGE     = "arrhythmia:latest"

        MEDICAL_CONTAINER = "medical-chatbot"
        ARR_CONTAINER     = "arrhythmia"

        MEDICAL_PORT = "5000"
        ARR_PORT     = "5010"

        KEY_VAULT_NAME = "mlproject-keyvault"
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
                echo "=========================================="
                echo "Workspace Information"
                echo "=========================================="

                pwd
                ls -la

                echo ""
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

        stage('Fetch Secrets from Azure Key Vault') {
            steps {

                withAzureKeyvault(
                    azureKeyVaultSecrets: [
                        [
                            secretType: 'Secret',
                            name: 'storage-connection-string',
                            envVariable: 'AZURE_STORAGE_CONNECTION_STRING'
                        ]
                    ]
                ) {

                    sh '''
                    echo "Azure Key Vault Secret Loaded Successfully"
                    '''

                }
            }
        }

        stage('Build Medical Chatbot Image') {
            steps {

                dir('medical-chatbot') {

                    sh '''
                    echo "Building Medical Chatbot Image"

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
                    echo "Building Arrhythmia Image"

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

        stage('Run Medical Chatbot') {
            steps {

                sh '''
                docker run -d \
                  --name ${MEDICAL_CONTAINER} \
                  -p ${MEDICAL_PORT}:${MEDICAL_PORT} \
                  -e AZURE_STORAGE_CONNECTION_STRING="${AZURE_STORAGE_CONNECTION_STRING}" \
                  -e KEY_VAULT_NAME="${KEY_VAULT_NAME}" \
                  ${MEDICAL_IMAGE}
                '''

            }
        }

        stage('Run Arrhythmia') {
            steps {

                sh '''
                docker run -d \
                  --name ${ARR_CONTAINER} \
                  -p ${ARR_PORT}:${ARR_PORT} \
                  -e AZURE_STORAGE_CONNECTION_STRING="${AZURE_STORAGE_CONNECTION_STRING}" \
                  -e KEY_VAULT_NAME="${KEY_VAULT_NAME}" \
                  ${ARR_IMAGE}
                '''

            }
        }

        stage('Health Check') {
            steps {

                sh '''
                echo "Waiting for applications..."
                sleep 20

                echo ""
                docker ps

                echo ""
                echo "Medical Chatbot Health"

                curl -f http://localhost:${MEDICAL_PORT}/health || true

                echo ""
                echo "Arrhythmia"

                curl -f http://localhost:${ARR_PORT}/ || true
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

            echo "Medical Chatbot : http://<VM-IP>:5000"
            echo "Arrhythmia      : http://<VM-IP>:5010"

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
