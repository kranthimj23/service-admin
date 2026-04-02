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
        stage('Prepare Agent Tools') {
            steps {
                script {
                    echo "Checking and installing missing tools (Docker, venv)..."
                    sh """
                        # Install Python venv
                        sudo apt-get update && sudo apt-get install -y python3.11-venv
                        
                        # Install Docker if missing
                        if ! command -v docker &> /dev/null; then
                            echo "Docker not found, installing..."
                            sudo apt-get install -y docker.io
                            # Attempting to add current user to docker group (may require logout/re-login to take effect)
                            sudo usermod -aG docker \$USER || true
                        fi
                    """
                }
            }
        }

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
                    
                    // Using specifically the 'gcp-sa-key' you mentioned earlier
                    withCredentials([file(credentialsId: 'gcp-sa', variable: 'GCP_KEY_FILE')]) {
                        echo "Authenticating and Pushing Docker image: ${imageFull}"
                        
                        sh """
                            # Activate service account
                            gcloud auth activate-service-account --key-file=\$GCP_KEY_FILE
                            gcloud config set project ${env.PROJECT_ID}
                            
                            # Log in to Artifact Registry
                            gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://${env.REGION}-docker.pkg.dev
                            
                            # Build the image
                            docker build -t ${imageFull} -t ${IMAGE_URI}:latest .
                            
                            # Push to Google Cloud Artifact Registry
                            docker push ${imageFull}
                            docker push ${IMAGE_URI}:latest
                        """
                    }
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
