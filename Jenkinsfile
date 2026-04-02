pipeline {
    agent { label 'garuda-agent' }

    environment {
        // Project IDs matched to your GKE settings
        PROJECT_ID = 'garudaone20'
        REGION = 'us-central1'
        REPO = 'garuda-docker'
        IMAGE_NAME = 'service-admin'
        IMAGE_URI = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}"
        GIT_CREDENTIALS_ID = 'git-token'
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "Checking out service-admin onto node: ${env.NODE_NAME}"
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    echo "Initializing virtual environment and running tests..."
                    sh """
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install -r requirements.txt
                        # Verifying application imports
                        python3 -c "import flask; print('Flask imported successfully')"
                    """
                }
            }
        }

        stage('Build & Push Image') {
            steps {
                script {
                    // Use commit SHA as version tag for traceability
                    def gitSha = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                    def imageFull = "${IMAGE_URI}:${gitSha}"
                    
                    echo "Building and Pushing Docker image: ${imageFull}"
                    
                    sh """
                        # Authenticate Docker to Artifact Registry
                        gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
                        
                        # Build the image from current directory
                        docker build -t ${imageFull} -t ${IMAGE_URI}:latest .
                        
                        # Push to Google Cloud Artifact Registry
                        docker push ${imageFull}
                        docker push ${IMAGE_URI}:latest
                    """
                }
            }
        }
    }

    post {
        success {
            echo "CI Pipeline Successful! Image pushed to: ${IMAGE_URI}"
        }
        failure {
            echo "CI Pipeline failed. Check console output for debugging."
        }
    }
}
