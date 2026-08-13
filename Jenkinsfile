pipeline {

    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    environment {

        // GitHub
        GIT_URL = 'https://github.com/1998kruthik-commits/Python-Projects.git'
        GIT_BRANCH = 'main'

        // DockerHub
        DOCKER_REPO = 'kruthikchethu'

        MEDICAL_IMAGE = "${DOCKER_REPO}/medical-chat"
        ML_IMAGE      = "${DOCKER_REPO}/ml-app"

        BUILD_TAG_VALUE = "${BUILD_NUMBER}"

        // Azure
        AZ_RESOURCE_GROUP = 'MLPython3418'
        AKS_CLUSTER       = 'MLPython'

        // Azure Container Registry if you later use ACR
        ACR_NAME = ''

        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    }

    stages {

        /*
         * ---------------------------------------------------------
         * 1. CLEAN WORKSPACE
         * ---------------------------------------------------------
         */
        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        /*
         * ---------------------------------------------------------
         * 2. CHECKOUT
         * ---------------------------------------------------------
         */
        stage('Checkout') {
            steps {
                git branch: "${GIT_BRANCH}",
                    credentialsId: 'github-creds',
                    url: "${GIT_URL}"
            }
        }

        /*
         * ---------------------------------------------------------
         * 3. VERIFY PROJECT
         * ---------------------------------------------------------
         */
        stage('Verify Project') {
            steps {
                sh '''
                    echo "===== PROJECT STRUCTURE ====="
                    find . -maxdepth 3 -type f | sort | head -200

                    echo ""
                    echo "===== DOCKER ====="
                    docker --version || true

                    echo ""
                    echo "===== KUBECTL ====="
                    kubectl version --client || true

                    echo ""
                    echo "===== AZURE CLI ====="
                    az version || true
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 4. SONARQUBE
         * ---------------------------------------------------------
         */
        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        if command -v sonar-scanner >/dev/null 2>&1; then
                            sonar-scanner \
                              -Dsonar.projectKey=MLPython \
                              -Dsonar.projectName=MLPython \
                              -Dsonar.sources=.
                        else
                            echo "sonar-scanner not installed - skipping"
                        fi
                    '''
                }
            }
        }

        /*
         * ---------------------------------------------------------
         * 5. BUILD MEDICAL IMAGE
         * ---------------------------------------------------------
         */
        stage('Build Medical Docker Image') {
            steps {
                sh '''
                    if [ -f medical/Dockerfile ]; then
                        docker build \
                            -t ${MEDICAL_IMAGE}:${BUILD_NUMBER} \
                            -t ${MEDICAL_IMAGE}:latest \
                            ./medical
                    else
                        echo "medical/Dockerfile not found"
                    fi
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 6. BUILD ML IMAGE
         * ---------------------------------------------------------
         */
        stage('Build ML Docker Image') {
            steps {
                sh '''
                    if [ -f ml/Dockerfile ]; then
                        docker build \
                            -t ${ML_IMAGE}:${BUILD_NUMBER} \
                            -t ${ML_IMAGE}:latest \
                            ./ml
                    elif [ -f Dockerfile ]; then
                        docker build \
                            -t ${ML_IMAGE}:${BUILD_NUMBER} \
                            -t ${ML_IMAGE}:latest \
                            .
                    else
                        echo "No ML Dockerfile found"
                    fi
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 7. DOCKERHUB LOGIN
         * ---------------------------------------------------------
         *
         * Create Jenkins credential:
         *
         * ID: dockerhub-creds
         * Type: Username with password
         *
         */
        stage('DockerHub Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login \
                            -u "$DOCKER_USER" \
                            --password-stdin
                    '''
                }
            }
        }

        /*
         * ---------------------------------------------------------
         * 8. PUSH IMAGES
         * ---------------------------------------------------------
         */
        stage('Push Images to DockerHub') {
            steps {
                sh '''
                    echo "===== PUSHING MEDICAL IMAGE ====="

                    if docker image inspect ${MEDICAL_IMAGE}:${BUILD_NUMBER} >/dev/null 2>&1; then
                        docker push ${MEDICAL_IMAGE}:${BUILD_NUMBER}
                        docker push ${MEDICAL_IMAGE}:latest
                    fi

                    echo "===== PUSHING ML IMAGE ====="

                    if docker image inspect ${ML_IMAGE}:${BUILD_NUMBER} >/dev/null 2>&1; then
                        docker push ${ML_IMAGE}:${BUILD_NUMBER}
                        docker push ${ML_IMAGE}:latest
                    fi
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 9. AZURE LOGIN
         * ---------------------------------------------------------
         *
         * Jenkins credential:
         *
         * ID: azure-service-principal
         * Type: Secret text
         *
         * Value:
         * <service-principal-json>
         *
         */
        stage('Azure Login') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'azure-service-principal',
                        variable: 'AZURE_CREDENTIALS'
                    )
                ]) {
                    sh '''
                        az login --service-principal \
                            --username "$(echo "$AZURE_CREDENTIALS" | python3 -c 'import sys,json; print(json.load(sys.stdin)["clientId"])')" \
                            --password "$(echo "$AZURE_CREDENTIALS" | python3 -c 'import sys,json; print(json.load(sys.stdin)["clientSecret"])')" \
                            --tenant "$(echo "$AZURE_CREDENTIALS" | python3 -c 'import sys,json; print(json.load(sys.stdin)["tenantId"])')" \
                            >/dev/null

                        az account set --subscription "$(echo "$AZURE_CREDENTIALS" | python3 -c 'import sys,json; print(json.load(sys.stdin)["subscriptionId"])')"

                        az account show -o table
                    '''
                }
            }
        }

        /*
         * ---------------------------------------------------------
         * 10. GET AKS CREDENTIALS
         * ---------------------------------------------------------
         */
        stage('Connect to AKS') {
            steps {
                sh '''
                    az aks get-credentials \
                        --resource-group "${AZ_RESOURCE_GROUP}" \
                        --name "${AKS_CLUSTER}" \
                        --overwrite-existing

                    kubectl cluster-info

                    echo "===== NODES ====="
                    kubectl get nodes
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 11. UPDATE KUBERNETES IMAGES
         * ---------------------------------------------------------
         */
        stage('Update Kubernetes Images') {
            steps {
                sh '''
                    echo "===== KUBERNETES FILES ====="
                    find . -type f \\( \
                        -name "*.yaml" -o \
                        -name "*.yml" \
                    \\) | sort

                    if [ -d k8s ]; then

                        echo "===== APPLYING K8S CONFIG ====="

                        kubectl apply -f k8s/

                        echo "===== UPDATING MEDICAL IMAGE ====="

                        kubectl set image deployment/medical-chat \
                            medical-chat=${MEDICAL_IMAGE}:${BUILD_NUMBER} \
                            --record=false || true

                        echo "===== UPDATING ML IMAGE ====="

                        kubectl set image deployment/ml-app \
                            ml-app=${ML_IMAGE}:${BUILD_NUMBER} \
                            --record=false || true

                    else
                        echo "k8s directory not found"
                    fi
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 12. WAIT FOR DEPLOYMENT
         * ---------------------------------------------------------
         */
        stage('Wait for Kubernetes') {
            steps {
                sh '''
                    echo "===== DEPLOYMENTS ====="
                    kubectl get deployments -A

                    echo ""
                    echo "===== PODS ====="
                    kubectl get pods -A -o wide

                    echo ""
                    echo "===== SERVICES ====="
                    kubectl get svc -A
                '''
            }
        }

        /*
         * ---------------------------------------------------------
         * 13. VERIFY
         * ---------------------------------------------------------
         */
        stage('Deployment Verification') {
            steps {
                sh '''
                    echo "===== POD STATUS ====="
                    kubectl get pods -A

                    echo ""
                    echo "===== SERVICE STATUS ====="
                    kubectl get svc -A

                    echo ""
                    echo "===== DEPLOYMENT STATUS ====="
                    kubectl get deployments -A
                '''
            }
        }
    }

    post {

        success {
            echo '''
            ============================================
                    PIPELINE SUCCESSFUL
            ============================================
            Docker images pushed successfully.
            Kubernetes deployment completed.
            ============================================
            '''
        }

        failure {
            echo '''
            ============================================
                    PIPELINE FAILED
            ============================================
            Check the failed stage above.
            ============================================
            '''
        }

        always {
            sh '''
                docker logout || true

                echo "===== FINAL DOCKER IMAGES ====="
                docker images | head -20 || true
            '''
        }
    }
}
