pipeline {
    agent any

    environment {
        APP_ENV    = 'staging'
        APP_NAME   = 'deploy-app'
        DOCKER_USER = 'rmdhnaditya08'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Mengambil source code dari GitHub...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Menginstall dependencies...'
                sh '''
                    python3 -m pip install --break-system-packages -r requirements.txt \
                    || python3 -m pip install -r requirements.txt \
                    || echo "Tidak ada requirements.txt atau pip, skip..."
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Menjalankan unit test...'
                sh '''
                    if [ -d tests ]; then
                        python3 -m pytest tests/ -v
                    else
                        echo "Folder tests/ tidak ditemukan, skip..."
                    fi
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
                        if [ -f Dockerfile ]; then
                            docker build -t rmdhnaditya08/deploy-app:latest .
                            echo $DOCKER_PASS | docker login -u rmdhnaditya08 --password-stdin
                            docker push rmdhnaditya08/deploy-app:latest
                            docker logout
                        else
                            echo "Dockerfile tidak ditemukan, skip..."
                        fi
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo "Deploy ke environment: ${APP_ENV}..."
                sh '''
                    if docker image inspect rmdhnaditya08/deploy-app:latest > /dev/null 2>&1; then
                        docker stop deploy-app || true
                        docker rm   deploy-app || true
                        docker run -d \
                            --name deploy-app \
                            -p 5000:5000 \
                            rmdhnaditya08/deploy-app:latest
                    else
                        echo "Image belum tersedia, skip deploy..."
                    fi
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
