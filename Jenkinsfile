pipeline {

    agent any

    environment {

        DOCKER_USER = "kruthikchethu"

    }

    stages {

        stage('Checkout') {

            steps {

                git branch: 'main',
                url: 'https://github.com/1998kruthik-commits/Python-Projects.git'

            }

        }

        stage('Build Medical Chatbot') {

            steps {

                dir('medical-chatbot') {

                    sh '''
                    docker build \
                    -t $DOCKER_USER/medical-chatbot:v1 .
                    '''

                }

            }

        }

        stage('Build Arrhythmia') {

            steps {

                dir('Classification of Arrhythmia [ECG DATA]') {

                    sh '''
                    docker build \
                    -t $DOCKER_USER/medical-chatbot:v2 .
                    '''

                }

            }

        }

        stage('Push Images') {

            steps {

                withCredentials([usernamePassword(

                    credentialsId: 'dockerhub',

                    usernameVariable: 'USERNAME',

                    passwordVariable: 'PASSWORD'

                )]) {

                    sh '''

                    echo "$PASSWORD" | docker login \
                    -u "$USERNAME" --password-stdin

                    docker push $DOCKER_USER/medical-chatbot:v1

                    docker push $DOCKER_USER/medical-chatbot:v2

                    docker logout

                    '''

                }

            }

        }

    }

}
