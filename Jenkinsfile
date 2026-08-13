pipeline {

    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    environment {

        // =====================================================
        // GITHUB
        // =====================================================
        GIT_URL = 'https://github.com/1998kruthik-commits/Python-Projects.git'
        GIT_BRANCH = 'main'

        // =====================================================
        // DOCKER HUB
        // =====================================================
        DOCKER_REPO = 'kruthikchethu'

        ARRHYTHMIA_IMAGE = "${DOCKER_REPO}/arrhythmia"

        // =====================================================
        // AZURE
        // =====================================================
        AZ_RESOURCE_GROUP = 'MLPython3418'
        AKS_CLUSTER = 'MLPython'

        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"
    }


    stages {

        // =====================================================
        // 1. CLEAN WORKSPACE
        // =====================================================
        stage('Clean Workspace') {
            steps {
                deleteDir()
            }
        }


        // =====================================================
        // 2. CHECKOUT
        // =====================================================
        stage('Checkout') {
            steps {

                git(
                    branch: "${GIT_BRANCH}",
                    url: "${GIT_URL}"
                )

            }
        }


        // =====================================================
        // 3. VERIFY PROJECT
        // =====================================================
        stage('Verify Project') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "PROJECT STRUCTURE"
                    echo "=========================================="

                    find . -maxdepth 3 -type f \
                        ! -path "./.git/*" \
                        | sort | head -200

                    echo ""
                    echo "=========================================="
                    echo "TOOLS"
                    echo "=========================================="

                    echo "Docker:"
                    docker --version

                    echo ""
                    echo "Kubectl:"
                    kubectl version --client

                    echo ""
                    echo "Azure CLI:"
                    az version

                    echo ""
                    echo "Git:"
                    git --version
                '''
            }
        }


        // =====================================================
        // 4. SONARQUBE - OPTIONAL
        // =====================================================
        stage('SonarQube Analysis') {
            steps {

                sh '''
                    echo "=========================================="
                    echo "SONARQUBE CHECK"
                    echo "=========================================="

                    if command -v sonar-scanner >/dev/null 2>&1; then

                        echo "sonar-scanner found."

                        sonar-scanner \
                            -Dsonar.projectKey=MLPython \
                            -Dsonar.projectName=MLPython \
                            -Dsonar.sources="Classification of Arrhythmia [ECG DATA]"

                    else

                        echo "sonar-scanner is not installed."
                        echo "Skipping SonarQube analysis."

                    fi
                '''
            }
        }


        // =====================================================
        // 5. CHECK ARRHYTHMIA PROJECT
        // =====================================================
        stage('Check Arrhythmia Project') {
            steps {

                sh '''
                    set -e

                    PROJECT="Classification of Arrhythmia [ECG DATA]"

                    echo "=========================================="
                    echo "CHECKING ARRHYTHMIA PROJECT"
                    echo "=========================================="

                    if [ ! -d "$PROJECT" ]; then
                        echo "ERROR: Arrhythmia project directory not found."
                        exit 1
                    fi

                    if [ ! -f "$PROJECT/Dockerfile" ]; then
                        echo "ERROR: Dockerfile not found."
                        exit 1
                    fi

                    if [ ! -f "$PROJECT/requirements.txt" ]; then
                        echo "WARNING: requirements.txt not found."
                    fi

                    echo ""
                    echo "Project:"
                    ls -la "$PROJECT"

                    echo ""
                    echo "Dockerfile:"
                    cat "$PROJECT/Dockerfile"
                '''
            }
        }


        // =====================================================
        // 6. BUILD ARRHYTHMIA DOCKER IMAGE
        // =====================================================
        stage('Build Arrhythmia Docker Image') {
            steps {

                sh '''
                    set -e

                    PROJECT="Classification of Arrhythmia [ECG DATA]"

                    echo "=========================================="
                    echo "BUILDING ARRHYTHMIA IMAGE"
                    echo "=========================================="

                    docker build \
                        -t ${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER} \
                        -t ${ARRHYTHMIA_IMAGE}:latest \
                        "$PROJECT"

                    echo ""
                    echo "=========================================="
                    echo "BUILT IMAGES"
                    echo "=========================================="

                    docker images "${ARRHYTHMIA_IMAGE}"
                '''
            }
        }


        // =====================================================
        // 7. TEST DOCKER IMAGE
        // =====================================================
        stage('Test Docker Image') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "TESTING DOCKER IMAGE"
                    echo "=========================================="

                    docker image inspect \
                        ${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER} \
                        >/dev/null

                    echo "Docker image exists successfully."

                    docker image inspect \
                        ${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER} \
                        --format='Image: {{.RepoTags}}'

                    docker image inspect \
                        ${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER} \
                        --format='Size: {{.Size}} bytes'
                '''
            }
        }


        // =====================================================
        // 8. DOCKER HUB LOGIN
        // =====================================================
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
                        set -e

                        echo "=========================================="
                        echo "DOCKER HUB LOGIN"
                        echo "=========================================="

                        echo "$DOCKER_PASS" | docker login \
                            --username "$DOCKER_USER" \
                            --password-stdin

                        echo "DockerHub login successful."
                    '''
                }
            }
        }


        // =====================================================
        // 9. PUSH DOCKER IMAGE
        // =====================================================
        stage('Push Image to DockerHub') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "PUSHING ARRHYTHMIA IMAGE"
                    echo "=========================================="

                    docker push \
                        ${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER}

                    docker push \
                        ${ARRHYTHMIA_IMAGE}:latest

                    echo ""
                    echo "Images pushed successfully:"
                    echo "${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER}"
                    echo "${ARRHYTHMIA_IMAGE}:latest"
                '''
            }
        }


        // =====================================================
        // 10. AZURE LOGIN
        // =====================================================
        stage('Azure Login') {
            steps {

                withCredentials([
                    string(
                        credentialsId: 'azure-service-principal',
                        variable: 'AZURE_CREDENTIALS'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "=========================================="
                        echo "AZURE LOGIN"
                        echo "=========================================="

                        CLIENT_ID=$(echo "$AZURE_CREDENTIALS" | \
                            python3 -c 'import sys,json; print(json.load(sys.stdin)["clientId"])')

                        CLIENT_SECRET=$(echo "$AZURE_CREDENTIALS" | \
                            python3 -c 'import sys,json; print(json.load(sys.stdin)["clientSecret"])')

                        TENANT_ID=$(echo "$AZURE_CREDENTIALS" | \
                            python3 -c 'import sys,json; print(json.load(sys.stdin)["tenantId"])')

                        SUBSCRIPTION_ID=$(echo "$AZURE_CREDENTIALS" | \
                            python3 -c 'import sys,json; print(json.load(sys.stdin)["subscriptionId"])')

                        az login \
                            --service-principal \
                            --username "$CLIENT_ID" \
                            --password "$CLIENT_SECRET" \
                            --tenant "$TENANT_ID" \
                            >/dev/null

                        az account set \
                            --subscription "$SUBSCRIPTION_ID"

                        echo ""
                        echo "Azure account:"
                        az account show \
                            --query "{Name:name,Subscription:id,Tenant:tenantId}" \
                            -o table
                    '''
                }
            }
        }


        // =====================================================
        // 11. CONNECT TO AKS
        // =====================================================
        stage('Connect to AKS') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "CONNECTING TO AKS"
                    echo "=========================================="

                    az aks get-credentials \
                        --resource-group "${AZ_RESOURCE_GROUP}" \
                        --name "${AKS_CLUSTER}" \
                        --overwrite-existing

                    echo ""
                    echo "AKS cluster:"
                    kubectl cluster-info

                    echo ""
                    echo "AKS nodes:"
                    kubectl get nodes -o wide
                '''
            }
        }


        // =====================================================
        // 12. CHECK KUBERNETES
        // =====================================================
        stage('Check Kubernetes Resources') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "KUBERNETES RESOURCES"
                    echo "=========================================="

                    echo ""
                    echo "Namespaces:"
                    kubectl get namespaces

                    echo ""
                    echo "Deployments:"
                    kubectl get deployments -A

                    echo ""
                    echo "Pods:"
                    kubectl get pods -A

                    echo ""
                    echo "Services:"
                    kubectl get svc -A

                    echo ""
                    echo "Kubernetes YAML files in repository:"
                    find . -type f \\( \
                        -name "*.yaml" -o \
                        -name "*.yml" \
                    \\) \
                    ! -path "./.git/*" \
                    | sort
                '''
            }
        }


        // =====================================================
        // 13. DEPLOY / UPDATE ARRHYTHMIA
        // =====================================================
        stage('Deploy Arrhythmia to AKS') {
            steps {

                sh '''
                    set -e

                    echo "=========================================="
                    echo "DEPLOYING ARRHYTHMIA TO AKS"
                    echo "=========================================="

                    echo ""
                    echo "Searching for Kubernetes manifests..."

                    YAML_FILES=$(find . -type f \\( \
                        -name "*.yaml" -o \
                        -name "*.yml" \
                    \\) \
                    ! -path "./.git/*")

                    if [ -z "$YAML_FILES" ]; then

                        echo ""
                        echo "No Kubernetes YAML files found."
                        echo "Skipping Kubernetes manifest deployment."

                    else

                        echo ""
                        echo "Kubernetes manifests found:"
                        echo "$YAML_FILES"

                        for FILE in $YAML_FILES
                        do
                            echo ""
                            echo "Applying: $FILE"
                            kubectl apply -f "$FILE"
                        done

                    fi
                '''
            }
        }


        // =====================================================
        // 14. UPDATE IMAGE IF DEPLOYMENT EXISTS
        // =====================================================
        stage('Update Running Image') {
            steps {

                sh '''
                    set +e

                    echo "=========================================="
                    echo "CHECKING ARRHYTHMIA DEPLOYMENT"
                    echo "=========================================="

                    DEPLOYMENT=$(kubectl get deployment \
                        -A \
                        -o jsonpath='{range .items[*]}{.metadata.namespace}{" "}{.metadata.name}{"\\n"}{end}' \
                        | grep -i arrhythmia \
                        | head -1)

                    if [ -z "$DEPLOYMENT" ]; then

                        echo "No deployment containing 'arrhythmia' found."
                        echo "Skipping kubectl set image."

                    else

                        NAMESPACE=$(echo "$DEPLOYMENT" | awk '{print $1}')
                        DEPLOYMENT_NAME=$(echo "$DEPLOYMENT" | awk '{print $2}')

                        echo "Namespace: $NAMESPACE"
                        echo "Deployment: $DEPLOYMENT_NAME"

                        CONTAINER=$(kubectl get deployment \
                            "$DEPLOYMENT_NAME" \
                            -n "$NAMESPACE" \
                            -o jsonpath='{.spec.template.spec.containers[0].name}')

                        echo "Container: $CONTAINER"

                        kubectl set image deployment/"$DEPLOYMENT_NAME" \
                            "$CONTAINER"="${ARRHYTHMIA_IMAGE}:${BUILD_NUMBER}" \
                            -n "$NAMESPACE"

                        echo ""
                        echo "Waiting for rollout..."

                        kubectl rollout status \
                            deployment/"$DEPLOYMENT_NAME" \
                            -n "$NAMESPACE" \
                            --timeout=300s

                    fi
                '''
            }
        }


        // =====================================================
        // 15. FINAL KUBERNETES VERIFICATION
        // =====================================================
        stage('Deployment Verification') {
            steps {

                sh '''
                    echo "=========================================="
                    echo "FINAL KUBERNETES STATUS"
                    echo "=========================================="

                    echo ""
                    echo "Deployments:"
                    kubectl get deployments -A -o wide

                    echo ""
                    echo "Pods:"
                    kubectl get pods -A -o wide

                    echo ""
                    echo "Services:"
                    kubectl get svc -A

                    echo ""
                    echo "All Kubernetes resources:"
                    kubectl get all -A
                '''
            }
        }
    }


    // =========================================================
    // POST ACTIONS
    // =========================================================

    post {

        success {

            echo '''
            ============================================
                    PIPELINE SUCCESSFUL
            ============================================

            GitHub checkout       : SUCCESS
            SonarQube             : OPTIONAL
            Docker build          : SUCCESS
            DockerHub push        : SUCCESS
            Azure login           : SUCCESS
            AKS connection        : SUCCESS
            Kubernetes deployment : SUCCESS

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
                echo "=========================================="
                echo "CLEANUP"
                echo "=========================================="

                docker logout || true

                echo ""
                echo "Docker images:"
                docker images | head -20 || true
            '''
        }
    }
}
