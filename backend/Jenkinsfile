pipeline {
    agent any

    triggers {
        githubPush()  // ensures Jenkins triggers on GitHub push events
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code checked out successfully."
            }
        }

        stage('Build') {
            steps {
                echo "🚧 Running build process..."
                sh 'echo build commands go here'
            }
        }

        stage('Test') {
            steps {
                echo "🧪 Running tests..."
                sh 'echo test commands go here'
            }
        }
    }

    post {
        success {
            echo "🎉 Build completed successfully."
        }
        failure {
            echo "❌ Build failed."
        }
    }
}

