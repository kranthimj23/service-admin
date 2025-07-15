def image_repo = ''
def image_tag = ''

pipeline {
    agent any

    environment {
        PROJECT_ID = 'nice-virtue-463917-m0'
        CLUSTER = 'autopilot-cluster-1'
        ZONE = 'asia-south1'
        
        // Update this path if your key is stored elsewhere
        GCP_KEY = '/var/lib/jenkins/keys/nice-virtue-463917-m0-b7c626c7348c.json'
        
        PYTHON_EXEC = 'python3.11'
        GIT_CREDENTIALS_ID = credentials('jenkins-token')
    }

    stages {
        stage('Checkout with credentials') {
            steps {
                deleteDir()
                script {
                    withCredentials([string(credentialsId: 'jenkins-token', variable: 'GIT_TOKEN')]) {
                        checkout([
                            $class: 'GitSCM',
                            branches: [[name: "*/dev"]],
                            userRemoteConfigs: [[
                                url: "https://${GIT_TOKEN}@github.com/kranthimj23/service-admin.git"
                            ]]
                        ])
                    }
                }
            }
        }
        
        stage('Authenticate with GCP') {
            steps {
                sh """
                    gcloud auth activate-service-account --key-file="${GCP_KEY}"
                    gcloud config set project ${PROJECT_ID}
                    gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet
                    gcloud auth list
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    image_repo = "asia-south1-docker.pkg.dev/${env.PROJECT_ID}/service-admin/admin"
                    image_tag = "${BUILD_NUMBER}-${env.env_namespace ?: 'dev'}" // fallback if env_namespace not set
                    def image_full = "${image_repo}:${image_tag}"

                    sh """
                        echo 'Logging in to Artifact Registry...'
                        gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://asia-south1-docker.pkg.dev

                        echo 'Building Docker image...'
                        docker build -t ${image_full} .

                        echo 'Pushing Docker image...'
                        docker push ${image_full}
                    """
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                sh """
                    gcloud container clusters get-credentials ${CLUSTER} --zone ${ZONE} --project ${PROJECT_ID}
                """

                configFileProvider([configFile(fileId: 'deploy_to_gke', targetLocation: 'deploy_to_gke.py')]) {
                    withCredentials([string(credentialsId: 'jenkins-token', variable: 'GIT_TOKEN')]) {
                        script {
                            def pythonCommand = """
                                export CLUSTER=${CLUSTER}
                                export ZONE=${ZONE}
                                export PROJECT_ID=${PROJECT_ID}
                                echo Running Python script...
                                ${PYTHON_EXEC} deploy_to_gke.py ${env.env_namespace ?: 'dev'} ${image_repo} ${image_tag} ${env.github_url} ${env.microservice}
                            """
    
                            echo "Executing Python Deployment Script..."
    
                            def result = sh(script: pythonCommand, returnStdout: true).trim()
                            echo "Deployment Output:\n${result}"
                        }
                    }
                }
            }
        }
    }
}
