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

        RESOURCE_GROUP = "MLPython3418"
        AKS_NAME = "myakcluster"

        SUBSCRIPTION_ID = "f22a3c52-9826-4dbd-ba61-5c0e118462b4"
    }

    stages {

        // ============================================================
        // 1. CHECKOUT
        // ============================================================

        stage('Checkout') {

            steps {

                echo "========================================"
                echo "CHECKING OUT SOURCE CODE"
                echo "========================================"

                checkout scm

                sh '''
                    set -e

                    echo "Workspace:"
                    pwd

                    echo ""
                    echo "Git commit:"
                    git rev-parse --short HEAD

                    echo ""
                    echo "Git branch:"
                    git branch --show-current || true

                    echo ""
                    echo "Workspace files:"
                    ls -la
                '''
            }
        }


        // ============================================================
        // 2. SONARQUBE + QUALITY GATE
        // ============================================================

        stage('SonarQube & Quality Gate') {

            steps {

                script {

                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('mypython') {

                        sh """

                            set -e

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
                            echo "Running SonarScanner..."

                            ${scannerHome}/bin/sonar-scanner \\
                                -Dsonar.projectKey=PythonProjects \\
                                -Dsonar.projectName=PythonProjects \\
                                -Dsonar.sources=. \\
                                -Dsonar.sourceEncoding=UTF-8 \\
                                -Dsonar.python.version=3.12
                        """
                    }

                    echo ""
                    echo "========================================"
                    echo "SONARQUBE QUALITY GATE"
                    echo "========================================"

                    timeout(time: 15, unit: 'MINUTES') {

                        def qg = waitForQualityGate(
                            abortPipeline: false
                        )

                        echo "Quality Gate Status: ${qg.status}"

                        if (qg.status != 'OK') {

                            echo "WARNING: SonarQube Quality Gate did not pass."
                            echo "WARNING: Issues were detected."
                            echo "WARNING: Continuing pipeline as configured."

                        } else {

                            echo "SUCCESS: SonarQube Quality Gate passed."
                        }
                    }
                }
            }
        }


        // ============================================================
        // 3. AZURE + AKS SETUP
        // ============================================================

        stage('Azure & AKS Setup') {

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
                        echo "Setting Azure subscription..."

                        az account set \
                            --subscription "$SUBSCRIPTION_ID"


                        echo ""
                        echo "Current Azure account:"

                        az account show -o table


                        # ==================================================
                        # AKS TOOLS
                        # ==================================================

                        echo ""
                        echo "========================================"
                        echo "PREPARING AKS TOOLS"
                        echo "========================================"

                        mkdir -p "$HOME/.local/bin"
                        mkdir -p "$HOME/.kube"

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

                            echo "ERROR: kubelogin is not available."

                            exit 1

                        fi


                        # ==================================================
                        # AKS CREDENTIALS
                        # ==================================================

                        echo ""
                        echo "========================================"
                        echo "GETTING AKS CREDENTIALS"
                        echo "========================================"

                        export KUBECONFIG="$HOME/.kube/config"

                        az aks get-credentials \
                            --resource-group "$RESOURCE_GROUP" \
                            --name "$AKS_NAME" \
                            --subscription "$SUBSCRIPTION_ID" \
                            --overwrite-existing

                        echo ""
                        echo "AKS credentials obtained successfully."


                        echo ""
                        echo "Converting kubeconfig..."

                        kubelogin convert-kubeconfig -l azurecli


                        echo ""
                        echo "Current Kubernetes context:"

                        kubectl config current-context


                        echo ""
                        echo "Testing AKS connection..."

                        kubectl get nodes


                        echo ""
                        echo "AKS connection successful."
                    '''
                }
            }
        }


        // ============================================================
        // 4. BUILD DOCKER IMAGES
        // ============================================================

        stage('Build Docker Images') {

    steps {

        script {

            // ================================================
            // AUTOMATIC DOCKER VERSION
            // Jenkins #18 -> 0.1
            // Jenkins #19 -> 0.2
            // Jenkins #20 -> 0.3
            // ================================================

            def minorVersion = BUILD_NUMBER.toInteger() - 17

            if (minorVersion < 1) {
                minorVersion = 1
            }

            env.IMAGE_VERSION = "0.${minorVersion}"

            env.MEDICAL_IMAGE =
                "${DOCKER_REPO}/medical-chatbot:${IMAGE_VERSION}"

            env.ARR_IMAGE =
                "${DOCKER_REPO}/arrhythmia:${IMAGE_VERSION}"


            echo "========================================"
            echo "DOCKER VERSION"
            echo "========================================"

            echo "Jenkins Build : ${BUILD_NUMBER}"
            echo "Docker Version: ${IMAGE_VERSION}"

            echo ""
            echo "Medical Image:"
            echo "${MEDICAL_IMAGE}"

            echo ""
            echo "Arrhythmia Image:"
            echo "${ARR_IMAGE}"


            // ================================================
            // BUILD MEDICAL CHATBOT
            // ================================================

            dir('medical-chatbot') {

                sh '''
                    set -e

                    echo ""
                    echo "========================================"
                    echo "BUILDING MEDICAL CHATBOT"
                    echo "========================================"

                    echo "Image:"
                    echo "$MEDICAL_IMAGE"

                    docker build \
                        -t "$MEDICAL_IMAGE" \
                        .

                    echo ""
                    echo "Medical Chatbot image built successfully."

                    docker images "$MEDICAL_IMAGE"
                '''
            }


            // ================================================
            // BUILD ARRHYTHMIA
            // ================================================

            dir('Classification of Arrhythmia [ECG DATA]') {

                sh '''
                    set -e

                    echo ""
                    echo "========================================"
                    echo "BUILDING ARRHYTHMIA"
                    echo "========================================"

                    echo "Image:"
                    echo "$ARR_IMAGE"

                    docker build \
                        -t "$ARR_IMAGE" \
                        .

                    echo ""
                    echo "Arrhythmia image built successfully."

                    docker images "$ARR_IMAGE"
                '''
            }


            echo ""
            echo "========================================"
            echo "BOTH DOCKER IMAGES BUILT"
            echo "========================================"

            echo "Medical Chatbot:"
            echo "${MEDICAL_IMAGE}"

            echo ""
            echo "Arrhythmia:"
            echo "${ARR_IMAGE}"
        }
    }
}


                    // ==================================================
                    // ARRHYTHMIA
                    // ==================================================

                    stage('Arrhythmia Image') {

                        steps {

                            dir('Classification of Arrhythmia [ECG DATA]') {

                                sh '''

                                    set -e

                                    echo "========================================"
                                    echo "BUILDING ARRHYTHMIA"
                                    echo "========================================"

                                    echo "Image:"
                                    echo "$ARR_IMAGE"


                                    docker build \
                                        -t "$ARR_IMAGE" \
                                        .


                                    echo ""
                                    echo "Arrhythmia image built successfully."


                                    echo ""
                                    echo "Docker image:"

                                    docker images "$ARR_IMAGE"
                                '''
                            }
                        }
                    }
                }
            }
        }


        // ============================================================
        // 5. PUSH IMAGES + UPDATE KUBERNETES MANIFESTS
        // ============================================================

        stage('Push Images & Update Manifests') {

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

                        echo "$MEDICAL_IMAGE"

                        docker push "$MEDICAL_IMAGE"


                        echo ""
                        echo "========================================"
                        echo "PUSHING ARRHYTHMIA"
                        echo "========================================"

                        echo "$ARR_IMAGE"

                        docker push "$ARR_IMAGE"


                        docker logout || true


                        # ==================================================
                        # UPDATE KUBERNETES
                        # ==================================================

                        echo ""
                        echo "========================================"
                        echo "UPDATING KUBERNETES MANIFESTS"
                        echo "========================================"


                        echo ""
                        echo "Medical image:"
                        echo "$MEDICAL_IMAGE"


                        echo ""
                        echo "Arrhythmia image:"
                        echo "$ARR_IMAGE"


                        sed -i \
                            "s|image: .*medical-chatbot.*|image: ${MEDICAL_IMAGE}|g" \
                            k8s/medical-chatbot-deployment.yaml


                        sed -i \
                            "s|image: .*arrhythmia.*|image: ${ARR_IMAGE}|g" \
                            k8s/arrhythmia-deployment.yml


                        echo ""
                        echo "========================================"
                        echo "UPDATED KUBERNETES IMAGES"
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
        }


        // ============================================================
        // 6. DEPLOY TO AKS
        // ============================================================

        stage('Deploy to AKS') {

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

                        set -e

                        export PATH="$HOME/.local/bin:$PATH"
                        export KUBECONFIG="$HOME/.kube/config"


                        echo "========================================"
                        echo "AZURE KEY VAULT"
                        echo "========================================"


                        if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then

                            echo "ERROR:"
                            echo "Azure Storage connection string was not loaded."

                            exit 1

                        fi


                        echo "Azure Key Vault secret loaded successfully."


                        echo ""
                        echo "========================================"
                        echo "DEPLOYING TO AKS"
                        echo "========================================"


                        echo ""
                        echo "Medical Image:"
                        echo "$MEDICAL_IMAGE"


                        echo ""
                        echo "Arrhythmia Image:"
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


                        echo ""
                        echo "Deployments:"

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
        }


        // ============================================================
        // 7. VERIFY AKS + GET APPLICATION URLS
        // ============================================================

        stage('Verify AKS & Get URLs') {

            steps {

                sh '''

                    set -e

                    export PATH="$HOME/.local/bin:$PATH"
                    export KUBECONFIG="$HOME/.kube/config"


                    echo "========================================"
                    echo "AKS HEALTH CHECK"
                    echo "========================================"


                    echo ""
                    echo "Deployments:"

                    kubectl get deployments


                    echo ""
                    echo "Pods:"

                    kubectl get pods


                    echo ""
                    echo "Services:"

                    kubectl get svc


                    # ==================================================
                    # MEDICAL CHATBOT
                    # ==================================================

                    echo ""
                    echo "========================================"
                    echo "MEDICAL CHATBOT EXTERNAL IP"
                    echo "========================================"


                    MEDICAL_IP=""


                    for i in $(seq 1 30); do

                        MEDICAL_IP=$(kubectl get svc medical-chatbot-service \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
                            2>/dev/null || true)


                        if [ -n "$MEDICAL_IP" ]; then

                            break

                        fi


                        echo "Attempt $i/30 - waiting for External IP..."

                        sleep 10

                    done


                    if [ -z "$MEDICAL_IP" ]; then

                        echo ""
                        echo "ERROR: Medical Chatbot External IP was not assigned."

                        kubectl get svc medical-chatbot-service || true

                        kubectl describe svc medical-chatbot-service || true

                        exit 1

                    fi


                    # ==================================================
                    # ARRHYTHMIA
                    # ==================================================

                    echo ""
                    echo "========================================"
                    echo "ARRHYTHMIA EXTERNAL IP"
                    echo "========================================"


                    ARRHYTHMIA_IP=""


                    for i in $(seq 1 30); do

                        ARRHYTHMIA_IP=$(kubectl get svc arrhythmia-service \
                            -o jsonpath='{.status.loadBalancer.ingress[0].ip}' \
                            2>/dev/null || true)


                        if [ -n "$ARRHYTHMIA_IP" ]; then

                            break

                        fi


                        echo "Attempt $i/30 - waiting for External IP..."

                        sleep 10

                    done


                    if [ -z "$ARRHYTHMIA_IP" ]; then

                        echo ""
                        echo "ERROR: Arrhythmia External IP was not assigned."

                        kubectl get svc arrhythmia-service || true

                        kubectl describe svc arrhythmia-service || true

                        exit 1

                    fi


                    # ==================================================
                    # FINAL APPLICATION URLS
                    # ==================================================

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

            echo "Jenkins Build : ${BUILD_NUMBER}"
            echo "Docker Version: ${IMAGE_VERSION}"
            echo "Medical Image : ${MEDICAL_IMAGE}"
            echo "Arrhythmia    : ${ARR_IMAGE}"


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


                echo "Collecting AKS diagnostics..."


                if [ -f "$HOME/.kube/config" ]; then

                    echo ""
                    echo "Current Kubernetes context:"

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

                    echo "Kubeconfig not found."

                fi
            '''
        }


        always {

            echo "Cleaning Jenkins workspace..."

            cleanWs()
        }
    }
}
