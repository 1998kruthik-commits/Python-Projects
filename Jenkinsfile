pipeline {

    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {

        PATH = "/usr/local/bin:/usr/bin:/bin:${env.PATH}"

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        DOCKER_REPO = "kruthikchethu"

        // Jenkins build number = Docker image version
        BUILD_TAG = "${BUILD_NUMBER}"

        // Example:
        // kruthikchethu/medical-chatbot:25
        // kruthikchethu/arrhythmia:25
        MEDICAL_IMAGE = "${DOCKER_REPO}/medical-chatbot:${BUILD_NUMBER}"
        ARR_IMAGE     = "${DOCKER_REPO}/arrhythmia:${BUILD_NUMBER}"

        RESOURCE_GROUP = "MLPython3418"
        AKS_NAME       = "myakcluster"

        KEY_VAULT_NAME = "myakcluster"

        SUBSCRIPTION_ID = "f22a3c52-9826-4dbd-ba61-5c0e118462b4"
    }


    stages {

        // ============================================================
        // CHECKOUT
        // ============================================================

        stage('Checkout Code') {

            steps {

                echo "========================================"
                echo "CHECKING OUT SOURCE CODE"
                echo "========================================"

                checkout scm

                sh '''
                    set -e

                    echo "Current directory:"
                    pwd

                    echo ""
                    echo "Git commit:"
                    git rev-parse --short HEAD

                    echo ""
                    echo "Git branch:"
                    git branch --show-current || true

                    echo ""
                    echo "Workspace:"
                    ls -la
                '''
            }
        }


        // ============================================================
        // WORKSPACE INFORMATION
        // ============================================================

        stage('Workspace Info') {

            steps {

                sh '''
                    echo "========================================"
                    echo "WORKSPACE INFORMATION"
                    echo "========================================"

                    pwd

                    echo ""
                    echo "Files:"
                    ls -la

                    echo ""
                    echo "========================================"
                    echo "KUBECTL"
                    echo "========================================"

                    which kubectl || true
                    kubectl version --client || true

                    echo ""
                    echo "========================================"
                    echo "AZURE CLI"
                    echo "========================================"

                    which az || true
                    az version || true

                    echo ""
                    echo "========================================"
                    echo "DOCKER"
                    echo "========================================"

                    which docker || true
                    docker --version || true

                    echo ""
                    echo "========================================"
                    echo "KUBELOGIN"
                    echo "========================================"

                    which kubelogin || true
                    kubelogin --version || true
                '''
            }
        }


        // ============================================================
        // SONARQUBE
        // ============================================================

        stage('SonarQube Analysis') {

            steps {

                script {

                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('mypython') {

                        sh """

                            echo "========================================"
                            echo "SONARQUBE ANALYSIS"
                            echo "========================================"

                            echo "SonarQube URL:"
                            echo "\$SONAR_HOST_URL"

                            echo ""
                            echo "Testing SonarQube connectivity..."

                            curl -f --connect-timeout 10 \\
                                "\$SONAR_HOST_URL/api/server/version"

                            echo ""
                            echo "SonarQube is reachable."

                            echo ""
                            echo "Starting SonarScanner..."

                            ${scannerHome}/bin/sonar-scanner \\
                                -Dsonar.projectKey=PythonProjects \\
                                -Dsonar.projectName=PythonProjects \\
                                -Dsonar.sources=. \\
                                -Dsonar.sourceEncoding=UTF-8 \\
                                -Dsonar.python.version=3.12
                        """
                    }
                }
            }
        }


        // ============================================================
        // QUALITY GATE
        // ============================================================

        stage('Quality Gate') {

            steps {

                timeout(time: 15, unit: 'MINUTES') {

                    waitForQualityGate abortPipeline: true 
                }
            }
        }


        // ============================================================
        // AZURE KEY VAULT
        // ============================================================

        stage('Fetch Secrets from Azure Key Vault') {

            steps {

                withAzureKeyvault(

                    credentialIDOverride: 'azure-sp-jenkins',

                    keyVaultURLOverride:
                        'https://mlpythonproject1.vault.azure.net/',

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

                            echo "ERROR:"
                            echo "Azure Storage connection string was not loaded."

                            exit 1
                        fi

                        echo "Azure Key Vault secret loaded successfully."
                    '''
                }
            }
        }


        // ============================================================
        // BUILD DOCKER IMAGES
        // ============================================================

        stage('Build Docker Images') {

            parallel {

                // ----------------------------------------------------
                // MEDICAL CHATBOT
                // ----------------------------------------------------

                stage('Medical Chatbot') {

                    steps {

                        dir('medical-chatbot') {

                            sh '''

                                set -e

                                echo "========================================"
                                echo "BUILDING MEDICAL CHATBOT"
                                echo "========================================"

                                echo "Docker image:"
                                echo "$MEDICAL_IMAGE"

                                docker build \
                                    -t "$MEDICAL_IMAGE" \
                                    .

                                echo ""
                                echo "Medical Chatbot image built successfully."

                                echo ""
                                echo "Checking image:"

                                docker images | grep medical-chatbot || true
                            '''
                        }
                    }
                }


                // ----------------------------------------------------
                // ARRHYTHMIA
                // ----------------------------------------------------

                stage('Arrhythmia') {

                    steps {

                        dir('Classification of Arrhythmia [ECG DATA]') {

                            sh '''

                                set -e

                                echo "========================================"
                                echo "BUILDING ARRHYTHMIA"
                                echo "========================================"

                                echo "Docker image:"
                                echo "$ARR_IMAGE"

                                docker build \
                                    -t "$ARR_IMAGE" \
                                    .

                                echo ""
                                echo "Arrhythmia image built successfully."

                                echo ""
                                echo "Checking image:"

                                docker images | grep arrhythmia || true
                            '''
                        }
                    }
                }
            }
        }


        // ============================================================
        // DOCKER HUB
        // ============================================================

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

                        set -e

                        echo "========================================"
                        echo "DOCKER HUB LOGIN"
                        echo "========================================"

                        echo "$DOCKER_PASS" | \
                            docker login \
                            -u "$DOCKER_USER" \
                            --password-stdin

                        echo ""
                        echo "Docker login successful."


                        echo ""
                        echo "========================================"
                        echo "PUSHING MEDICAL CHATBOT"
                        echo "========================================"

                        echo "Image:"
                        echo "$MEDICAL_IMAGE"

                        docker push "$MEDICAL_IMAGE"


                        echo ""
                        echo "========================================"
                        echo "PUSHING ARRHYTHMIA"
                        echo "========================================"

                        echo "Image:"
                        echo "$ARR_IMAGE"

                        docker push "$ARR_IMAGE"


                        echo ""
                        echo "========================================"
                        echo "DOCKER IMAGES PUSHED SUCCESSFULLY"
                        echo "========================================"

                        echo ""
                        echo "Medical Chatbot:"
                        echo "$MEDICAL_IMAGE"

                        echo ""
                        echo "Arrhythmia:"
                        echo "$ARR_IMAGE"


                        docker logout || true
                    '''
                }
            }
        }


        // ============================================================
        // UPDATE KUBERNETES MANIFESTS
        // ============================================================

        stage('Update Kubernetes Manifests') {

            steps {

                sh '''

                    set -e

                    echo "========================================"
                    echo "UPDATING KUBERNETES MANIFESTS"
                    echo "========================================"

                    echo ""
                    echo "Medical image:"
                    echo "$MEDICAL_IMAGE"

                    echo ""
                    echo "Arrhythmia image:"
                    echo "$ARR_IMAGE"


                    echo ""
                    echo "Updating Medical Chatbot manifest..."

                    sed -i \
                        "s|image: .*medical-chatbot.*|image: ${MEDICAL_IMAGE}|g" \
                        k8s/medical-chatbot-deployment.yaml


                    echo ""
                    echo "Updating Arrhythmia manifest..."

                    sed -i \
                        "s|image: .*arrhythmia.*|image: ${ARR_IMAGE}|g" \
                        k8s/arrhythmia-deployment.yml


                    echo ""
                    echo "========================================"
                    echo "UPDATED IMAGES"
                    echo "========================================"


                    echo ""
                    echo "Medical Chatbot:"

                    grep "image:" \
                        k8s/medical-chatbot-deployment.yaml


                    echo ""
                    echo "Arrhythmia:"

                    grep "image:" \
                        k8s/arrhythmia-deployment.yml
                '''
            }
        }


        // ============================================================
        // AZURE LOGIN
        // ============================================================

        stage('Login to Azure') {

            steps {

                withCredentials([

                    azureServicePrincipal(
                        'azure-sp-jenkins'
                    ),

                    string(
                        credentialsId: 'azure-tenant-id',
                        variable: 'AZURE_TENANT_ID'
                    )

                ]) {

                    sh '''

                        set -e

                        echo "========================================"
                        echo "AZURE LOGIN"
                        echo "========================================"

                        az login \
                            --service-principal \
                            --username "$AZURE_CLIENT_ID" \
                            --password "$AZURE_CLIENT_SECRET" \
                            --tenant "$AZURE_TENANT_ID" \
                            --output none


                        echo "Azure login successful."


                        echo ""
                        echo "Setting subscription..."

                        az account set \
                            --subscription "$SUBSCRIPTION_ID"


                        echo ""
                        echo "Current Azure account:"

                        az account show \
                            --output table
                    '''
                }
            }
        }


        // ============================================================
        // PREPARE AKS TOOLS
        // ============================================================

        stage('Prepare AKS Tools') {

            steps {

                sh '''

                    set -e

                    echo "========================================"
                    echo "PREPARING AKS TOOLS"
                    echo "========================================"


                    mkdir -p "$HOME/.local/bin"
                    mkdir -p "$HOME/.kube"


                    echo ""
                    echo "Installing kubectl and kubelogin if required..."

                    az aks install-cli \
                        --install-location "$HOME/.local/bin/kubectl" \
                        --kubelogin-install-location "$HOME/.local/bin/kubelogin" \
                        || true


                    export PATH="$HOME/.local/bin:$PATH"


                    echo ""
                    echo "kubectl:"

                    which kubectl || true

                    kubectl version --client || true


                    echo ""
                    echo "kubelogin:"

                    which kubelogin || true

                    kubelogin --version || true


                    if ! command -v kubelogin >/dev/null 2>&1; then

                        echo ""
                        echo "ERROR: kubelogin is not installed or not in PATH."

                        find "$HOME" \
                            -name kubelogin \
                            -type f \
                            2>/dev/null || true

                        exit 1
                    fi


                    echo ""
                    echo "AKS tools are ready."
                '''
            }
        }


        // ============================================================
        // AKS CREDENTIALS
        // ============================================================

        stage('Get & Verify AKS Credentials') {

            steps {

                sh '''

                    set -e

                    export PATH="$HOME/.local/bin:$PATH"

                    echo "========================================"
                    echo "GETTING AKS CREDENTIALS"
                    echo "========================================"


                    echo "Jenkins user:"
                    whoami


                    echo ""
                    echo "HOME:"
                    echo "$HOME"


                    echo ""
                    echo "Resource Group:"
                    echo "$RESOURCE_GROUP"


                    echo ""
                    echo "AKS Cluster:"
                    echo "$AKS_NAME"


                    mkdir -p "$HOME/.kube"

                    export KUBECONFIG="$HOME/.kube/config"


                    echo ""
                    echo "Getting AKS credentials..."


                    az aks get-credentials \
                        --resource-group "$RESOURCE_GROUP" \
                        --name "$AKS_NAME" \
                        --subscription "$SUBSCRIPTION_ID" \
                        --overwrite-existing


                    echo ""
                    echo "AKS credentials obtained successfully."


                    echo ""
                    echo "Kubeconfig:"

                    ls -l "$KUBECONFIG"


                    echo ""
                    echo "Current Kubernetes context:"

                    kubectl config current-context


                    echo ""
                    echo "Kubernetes contexts:"

                    kubectl config get-contexts


                    echo ""
                    echo "Converting kubeconfig for Azure CLI authentication..."


                    kubelogin convert-kubeconfig \
                        -l azurecli


                    echo ""
                    echo "Testing AKS connection..."


                    kubectl get nodes


                    echo ""
                    echo "AKS connection successful."
                '''
            }
        }


        // ============================================================
        // DEPLOY TO AKS
        // ============================================================

        stage('Deploy & Verify AKS') {

            steps {

                sh '''

                    set -e

                    export PATH="$HOME/.local/bin:$PATH"
                    export KUBECONFIG="$HOME/.kube/config"


                    echo "========================================"
                    echo "DEPLOYING TO AKS"
                    echo "========================================"


                    echo ""
                    echo "Deploying Medical Chatbot image:"

                    echo "$MEDICAL_IMAGE"


                    echo ""
                    echo "Deploying Arrhythmia image:"

                    echo "$ARR_IMAGE"


                    echo ""
                    echo "Applying Medical Chatbot deployment..."

                    kubectl apply \
                        -f k8s/medical-chatbot-deployment.yaml


                    echo ""
                    echo "Applying Arrhythmia deployment..."

                    kubectl apply \
                        -f k8s/arrhythmia-deployment.yml


                    echo ""
                    echo "Waiting for Medical Chatbot rollout..."

                    kubectl rollout status \
                        deployment/medical-chatbot \
                        --timeout=180s


                    echo ""
                    echo "Waiting for Arrhythmia rollout..."

                    kubectl rollout status \
                        deployment/arrhythmia \
                        --timeout=180s


                    echo ""
                    echo "========================================"
                    echo "DEPLOYMENT STATUS"
                    echo "========================================"


                    kubectl get deployments


                    echo ""
                    echo "Pods:"

                    kubectl get pods


                    echo ""
                    echo "Services:"

                    kubectl get svc
                '''
            }
        }


        // ============================================================
        // AKS HEALTH CHECK
        // ============================================================

        stage('AKS Health Check') {

            steps {

                sh '''

                    set -e

                    export PATH="$HOME/.local/bin:$PATH"
                    export KUBECONFIG="$HOME/.kube/config"


                    echo "========================================"
                    echo "AKS SERVICES"
                    echo "========================================"


                    kubectl get svc


                    # ------------------------------------------------
                    # MEDICAL CHATBOT
                    # ------------------------------------------------

                    echo ""
                    echo "========================================"
                    echo "WAITING FOR MEDICAL CHATBOT EXTERNAL IP"
                    echo "========================================"


                    MEDICAL_IP=""


                    for i in $(seq 1 30); do

                        MEDICAL_IP=$(kubectl get svc medical-chatbot-service \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
                            2>/dev/null || true)


                        if [ -n "$MEDICAL_IP" ]; then

                            echo ""
                            echo "Medical Chatbot External IP:"
                            echo "$MEDICAL_IP"

                            break
                        fi


                        echo "Attempt $i/30 - Medical Chatbot External IP not ready..."

                        sleep 10

                    done


                    if [ -z "$MEDICAL_IP" ]; then

                        echo ""
                        echo "ERROR:"
                        echo "Medical Chatbot External IP was not assigned."


                        kubectl get svc medical-chatbot-service || true

                        kubectl describe svc medical-chatbot-service || true

                        exit 1
                    fi


                    # ------------------------------------------------
                    # ARRHYTHMIA
                    # ------------------------------------------------

                    echo ""
                    echo "========================================"
                    echo "WAITING FOR ARRHYTHMIA EXTERNAL IP"
                    echo "========================================"


                    ARRHYTHMIA_IP=""


                    for i in $(seq 1 30); do

                        ARRHYTHMIA_IP=$(kubectl get svc arrhythmia-service \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
                            2>/dev/null || true)


                        if [ -n "$ARRHYTHMIA_IP" ]; then

                            echo ""
                            echo "Arrhythmia External IP:"
                            echo "$ARRHYTHMIA_IP"

                            break
                        fi


                        echo "Attempt $i/30 - Arrhythmia External IP not ready..."

                        sleep 10

                    done


                    if [ -z "$ARRHYTHMIA_IP" ]; then

                        echo ""
                        echo "ERROR:"
                        echo "Arrhythmia External IP was not assigned."


                        kubectl get svc arrhythmia-service || true

                        kubectl describe svc arrhythmia-service || true

                        exit 1
                    fi


                    # ------------------------------------------------
                    # FINAL URLS
                    # ------------------------------------------------

                    echo ""
                    echo "========================================"
                    echo "APPLICATION URLS"
                    echo "========================================"


                    echo ""
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


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {

            echo "========================================"
            echo "PIPELINE COMPLETED SUCCESSFULLY"
            echo "========================================"

            echo "Medical Image: ${MEDICAL_IMAGE}"
            echo "Arrhythmia Image: ${ARR_IMAGE}"

            sh '''

                export PATH="$HOME/.local/bin:$PATH"
                export KUBECONFIG="$HOME/.kube/config"

                echo ""
                echo "Final AKS Status:"

                kubectl get deployments || true

                kubectl get pods || true

                kubectl get svc || true
            '''
        }


        failure {

            echo "========================================"
            echo "PIPELINE FAILED"
            echo "========================================"

            sh '''

                export PATH="$HOME/.local/bin:$PATH"
                export KUBECONFIG="$HOME/.kube/config"

                echo "Collecting diagnostics..."


                if [ -f "$HOME/.kube/config" ]; then

                    echo "Kubeconfig exists."


                    echo ""
                    echo "Current context:"

                    kubectl config current-context || true


                    echo ""
                    echo "Nodes:"

                    kubectl get nodes || true


                    echo ""
                    echo "Deployments:"

                    kubectl get deployments || true


                    echo ""
                    echo "Pods:"

                    kubectl get pods -o wide || true


                    echo ""
                    echo "Services:"

                    kubectl get svc || true

                else

                    echo "No kubeconfig found."

                    echo "AKS credentials were probably never configured."

                fi
            '''
        }


        always {

            echo "Cleaning Jenkins workspace..."

            cleanWs()
        }
    }
}
