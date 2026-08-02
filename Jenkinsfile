pipeline {

    agent any

    environment {

        GIT_URL = "https://github.com/1998kruthik-commits/Python-Projects.git"

        MEDICAL_IMAGE = "kruthikchethu/medical-chatbot:v1"

        ARR_IMAGE = "kruthikchethu/arrhythmia:v1"

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

        stage('Build Medical Chatbot') {

            steps {

                dir('medical-chatbot') {

                    sh '''
                    docker build -t ${MEDICAL_IMAGE} .
                    '''

                }

            }

        }

        stage('Build Arrhythmia') {

            steps {

                dir('Classification of Arrhythmia [ECG DATA]') {

                    sh '''
                    docker build -t ${ARR_IMAGE} .
                    '''

                }

            }

        }

        stage('Docker Login') {

            steps {

                sh '''
                echo ${DOCKER_CREDS_PSW} | docker login -u ${DOCKER_CREDS_USR} --password-stdin
                '''

            }

        }

        stage('Push Images') {

            steps {

                sh '''
                docker push ${MEDICAL_IMAGE}

                docker push ${ARR_IMAGE}
                '''

            }

        }

        stage('Cleanup') {

            steps {

                sh '''
                docker logout

                docker image prune -f
                '''

            }

        }

    }

}
