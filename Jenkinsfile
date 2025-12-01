pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        PROJECT_DIR = "/home/ayon/global-math/backend"
        VENV_BIN = "/home/ayon/global-math/backend/venv/bin"
        PM2_APP_NAME = "globalmath"
    }

    stages {

        stage('Prepare Workspace') {
            steps {
                cleanWs()
                dir("${PROJECT_DIR}") {
                    sh 'git fetch origin main && git reset --hard origin/main'
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                echo "📦 Installing dependencies..."
                sh """
                    cd ${PROJECT_DIR}
                    ${VENV_BIN}/pip install -r requirements.txt
                """
            }
        }

        stage('Database Migrations') {
            steps {
                echo "🛠 Applying migrations..."
                sh """
                    cd ${PROJECT_DIR}
                    ${VENV_BIN}/python manage.py migrate
                """
            }
        }

        stage('Collect Static Files') {
            steps {
                echo "🎨 Collecting static files..."
                sh """
                    cd ${PROJECT_DIR}
                    ${VENV_BIN}/python manage.py collectstatic --noinput
                """
            }
        }

        stage('Restart Application (PM2 + Uvicorn)') {
            steps {
                echo "🔁 Restarting PM2 Application..."
                sh """
                    pm2 restart ${PM2_APP_NAME} || \
                    pm2 start "${VENV_BIN}/uvicorn core.asgi:application --host 0.0.0.0 --port 8000 --workers 4" \
                    --name ${PM2_APP_NAME}
                """
            }
        }
    }

    post {
        success {
            echo "🚀 Deployment Successful!"
        }
        failure {
            echo "💀 Deployment Failed — Fix Immediately."
        }
    }
}

