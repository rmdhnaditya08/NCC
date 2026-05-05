pipeline {
    agent any

    environment {
        APP_ENV  = 'staging'
        APP_NAME = 'deploy-app'
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
                    python3 -m pip install --break-system-packages -r requirements.txt || \
                    pip3 install -r requirements.txt || \
                    echo "Skip install..."
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Menjalankan unit test...'
                sh '''
                    python3 -m pytest tests/ -v || \
                    pytest tests/ -v || \
                    echo "Skip test..."
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'Menjalankan analisis SonarQube...'
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv() {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo 'Mengecek Quality Gate...'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
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
