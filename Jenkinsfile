def image_repo = ''
def image_tag = ''

pipeline {
    agent any

    environment {
        PROJECT_ID = 'bamboo-diode-456912-p9'
        CLUSTER = 'autopilot-cluster-1'
        ZONE = 'asia-south1'
        GCP_KEY = 'C:\\Users\\himan\\Downloads\\devops-lab-ci\\flask-gke-helm\\jenkins-sa-key.json'   
        PYTHON_EXEC = 'C:\\Users\\himan\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        GIT_CREDENTIALS_ID = credentials('Jenkins-Generic')
    }

    stages {
 
        stage('Checkout') {
 
            steps {
 
                checkout scm
 
            }
 
        }

        stage('Authenticate with GCP') {
            steps {
                bat """
                    gcloud auth activate-service-account --key-file="${env.GCP_KEY}"
                    gcloud config set project ${env.PROJECT_ID}
                    gcloud auth configure-docker asia-south1-docker.pkg.dev --quiet
                """
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    image_repo = "asia-south1-docker.pkg.dev/${env.PROJECT_ID}/service-admin/admin"
                    image_tag = "${BUILD_NUMBER}-${env.env_namespace}"
                    def image_full = "${image_repo}:${image_tag}"

                    bat """
                        docker build -t ${image_full} .
                        docker push ${image_full}
                    """
                }
            }
        }

        stage('Deploy to GKE') {
            steps {
                bat """
                    gcloud container clusters get-credentials ${env.CLUSTER} --zone ${env.ZONE} --project ${env.PROJECT_ID}
                """

                configFileProvider([configFile(fileId: 'deploy_to_gke', targetLocation: 'deploy_to_gke.py')]) {
                     script {
                            def pythonCommand = """
                                set CLUSTER=${env.CLUSTER}
                                set ZONE=${env.ZONE}
                                set PROJECT_ID=${env.PROJECT_ID}
                                echo Running Python script...
                                ${env.PYTHON_EXEC} deploy_to_gke.py ${env.env_namespace} ${image_repo} ${image_tag} ${env.github_url}
                            """
                        
                            echo "Executing Python Deployment Script..."
                        
                            def result = bat(script: pythonCommand, returnStdout: true).trim()
                            echo "Deployment Output:\n${result}"
                        }

                }
            }
        }
    }
}
