pipeline {

    agent any

    environment {

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        DOCKER_REPO = "kruthikchethu"

        BUILD_TAG = "${BUILD_NUMBER}"

        MEDICAL_IMAGE = "${DOCKER_REPO}/medical-chatbot:${BUILD_TAG}"
        ARR_IMAGE     = "${DOCKER_REPO}/arrhythmia:${BUILD_TAG}"

        RESOURCE_GROUP = "Team_zanskar"
        AKS_NAME       = "MLProject-AKS"

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
                pwd
                ls -la
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

                timeout(time:15, unit:'MINUTES') {

                    waitForQualityGate abortPipeline:false

                }

            }

        }

        stage('Fetch Secrets from Azure Key Vault') {

            steps {

                withAzureKeyvault(

                    credentialIDOverride:'azure-sp-jenkins',

                    keyVaultURLOverride:'https://mlproject-keyvault.vault.azure.net/',

                    azureKeyVaultSecrets:[

                        [

                            secretType:'Secret',

                            name:'storage-connection-string',

                            envVariable:'AZURE_STORAGE_CONNECTION_STRING'

                        ]

                    ]

                ) {

                    sh '''
                    echo "Azure KeyVault Secret Loaded"
                    '''

                }

            }

        }

        stage('Build Docker Images') {

            parallel {

                stage('Medical Chatbot') {

                    steps {

                        dir('medical-chatbot') {

                            sh '''
                            docker build -t ${MEDICAL_IMAGE} .
                            '''

                        }

                    }

                }

                stage('Arrhythmia') {

                    steps {

                        dir('Classification of Arrhythmia [ECG DATA]') {

                            sh '''
                            docker build -t ${ARR_IMAGE} .
                            '''

                        }

                    }

                }

            }

        }

        stage('Push Images to DockerHub') {

            steps {

                withCredentials([

                    usernamePassword(

                        credentialsId:'dockerhub-creds',

                        usernameVariable:'DOCKER_USER',

                        passwordVariable:'DOCKER_PASS'

                    )

                ]) {

                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin

                    docker push ${MEDICAL_IMAGE}
                    docker push ${ARR_IMAGE}
                    '''

                }

            }

        }

        stage('Update Kubernetes Manifests') {

            steps {

                sh """
                sed -i 's|image: .*medical-chatbot.*|image: ${MEDICAL_IMAGE}|g' k8s/medical-chatbot-deployment.yaml

                sed -i 's|image: .*arrhythmia.*|image: ${ARR_IMAGE}|g' k8s/arrhythmia-deployment.yml
                """

            }

        }

        stage('Login to Azure') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId:'azure-sp-jenkins',
                usernameVariable:'AZURE_CLIENT_ID',
                passwordVariable:'AZURE_CLIENT_SECRET'
            ),
            string(
                credentialsId:'azure-tenant-id',
                variable:'AZURE_TENANT_ID'
            )
        ]) {
            sh '''
            az login --service-principal \
            -u $AZURE_CLIENT_ID \
            -p $AZURE_CLIENT_SECRET \
            --tenant $AZURE_TENANT_ID

            az account set --subscription 34223793-8b41-4434-a686-438e9f0dc8df

            az account show
            '''
        }
    }
}

        stage('Get AKS Credentials') {

            steps {

                sh '''
                az aks get-credentials \
                --resource-group ${RESOURCE_GROUP} \
                --name ${AKS_NAME} \
                --overwrite-existing
                '''

            }

        }

        stage('Deploy to AKS') {

            steps {

                sh '''
                kubectl apply -f k8s/
                '''

            }

        }

        stage('Verify Deployment') {

            steps {

                sh '''
                kubectl rollout status deployment/medical-chatbot

                kubectl rollout status deployment/arrhythmia

                kubectl get pods

                kubectl get svc
                '''

            }

        }

        stage('AKS Health Check') {

            steps {

                sh '''

                MEDICAL_IP=$(kubectl get svc medical-chatbot-service -o jsonpath="{.status.loadBalancer.ingress[0].ip}")

                ARR_IP=$(kubectl get svc arrhythmia-service -o jsonpath="{.status.loadBalancer.ingress[0].ip}")

                echo "Medical Chatbot IP: $MEDICAL_IP"

                echo "Arrhythmia IP: $ARR_IP"

                echo ""

                curl http://$MEDICAL_IP/health || true

                curl http://$ARR_IP/health || true

                '''

            }

        }

    }

    post {

        success {

            echo "=================================="

            echo "Pipeline Completed Successfully"

            echo "=================================="

            sh '''

            kubectl get pods

            kubectl get svc

            '''

        }

        failure {

            echo "Pipeline Failed"

        }

        always {

            cleanWs()

        }

    }

}
