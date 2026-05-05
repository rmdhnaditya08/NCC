pipeline {
    agent any                           // Pipeline dijalankan di agent manapun

    environment {                       // Variabel lingkungan
        APP_ENV    = 'staging'
        APP_NAME   = 'deploy-app'
        DOCKER_USER = 'rmdhnaditya08'
    }

    stages {

        stage('Checkout') {             // Ambil kode dari repository
            steps {
                echo 'Mengambil source code dari GitHub...'
                checkout scm
            }
        }

        stage('Build') {                // Install dependencies Python
            steps {
                echo 'Menginstall dependencies...'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {                 // Jalankan pengujian
            steps {
                echo 'Menjalankan unit test...'
                sh 'pytest tests/ -v'
            }
        }

        stage('Docker Build & Push') {  // Build image dan push ke Docker Hub
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

        stage('Deploy') {               // Deployment — jalankan container
            steps {
                echo "Deploy ke environment: ${APP_ENV}..."
                sh '''
                    docker stop deploy-app || true
                    docker rm   deploy-app || true
                    docker run -d \
                        --name deploy-app \
                        -p 5000:5000 \
                        rmdhnaditya08/deploy-app:latest
                '''
            }
        }
    }

    post {                              // Aksi setelah pipeline selesai
        always  { echo 'Pipeline selesai' }
        success { echo 'Pipeline berhasil!' }
        failure { echo 'Pipeline gagal!' }
    }
}
