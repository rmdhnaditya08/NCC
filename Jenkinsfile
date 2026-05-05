pipeline {
    agent any

    environment {
        APP_ENV    = 'staging'
        APP_NAME   = 'deploy-app'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Mengambil source code dari GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            agent {
                docker { image 'python:3.11-slim'   // Pakai container Python
                         reuseNode true }
            }
            steps {
                echo 'Menginstall dependencies...'
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Test') {
            agent {
                docker { image 'python:3.11-slim'
                         reuseNode true }
            }
            steps {
                echo 'Menjalankan unit test...'
                sh '''
                    pip install --no-cache-dir pytest -q
                    pytest tests/ -v
                '''
            }
        }

        stage('Docker Build & Push') {
            steps {
                echo 'Build dan push Docker image...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        docker build -t rmdhnaditya08/deploy-app:latest .
                        echo $DOCKER_PASS | docker login -u rmdhnaditya08 --password-stdin
                        docker push rmdhnaditya08/deploy-app:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploy ke environment: ${APP_ENV}..."
                sh '''
                    docker stop deploy-app || true
                    docker rm   deploy-app || true
                    docker run -d \
                        --name deploy-app \
                        -p 5000:5000 \
                        rmdhnaditya08/deploy-app:latest
                    echo "Container berhasil dijalankan!"
                '''
            }
        }
    }

    post {
        always  { echo 'Pipeline selesai' }
        success { echo 'Pipeline berhasil!' }
        failure { echo 'Pipeline gagal!' }
    }
}pipeline {
    agent any

    environment {
        APP_ENV    = 'staging'
        APP_NAME   = 'deploy-app'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Mengambil source code dari GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            agent {
                docker { image 'python:3.11-slim'   // Pakai container Python
                         reuseNode true }
            }
            steps {
                echo 'Menginstall dependencies...'
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Test') {
            agent {
                docker { image 'python:3.11-slim'
                         reuseNode true }
            }
            steps {
                echo 'Menjalankan unit test...'
                sh '''
                    pip install --no-cache-dir pytest -q
                    pytest tests/ -v
                '''
            }
        }

        stage('Docker Build & Push') {
            steps {
                echo 'Build dan push Docker image...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        docker build -t rmdhnaditya08/deploy-app:latest .
                        echo $DOCKER_PASS | docker login -u rmdhnaditya08 --password-stdin
                        docker push rmdhnaditya08/deploy-app:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploy ke environment: ${APP_ENV}..."
                sh '''
                    docker stop deploy-app || true
                    docker rm   deploy-app || true
                    docker run -d \
                        --name deploy-app \
                        -p 5000:5000 \
                        rmdhnaditya08/deploy-app:latest
                    echo "Container berhasil dijalankan!"
                '''
            }
        }
    }

    post {
        always  { echo 'Pipeline selesai' }
        success { echo 'Pipeline berhasil!' }
        failure { echo 'Pipeline gagal!' }
    }
}
