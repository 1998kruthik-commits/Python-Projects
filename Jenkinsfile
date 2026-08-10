pipeline {

    agent any

    environment {
        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        DOCKER_REPO = "kruthikchethu"
        BUILD_TAG = "${BUILD_NUMBER}"

        MEDICAL_IMAGE = "${DOCKER_REPO}/medical-chatbot:${BUILD_TAG}"
        ARR_IMAGE     = "${DOCKER_REPO}/arrhythmia:${BUILD_TAG}"

        RESOURCE_GROUP = "TeamZanskar"
        AKS_NAME       = "myakcluster"
        KEY_VAULT_NAME = "myakcluster"

        SUBSCRIPTION_ID = "f0c66309-7e43-4400-9c2b-4304e2c2a752"
    }

    stages {

        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Workspace Info') {
            steps {
                sh '''
                    echo "========================================"
                    echo "WORKSPACE INFORMATION"
                    echo "========================================"

                    pwd
                    ls -la

                    echo "========================================"
                    echo "KUBECTL"
                    echo "========================================"

                    which kubectl
                    kubectl version --client
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {

                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('mypython') {

                        sh """
                            echo "========================================"
                            echo "SONARQUBE ANALYSIS"
                            echo "========================================"

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
                    credentialIDOverride: 'azure-sp-jenkins',
                    keyVaultURLOverride: 'https://mlpythonproject.vault.azure.net/',
                    azureKeyVaultSecrets: [
                        [
                            secretType: 'Secret',
                            name: 'storage-connection-string',
                            envVariable: 'AZURE_STORAGE_CONNECTION_STRING'
                        ]
                    ]
                ) {

                    sh '''
                        echo "========================================"
                        echo "AZURE KEY VAULT"
                        echo "========================================"

                        if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
                            echo "ERROR: Secret was not loaded from Azure Key Vault"
                            exit 1
                        fi

                        echo "Azure Key Vault secret loaded successfully"
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
                                echo "========================================"
                                echo "BUILDING MEDICAL CHATBOT IMAGE"
                                echo "========================================"

                                docker build \
                                    -t ${MEDICAL_IMAGE} .
                            '''
                        }
                    }
                }

                stage('Arrhythmia') {
                    steps {

                        dir('Classification of Arrhythmia [ECG DATA]') {

                            sh '''
                                echo "========================================"
                                echo "BUILDING ARRHYTHMIA IMAGE"
                                echo "========================================"

                                docker build \
                                    -t ${ARR_IMAGE} .
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
                credentialsId: 'dockerhub-creds',
                usernameVariable: 'DOCKER_USER',
                passwordVariable: 'DOCKER_PASS'
            )
        ]) {
            sh '''
                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                docker push ${MEDICAL_IMAGE}
                docker push ${ARR_IMAGE}

                echo "Docker images pushed successfully"
            '''
        }
    }
}

        stage('Update Kubernetes Manifests') {

            steps {

                sh '''
                    echo "========================================"
                    echo "UPDATING KUBERNETES MANIFESTS"
                    echo "========================================"

                    sed -i "s|image: .*medical-chatbot.*|image: ${MEDICAL_IMAGE}|g" \
                        k8s/medical-chatbot-deployment.yaml

                    sed -i "s|image: .*arrhythmia.*|image: ${ARR_IMAGE}|g" \
                        k8s/arrhythmia-deployment.yml

                    echo "Medical Chatbot image:"
                    grep "image:" k8s/medical-chatbot-deployment.yaml

                    echo "Arrhythmia image:"
                    grep "image:" k8s/arrhythmia-deployment.yml
                '''
            }
        }

        stage('Login to Azure') {
    steps {
        withCredentials([
            azureServicePrincipal('azure-sp-jenkins'),
            string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
        ]) {
            sh '''
                az login \
                    --service-principal \
                    -u "$AZURE_CLIENT_ID" \
                    -p "$AZURE_CLIENT_SECRET" \
                    --tenant "$AZURE_TENANT_ID"

                az account set --subscription "$SUBSCRIPTION_ID"
                az account show
            '''
        }
    }
}

        stage('Get & Verify AKS Credentials') {
    steps {
        sh '''
            az aks get-credentials \
                --resource-group "$RESOURCE_GROUP" \
                --name "$AKS_NAME" \
                --overwrite-existing

            kubectl config current-context
            kubectl get nodes
        '''
    }
}

       stage('Deploy & Verify AKS') {
    steps {
        sh '''
            kubectl apply -f k8s/medical-chatbot-deployment.yaml
            kubectl apply -f k8s/arrhythmia-deployment.yml

            kubectl rollout status deployment/medical-chatbot --timeout=180s
            kubectl rollout status deployment/arrhythmia --timeout=180s

            kubectl get pods
            kubectl get svc
        '''
    }
}

        stage('AKS Health Check') {

            steps {

                sh '''
                    echo "========================================"
                    echo "AKS SERVICES"
                    echo "========================================"

                    kubectl get svc

                    echo "========================================"
                    echo "WAITING FOR MEDICAL CHATBOT EXTERNAL IP"
                    echo "========================================"

                    MEDICAL_IP=""

                    for i in {1..30}; do

                        MEDICAL_IP=$(kubectl get svc medical-chatbot-service \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
                            2>/dev/null || true)

                        if [ -n "$MEDICAL_IP" ]; then
                            echo "Medical Chatbot External IP: $MEDICAL_IP"
                            break
                        fi

                        echo "Attempt $i/30 - Medical Chatbot External IP not ready..."

                        sleep 10
                    done

                    if [ -z "$MEDICAL_IP" ]; then

                        echo "ERROR: Medical Chatbot External IP was not assigned"

                        kubectl get svc medical-chatbot-service || true

                        kubectl describe svc medical-chatbot-service || true

                        exit 1
                    fi


                    echo "========================================"
                    echo "WAITING FOR ARRHYTHMIA EXTERNAL IP"
                    echo "========================================"

                    ARRHYTHMIA_IP=""

                    for i in {1..30}; do

                        ARRHYTHMIA_IP=$(kubectl get svc arrhythmia-service \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
                            2>/dev/null || true)

                        if [ -n "$ARRHYTHMIA_IP" ]; then
                            echo "Arrhythmia External IP: $ARRHYTHMIA_IP"
                            break
                        fi

                        echo "Attempt $i/30 - Arrhythmia External IP not ready..."

                        sleep 10
                    done

                    if [ -z "$ARRHYTHMIA_IP" ]; then

                        echo "ERROR: Arrhythmia External IP was not assigned"

                        kubectl get svc arrhythmia-service || true

                        kubectl describe svc arrhythmia-service || true

                        exit 1
                    fi


                    echo "========================================"
                    echo "APPLICATION URLS"
                    echo "========================================"

                    echo "Medical Chatbot:"
                    echo "http://$MEDICAL_IP"

                    echo ""

                    echo "Arrhythmia:"
                    echo "http://$ARRHYTHMIA_IP"

                    echo ""
                    echo "========================================"
                    echo "AKS HEALTH CHECK PASSED"
                    echo "========================================"
                '''
            }
        }
    }

    post {

        success {

            echo "========================================"
            echo "PIPELINE COMPLETED SUCCESSFULLY"
            echo "========================================"

            sh '''
                echo "Final AKS Status:"
                kubectl get deployments
                kubectl get pods
                kubectl get svc
            '''
        }

        failure {

            echo "========================================"
            echo "PIPELINE FAILED"
            echo "========================================"

            sh '''
                echo "Collecting AKS diagnostics..."

                kubectl get deployments || true
                kubectl get pods -o wide || true
                kubectl get svc || true
            '''
        }

        always {

            echo "Cleaning Jenkins workspace..."

            cleanWs()
        }
    }
}
